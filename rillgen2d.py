import branca
import os
import subprocess
import shutil
import sys
import tarfile
import time
import tkinter as tk
import folium
import matplotlib.pyplot as plt
import osgeo
import PIL
import rasterio
import requests
import webbrowser

from ctypes import CDLL
from datetime import datetime
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg)
from matplotlib.figure import Figure
from osgeo import gdal, osr
from pathlib import Path
from PIL import ImageTk
from PyQt5 import QtWidgets, QtWebEngineWidgets, QtCore
from PyQt5.QtWidgets import QApplication, QMessageBox, QMainWindow
from rasterio.plot import show
from socket import *
from subprocess import Popen, PIPE, STDOUT
from threading import Thread
from tkinter import *
from tkinter import messagebox
from tkinter import ttk
from tkinter.filedialog import askopenfilename, askdirectory
from wand.image import Image as im

"""This is the main rillgen2d file which handles the gui and communicates with console.py
and rillgen.c in order to perform the rillgen calculations"""

class Application(tk.Frame):
    def __init__(self, parent):
        """Initializing the tkinter application and its tabs.
        The PyQt5 Application must go where it can be initialized
        only once in order to avoid bugs; otherwise the garbage
        collector does not handle it correctly."""
        tk.Frame.__init__(self, parent)
        self.imagefile = None # This is the image file that will be used
        self.filename = None  #this is the name of the input file the user chooses
        self.ax = None # tkinter widget for the canvas for the first figure, this is needed in order to preview the
        # image in the canvas rather than in an external widget
        self.geo_ext = None  # used to get corner coordinates for the projection
        self.app = None  # This is the associated PyQt application that handles the map in View Output
        self.dimensions = None  # These are the dimensions of the input file that the user chooses
        self.socket = None  # socket for the connection between rillgen2d.py and console.py; host socket
        self.client_socket = None # socket for the connection between rillgen2d.py and console.py; client socket
        self.starterimg = None  # This is the image to be displayed in the input_dem tab
        self.popup = None  # This is the popup that comes up during the hydrologic correction step 
        self.popupLabel = None
        self.dynamic_mode_popup = None
        self.can_redraw = None  # Used to redraw the canvas in the view_output tab
        self.rillgen = None  # Used to import the rillgen.c code
        self.style = ttk.Style(root)
        self.style.layout('text.Horizontal.TProgressbar',
                    [('Horizontal.Progressbar.trough',
                    {'children': [('Horizontal.Progressbar.pbar',
                                    {'side': 'left', 'sticky': 'ns'})],
                        'sticky': 'nswe'}),
                    ('Horizontal.Progressbar.label', {'sticky': ''})])
        self.style.configure('text.Horizontal.TProgressbar', text='0 %', foreground='black', background='green')
        self.style.configure("TButton",font=('Helvetica', 18))
        self.style.configure('BLUE.TButton', font = ('Helvetica', 18,'underline'), foreground = 'blue')
        self.style.configure('RED.TButton', font = ('Helvetica', 18,'underline'), foreground = 'red')
        self.tabControl = ttk.Notebook(self)
        self.tab1 = ttk.Frame(self.tabControl)
        self.tab2 = ttk.Frame(self.tabControl)
        self.tab3 = ttk.Frame(self.tabControl)
        self.img1 = None 
        self.fig1 = Figure(figsize=(5, 5), dpi=100) # figure that will preview the image via rasterio
        self.canvas3imlbl = None
        self.t = Thread(target=self.network_function)
        self.t.daemon = True
        self.t.start()
        self.t1 = None
        """We only want the first tab for now; the others appear in order after the 
        processes carried out in a previous tab are completed"""
        self.tabControl.add(self.tab1, text="Input DEM") 
        self.tabControl.pack(expand=1, fill="both")
        self.first_time_populating_parameters_tab = True
        self.first_time_populating_view_output_tab = True
        self.populate_input_dem_tab()


    def network_function(self):
        """Handles the connection between rillgen2d.py and console.py by making a
        host/client structure with rillgen2d.py as the host and console.py as the
        client"""
        Popen([sys.executable, "console.py"], universal_newlines=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT)
        port = 5000  # initiate port no above 1024
        self.socket = socket()  # get instance
        self.socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1) # allows for a port to be used
        # even if it was previously being used
        # look closely. The bind() function takes tuple as argument
        self.socket.bind(('', port))  # bind host address and port together

        # configure how many client the server can listen simultaneously
        self.socket.listen(3)
        self.client_socket, address = self.socket.accept()  # accept new connection
        self.client_socket.send(("Connection from: " + str(address) + "\n\n").encode('utf-8'))


    def populate_input_dem_tab(self):
        """This populates the first tab in the application with tkinter widgets.
        The first tab allows a user to select an geotiff image from either their 
        local filesystem or from a url."""
        
        self.github_button = ttk.Button(self.tab1,text="README",command=self.open_github, style='BLUE.TButton')
        self.github_button.grid(row=0,column=0)

        self.button1 = ttk.Button(self.tab1, text="upload local file (.tif)", command=self.get_image_locally)
        self.button1.grid(row=1, column=0)

        self.entry1 = Text(self.tab1, width=60,height=5)
        self.entry1.insert(1.0,"paste or enter URL (must be .tif or .tar.gz)")
        self.entry1.first_time_clicked = True

        def delete_default_text(event):
            if self.entry1.first_time_clicked == True:
                self.entry1.delete(1.0,END)
                self.entry1.first_time_clicked = False

        self.entry1.bind("<Button-1>", delete_default_text)
        self.entry1.grid(row=2, column=0)

        self.button2 = ttk.Button(self.tab1, text="Download from URL", command=self.get_image_from_url)
        self.button2.grid(row=3, column=0)

        self.img1 = Label(self.tab1)
        self.canvas1 = FigureCanvasTkAgg(self.fig1, master=self.img1)
        self.canvas1.get_tk_widget().place_forget()
        self.canvas1.draw()
        self.canvas1.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1, padx=0, pady=0)
        self.canvas1._tkcanvas.pack(side=TOP, fill=BOTH, expand=1, padx=0, pady=0)

        self.img1.grid(row=0, column=2, rowspan=4, sticky=N+S+E+W)
        self.canvas1.get_tk_widget().configure(highlightbackground="red")

        style = ttk.Style()
        style.configure('W.TButton', font="Helvetica", foreground='red')

        self.save_image = ttk.Button(self.tab1, text="Next: Parameters", command=self.saveimageastxt,style='RED.TButton')
        self.save_image.grid(row=4, column=1)
        self.tab1.columnconfigure(0, weight=1)
        self.tab1.columnconfigure(1, weight=1)
        self.tab1.columnconfigure(2, weight=1)
        self.tab1.rowconfigure(0, weight=2)
        self.tab1.rowconfigure(1, weight=4)
        self.tab1.rowconfigure(2, weight=1)
        self.tab1.rowconfigure(3, weight=1)

    def open_github(self):
        webbrowser.open("https://github.com/jdpellet/rillgen2d",new=1,autoraise=True)

    def get_image_locally(self):
        """Given a geotiff image, either in .tar format or directly, extract the image and display
        it on the canvas"""
        try:
            self.imagefile = Path(askopenfilename(initialdir=Path.cwd().parent, filetypes=[('Image Files', ['.tif','.gz','.tar'])]))
            if self.imagefile.suffix == '.tar' or self.imagefile.suffix == '.gz':
                path = Path.cwd()
                if path.as_posix().endswith('tmp'):
                    path = path.parent
                self.imagefile = self.extract_geotiff_from_tarfile(self.imagefile,path)
        except:
            messagebox.showerror(title="ERROR", message="Invalid file type. Please select an image file")
        else:
            self.preview_geotiff(mode=1)

    
    def get_image_from_url(self):
        """Given the url of an image when a raster is generated or located online,
        extract the geotiff image from the url and display it on the canvas """
        try: 
            entry1 = str(self.entry1.get("1.0",'end-1c'))
            r = requests.get(entry1,allow_redirects=True)
            path = Path.cwd()
            if path.as_posix().endswith('tmp'):
                path = path.parent
            downloaded = os.path.basename(entry1)
            img = downloaded
            open((path / downloaded),'wb').write(r.content)
            if downloaded.endswith(".gz"):
                tarpath = path / downloaded
                self.imagefile = self.extract_geotiff_from_tarfile(tarpath,path)
                os.remove(path / downloaded)
            else:
                self.imagefile = (path / img)
            
        except Exception:
            messagebox.showerror(title="ERROR", message="Invalid url. Please use the url for an image")
        else:
            self.preview_geotiff(mode=2)

    def extract_geotiff_from_tarfile(self,tarpath,outputpath):
        img = tarpath
        tar = tarfile.open(tarpath)
        for filename in tar.getnames():
            if filename.endswith('.tif'):
                tar.extract(filename, path=str(outputpath))
                img = filename
                break
        desiredfile = (outputpath / img)
        return desiredfile


    def preview_geotiff(self, mode):
        """Display the geotiff on the canvas of the first tab"""
        try:
            self.starterimg = rasterio.open(self.imagefile)
            if self.imagefile.suffix == '.tif':
                if self.ax:
                    self.ax.clear()
                else:
                    self.ax = self.fig1.add_subplot(111)
                self.ax.set(title="",xticks=[], yticks=[])
                self.ax.spines["top"].set_visible(False)
                self.ax.spines["right"].set_visible(False)
                self.ax.spines["left"].set_visible(False)
                self.ax.spines["bottom"].set_visible(False)
                self.fig1.subplots_adjust(bottom=0, right=1, top=1, left=0, wspace=0, hspace=0)
                with self.starterimg as src_plot:
                    show(src_plot, ax=self.ax)
                plt.close()
                self.canvas1.draw()
            else:
                messagebox.showerror(title="ERROR", message="Invalid File Format. Supported files must be in TIFF format")
        except Exception as e:
                messagebox.showerror(title="ERROR", message="Exception: " + str(e))


    def saveimageastxt(self):
        """Prepares the geotiff file for the rillgen2D code by getting its dimensions (for the input.txt file) and converting it to
        .txt format"""
        if self.imagefile == None or self.imagefile == "":
            messagebox.showerror(title="NO FILENAME CHOSEN", message="Please choose a valid file")
        else:
            if Path.cwd().name == "tmp":
                os.chdir("..")
            """This portion compiles the rillgen2d.c file in order to import it as a module"""
            if self.rillgen == None:
                cmd = "gcc -Wall -shared -fPIC rillgen2d.c -o rillgen.so" # compile the c file so that it will be useable later
                self.client_socket.send(subprocess.check_output(cmd, shell=True) + ('\n').encode('utf-8'))
            path = Path.cwd() / "tmp"
            if path.exists():
                shutil.rmtree(path.as_posix())
            Path.mkdir(path)
            self.filename = str(path / self.imagefile.name)
            shutil.copyfile(str(self.imagefile), self.filename)
            if Path(str(self.imagefile) + ".aux.xml").exists():
                shutil.copyfile(str(self.imagefile) + ".aux.xml", str(path / self.imagefile.stem) + ".aux.xml")
            shutil.copyfile("input.txt", path / "input.txt")

            for fname in Path.cwd().iterdir():
                if fname.suffix == ".tif":
                    Path(fname).unlink()
            os.chdir(str(path))
            
            # Open existing dataset
            self.client_socket.send(("Filename is: " + Path(self.filename).name + "\n\n").encode('utf-8'))
            self.client_socket.send(("Saving the image as .txt...\n\n").encode('utf-8'))
            self.src_ds = gdal.Open(self.filename)
            band = self.src_ds.GetRasterBand(1)
            arr = band.ReadAsArray()
            self.dimensions = [arr.shape[0], arr.shape[1]]
            self.t1 = Thread(target=self.populate_parameters_tab)
            self.t1.start()  # Populates the second tab since now the user has chosen a file
            self.convert_geotiff_to_txt(Path(self.filename).stem)

            if self.first_time_populating_parameters_tab == True:
                self.tabControl.add(self.tab2, text="Parameters")
                self.tabControl.pack(expand=1, fill="both")
            self.client_socket.send(("Image saved\n\n").encode('utf-8'))


    def populate_parameters_tab(self):
        """Populate the second tab in the application with tkinter widgets. This tab holds editable parameters
        that will be used to run the rillgen2dwitherode.c script. lattice_size_x and lattice_size_y are read in from the
        geometry of the geotiff file"""

        if self.first_time_populating_parameters_tab == True:
            self.canvas2 = tk.Canvas(self.tab2, borderwidth=0)
            self.frame2 = tk.Frame(self.canvas2)
            self.hsb = tk.Scrollbar(self.tab2, orient="horizontal", command=self.canvas2.xview)
            self.vsb = tk.Scrollbar(self.tab2, orient="vertical", command=self.canvas2.yview)
            self.canvas2.configure(xscrollcommand=self.hsb.set, yscrollcommand=self.vsb.set)

            self.hsb.pack(side="bottom", fill="x")
            self.vsb.pack(side="right", fill="y")
            
            self.parameters_window = self.canvas2.create_window((0,0), window=self.frame2, anchor="nw")
        f = open('input.txt', 'r')
        rowNumber = 3

        # LABELS
        Label(self.frame2, text='RillGen2D', font='Helvetica 18 bold italic underline').grid(row=1, column=1, sticky=(N), pady=20)
        Label(self.frame2, text='Inputs', font='Helvetica 18 bold underline').grid(row=2, column=0, sticky=(N,E,S,W), pady=20)
        Label(self.frame2, text='Input Descriptions', font='Helvetica 18 bold underline').grid(row=2, column=2, sticky=(N,E,S,W), pady=50)

        # Flag for equation variable
        Label(self.frame2, text='Equation:', font='Helvetica 18 bold').grid(row=rowNumber, column=0, pady=20)
        Label(self.frame2, text='Should be 0 if the user wishes to implement the rock armor shear strength equation of Haws and Erickson (2020), 1 if the user wishes to implement the equation of Pelletier et al. (2021).', font='Helvetica 18', justify=CENTER, wraplength=750).grid(row=rowNumber, column=2, pady=20)
        
        self.flagForEquationVar = IntVar(value=int(f.readline()))
        Checkbutton(self.frame2, variable=self.flagForEquationVar, width=5).grid(row=rowNumber, column=1, pady=20)
        rowNumber += 1

        Frame(self.frame2, width=self.frame2.winfo_screenwidth(), height=5, background="PeachPuff").grid(row=rowNumber, column=0, columnspan=3, padx=0)
        rowNumber += 1

        # Flag for dynamic node variable
        Label(self.frame2, text='Enable Dynamic Mode', font='Helvetica 18 bold').grid(row=rowNumber, column=0, pady=20)
        Label(self.frame2, text='Should be 1 if the user wants to implement either the dynamic mode, in which case the file "dynamicinput.txt" must be provided in the same directory as the executable, and/or spatially variable rainfall. If this flag is set to zero then the model is run in "peak mode" with spatially uniform rainfall only.', font='Helvetica 18', justify=CENTER, wraplength=750).grid(row=rowNumber, column=2, pady=20)
        
        self.flagforDynamicModeVar = IntVar(value=int(f.readline()))
        Checkbutton(self.frame2, variable=self.flagforDynamicModeVar, width=5).grid(row=rowNumber, column=1, pady=20)
        rowNumber += 1

        Frame(self.frame2, width=self.frame2.winfo_screenwidth(), height=5, background="PeachPuff").grid(row=rowNumber, column=0, columnspan=3, padx=0)
        rowNumber += 1

        # Flag for mask variable
        Label(self.frame2, text='Mask:', font='Helvetica 18 bold').grid(row=rowNumber, column=0, pady=20)
        Label(self.frame2, text='Should be 1 if the user provides a raster (mask.tif) that restricts the model to certain portions of the input DEM (mask = 1 means run the model, 0 means ignore these areas).', font='Helvetica 18', justify=CENTER, wraplength=750).grid(row=rowNumber, column=2, pady=20)
        
        self.flagForMaskVar = IntVar(value=int(f.readline()))
        Checkbutton(self.frame2, variable=self.flagForMaskVar, width=5, command=self.getMask).grid(row=rowNumber, column=1, pady=20)
        rowNumber += 1

        Frame(self.frame2, width=self.frame2.winfo_screenwidth(), height=5, background="PeachPuff").grid(row=rowNumber, column=0, columnspan=3, padx=0)
        rowNumber += 1

        # flagForTaucSoilAndVeg variable
        Label(self.frame2, text='Tau C soil & veg:', font='Helvetica 18 bold').grid(row=rowNumber, column=0, pady=20)
        Label(self.frame2, text='Should be 1 if the user provides a raster (taucsoilandveg.txt) that maps the shear strength of soil and veg, 0 means a fixed value equal to taucsoilandvegfixed will be used.', font='Helvetica 18',justify=CENTER, wraplength=750).grid(row=rowNumber, column=2, pady=20)
        self.flagForTaucSoilAndVegVar = IntVar(value=int(f.readline()))
        flagForTaucSoilAndVegInput = Checkbutton(self.frame2, variable=self.flagForTaucSoilAndVegVar, width=5, pady=20)
        flagForTaucSoilAndVegInput.grid(row=rowNumber, column=1, pady=20)
        rowNumber += 1

        Frame(self.frame2, width=self.frame2.winfo_screenwidth(), height=5, background="PeachPuff").grid(row=rowNumber, column=0, columnspan=3)
        rowNumber += 1

        # Flag for d50 variable
        Label(self.frame2, text='d50', font='Helvetica 18 bold').grid(row=rowNumber, column=0, pady=20)
        Label(self.frame2, text='Should be 1 if the user provides a raster (d50.txt) that maps the median rock diameter, 0 means a fixed value equal to d50fixed will be used.', font='Helvetica 18',justify=CENTER, wraplength=750).grid(row=rowNumber, column=2, pady=20)
        self.flagFord50Var = IntVar(value=int(f.readline()))
        flagFord50Input = Checkbutton(self.frame2, variable=self.flagFord50Var, width=5, pady=20)
        flagFord50Input.grid(row=rowNumber, column=1)
        rowNumber += 1

        Frame(self.frame2, width=self.frame2.winfo_screenwidth(), height=5, background="PeachPuff").grid(row=rowNumber, column=0, columnspan=3)
        rowNumber += 1

        # Flag for rockcover
        Label(self.frame2, text='Rock Cover', font='Helvetica 18 bold').grid(row=rowNumber, column=0, pady=20)
        Label(self.frame2, text='Should be 1 if the user provides a raster (rockcover.txt) that maps the rock cover fraction, 0 means a fixed value equal to rockcoverfixed will be used.', font='Helvetica 18', justify=CENTER, wraplength=750).grid(row=rowNumber, column=2, pady=20)
        self.flagForRockCoverVar = IntVar(value=int(f.readline()))
        flagForRockCoverInput = Checkbutton(self.frame2, variable=self.flagForRockCoverVar, width=5, pady=20)
        flagForRockCoverInput.grid(row=rowNumber, column=1)
        rowNumber += 1

        Frame(self.frame2, width=self.frame2.winfo_screenwidth(), height=5, background="PeachPuff").grid(row=rowNumber, column=0, columnspan=3)
        rowNumber += 1

        # fillIncrement variable
        Label(self.frame2, text='fill Increment:', font='Helvetica 18 bold').grid(row=rowNumber, column=0, pady=20)
        Label(self.frame2, text='This value (in meters) is used to fill in pits and flats for hydrologic correction. 0.01 is a reasonable default value for most lidar applications.', font='Helvetica 18',justify=CENTER, wraplength=750).grid(row=rowNumber, column=2, pady=20)
        fillIncrementVar = StringVar(root, value=str(f.readline()))
        self.fillIncrementInput = Entry(self.frame2, textvariable=fillIncrementVar, width=5)
        self.fillIncrementInput.grid(row=rowNumber, column=1, pady=20)
        rowNumber += 1

        Frame(self.frame2, width=self.frame2.winfo_screenwidth(), height=5, background="PeachPuff").grid(row=rowNumber, column=0, columnspan=3)
        rowNumber += 1

        # minslope variable
        Label(self.frame2, text='min Slope:', font='Helvetica 18 bold').grid(row=rowNumber, column=0, pady=20)
        Label(self.frame2, text='This value (unitless) is used to halt runoff from areas below a threshold slope steepness. Setting this value larger than 0 is useful for eliminating runoff from portions of the landscape that the user expects are too flat to produce significant runoff.', font='Helvetica 18', justify=CENTER, wraplength=750).grid(row=rowNumber, column=2, pady=20)
        minslopeVar = StringVar(value=str(f.readline()))
        self.minslopeInput = Entry(self.frame2, textvariable=minslopeVar, width=5)
        self.minslopeInput.grid(row=rowNumber, column=1, pady=20)
        rowNumber += 1

        Frame(self.frame2, width=self.frame2.winfo_screenwidth(), height=5, background="PeachPuff").grid(row=rowNumber, column=0, columnspan=3)
        rowNumber += 1

        # Expansion variable
        Label(self.frame2, text='expansion:', font='Helvetica 18 bold').grid(row=rowNumber, column=0, pady=20)
        Label(self.frame2, text='This value (in number of pixels) is used to expand the zones where rills are predicted in the output raster. This is useful for making the areas where rilling is predicted easier to see in the model output.', font='Helvetica 18',justify=CENTER, wraplength=750).grid(row=rowNumber, column=2, pady=20)
        expansionVar = StringVar(value=str(f.readline()))
        self.expansionInput = Entry(self.frame2, textvariable=expansionVar, width=5)
        self.expansionInput.grid(row=rowNumber, column=1, pady=20)
        rowNumber += 1

        Frame(self.frame2, width=self.frame2.winfo_screenwidth(), height=5, background="PeachPuff").grid(row=rowNumber, column=0, columnspan=3)
        rowNumber += 1

        # yellowThreshold variable
        Label(self.frame2, text='yellow Threshold:', font='Helvetica 18 bold').grid(row=rowNumber, column=0, pady=20)
        Label(self.frame2, text='This is a threshold value of f used to indicate an area that is close to but less than the threshold for generating rills. The model will visualize any location with a f value between this value and 1 as potentially prone to rill generation (any area with a f value larger than 1 is considered prone to rill generation and is colored red).', font='Helvetica 18',justify=CENTER, wraplength=750).grid(row=rowNumber, column=2, pady=20)
        yellowThresholdVar = StringVar(value=str(f.readline()))
        self.yellowThresholdInput = Entry(self.frame2, textvariable=yellowThresholdVar, width=5)
        self.yellowThresholdInput.grid(row=rowNumber, column=1, pady=20)
        rowNumber += 1

        Frame(self.frame2, width=self.frame2.winfo_screenwidth(), height=5, background="PeachPuff").grid(row=rowNumber, column=0, columnspan=3)
        rowNumber += 1

        # Lattice_size_x variable
        Label(self.frame2, text='lattice_size_x:', font='Helvetica 18 bold').grid(row=rowNumber, column=0, pady=20)
        Label(self.frame2, text='The number of pixels along the east-west direction in the DEM.', font='Helvetica 18',justify=CENTER, wraplength=750).grid(row=rowNumber, column=2, pady=20)
        lattice_size_xVar = StringVar(value=self.dimensions[1])
        self.lattice_size_xInput = Entry(self.frame2, textvariable=lattice_size_xVar, width=5)
        self.lattice_size_xInput.grid(row=rowNumber, column=1, pady=20)
        self.lattice_size_xInput.config(state=DISABLED)
        rowNumber += 1

        Frame(self.frame2, width=self.frame2.winfo_screenwidth(), height=5, background="PeachPuff").grid(row=rowNumber, column=0, columnspan=3)
        rowNumber += 1

        # Lattice_size_y variable
        Label(self.frame2, text='lattice_size_y:', font='Helvetica 18 bold').grid(row=rowNumber, column=0, pady=20)
        Label(self.frame2, text='The number of pixels along the east-west direction in the DEM.', font='Helvetica 18', justify=CENTER, wraplength=750).grid(row=rowNumber, column=2, pady=20)
        lattice_size_yVar = StringVar(value=self.dimensions[0])
        self.lattice_size_yInput = Entry(self.frame2, textvariable=lattice_size_yVar, width=5)
        self.lattice_size_yInput.grid(row=rowNumber, column=1, pady=20)
        self.lattice_size_yInput.config(state=DISABLED)
        rowNumber += 1

        Frame(self.frame2, width=self.frame2.winfo_screenwidth(), height=5, background="PeachPuff").grid(row=rowNumber, column=0, columnspan=3)
        rowNumber += 1

        f.readline() # We do not want to read in the previous lattice_x and lattice_y
        f.readline() # Since they came from another geotiff file
  
        # Deltax variable
        Label(self.frame2, text='deltax:', font='Helvetica 18 bold').grid(row=rowNumber, column=0, pady=20)
        Label(self.frame2, text='The resolution (in meters/pixel) of the DEM and additional optional raster inputs.', font='Helvetica 18', justify=CENTER, wraplength=750).grid(row=rowNumber, column=2, pady=20)
        deltaxVar = StringVar(value=str(f.readline()))
        self.deltaxInput = Entry(self.frame2, textvariable=deltaxVar, width=5)
        self.deltaxInput.grid(row=rowNumber, column=1, pady=20)
        rowNumber += 1

        Frame(self.frame2, width=self.frame2.winfo_screenwidth(), height=5, background="PeachPuff").grid(row=rowNumber, column=0, columnspan=3)
        rowNumber += 1

        # Nodata variable
        Label(self.frame2, text='nodata:', font='Helvetica 18 bold').grid(row=rowNumber, column=0, pady=20)
        Label(self.frame2, text='Any topo less than or equal to this nodata value will be masked out.', font='Helvetica 18', justify=CENTER, wraplength=750).grid(row=rowNumber, column=2, pady=20)
        nodataVar = StringVar(value=str(f.readline()))
        self.nodataInput = Entry(self.frame2, textvariable=nodataVar, width=5)
        self.nodataInput.grid(row=rowNumber, column=1, pady=20)
        rowNumber += 1

        Frame(self.frame2, width=self.frame2.winfo_screenwidth(), height=5, background="PeachPuff").grid(row=rowNumber, column=0, columnspan=3)
        rowNumber += 1

        # Smoothinglength variable
        Label(self.frame2, text='smoothinglength:', font='Helvetica 18 bold').grid(row=rowNumber, column=0, pady=20)
        Label(self.frame2, text='The length scale (in pixels) for smoothing of the slope map. Set to 1 if no smoothing is desired.', font='Helvetica 18', justify=CENTER, wraplength=750).grid(row=rowNumber, column=2, pady=20)
        smoothinglengthVar = StringVar(value=str(f.readline()))
        self.smoothinglengthInput = Entry(self.frame2, textvariable=smoothinglengthVar, width=5)
        self.smoothinglengthInput.grid(row=rowNumber, column=1, pady=20)
        rowNumber += 1

        Frame(self.frame2, width=self.frame2.winfo_screenwidth(), height=5, background="PeachPuff").grid(row=rowNumber, column=0, columnspan=3)
        rowNumber += 1

        # Rain fixed variable
        Label(self.frame2, text='rain fixed:', font='Helvetica 18 bold').grid(row=rowNumber, column=0, pady=20)
        Label(self.frame2, text='Peak rainfall intensity (in mm/hr). This value is ignored if flagforrain=1.', font='Helvetica 18', justify=CENTER, wraplength=750).grid(row=rowNumber, column=2, pady=20)
        rainVar = StringVar(value=str(f.readline()))
        self.rainInput = Entry(self.frame2, textvariable=rainVar, width=5)
        self.rainInput.grid(row=rowNumber, column=1, pady=20)
        rowNumber += 1

        Frame(self.frame2, width=self.frame2.winfo_screenwidth(), height=5, background="PeachPuff").grid(row=rowNumber, column=0, columnspan=3)
        rowNumber += 1

        # tauc soil and vege fixed variable
        Label(self.frame2, text='tauc soil and vege fixed:', font='Helvetica 18 bold').grid(row=rowNumber, column=0, pady=20)
        Label(self.frame2, text='Threshold shear stress for soil and vegetation. This value is ignored if flagfortaucsoilandveg=1.', font='Helvetica 18',justify=CENTER, wraplength=750).grid(row=rowNumber, column=2, pady=20)
        taucSoilAndVegeVar = StringVar(value=str(f.readline()))
        self.taucSoilAndVegeInput = Entry(self.frame2, textvariable=taucSoilAndVegeVar, width=5)
        self.taucSoilAndVegeInput.grid(row=rowNumber, column=1, pady=20)
        rowNumber += 1

        Frame(self.frame2, width=self.frame2.winfo_screenwidth(), height=5, background="PeachPuff").grid(row=rowNumber, column=0, columnspan=3)
        rowNumber += 1

        # d50 fixed variable
        Label(self.frame2, text='d50 fixed:', font='Helvetica 18 bold').grid(row=rowNumber, column=0, pady=20)
        Label(self.frame2, text='Median rock armor diameter (in mm). This value is ignored if flagford50=1.', font='Helvetica 18',justify=CENTER, wraplength=750).grid(row=rowNumber, column=2, pady=20)
        d50Var = StringVar(value=str(f.readline()))
        self.d50Input = Entry(self.frame2, textvariable=d50Var, width=5)
        self.d50Input.grid(row=rowNumber, column=1, pady=20)
        rowNumber += 1

        Frame(self.frame2, width=self.frame2.winfo_screenwidth(), height=5, background="PeachPuff").grid(row=rowNumber, column=0, columnspan=3)
        rowNumber += 1

        # Rockcover fixed variable
        Label(self.frame2, text='rockcover:', font='Helvetica 18 bold').grid(row=rowNumber, column=0, pady=20)
        Label(self.frame2, text='This value indicates the fraction of area covered by rock armor. Will be 1 for continuous rock armors, less than one for partial rock cover. This value is ignored if flagforrockcover=1.', font='Helvetica 18',justify=CENTER, wraplength=750).grid(row=rowNumber, column=2, pady=20)
        rockcoverVar = StringVar(value=str(f.readline()))
        self.rockcoverInput = Entry(self.frame2, textvariable=rockcoverVar, width=5)
        self.rockcoverInput.grid(row=rowNumber, column=1, pady=20)
        rowNumber += 1

        Frame(self.frame2, width=self.frame2.winfo_screenwidth(), height=5, background="PeachPuff").grid(row=rowNumber, column=0, columnspan=3)
        rowNumber += 1

        # tanAngleOfInternalFriction fixed variable
        Label(self.frame2, text='tanAngleOfInternalFriction:', font='Helvetica 18 bold').grid(row=rowNumber, column=0, pady=20)
        Label(self.frame2, text='Tangent of the angle of internal friction. Values will typically be in the range of 0.5-0.8.  ', font='Helvetica 18',justify=CENTER, wraplength=750).grid(row=rowNumber, column=2, pady=20)
        tanAngleOfInternalFrictionVar = StringVar(value=str(f.readline()))
        self.tanAngleOfInternalFrictionInput = Entry(self.frame2, textvariable=tanAngleOfInternalFrictionVar, width=5)
        self.tanAngleOfInternalFrictionInput.grid(row=rowNumber, column=1, pady=20)
        rowNumber += 1

        Frame(self.frame2, width=self.frame2.winfo_screenwidth(), height=5, background="PeachPuff").grid(row=rowNumber, column=0, columnspan=3)
        rowNumber += 1

        # b variable
        Label(self.frame2, text='b:', font='Helvetica 18 bold').grid(row=rowNumber, column=0, pady=20)
        Label(self.frame2, text='This value is the coefficient in the model component that predicts the relationship between runoff and contributing area.', font='Helvetica 18',justify=CENTER, wraplength=750).grid(row=rowNumber, column=2, pady=20)
        bVar = StringVar(value=str(f.readline()))
        self.bInput = Entry(self.frame2, textvariable=bVar, width=5)
        self.bInput.grid(row=rowNumber, column=1, pady=20)
        rowNumber += 1

        Frame(self.frame2, width=self.frame2.winfo_screenwidth(), height=5, background="PeachPuff").grid(row=rowNumber, column=0, columnspan=3)
        rowNumber += 1

        # c variable
        Label(self.frame2, text='c:', font='Helvetica 18 bold').grid(row=rowNumber, column=0, pady=20)
        Label(self.frame2, text='This value is the exponent in the model component that predicts the relationship between runoff and contributing area.', font='Helvetica 18', justify=CENTER, wraplength=750).grid(row=rowNumber, column=2, pady=20)
        cVar = StringVar(value=str(f.readline()))
        self.cInput = Entry(self.frame2, textvariable=cVar, width=5)
        self.cInput.grid(row=rowNumber, column=1, pady=20)
        rowNumber += 1

        Frame(self.frame2, width=self.frame2.winfo_screenwidth(), height=5, background="PeachPuff").grid(row=rowNumber, column=0, columnspan=3)
        rowNumber += 1

        # rillWidth variable
        Label(self.frame2, text='rillWidth:', font='Helvetica 18 bold').grid(row=rowNumber, column=0, pady=20)
        Label(self.frame2, text='The width of rills (in m) as they begin to form. This value is used to localize water flow to a width less than the width of a pixel. For example, if deltax = 1 m and rillwidth = 20 cm then the flow entering each pixel is assumed, for the purposes of rill development, to be localized in a width equal to one fifth of the pixel width.', font='Helvetica 18', justify=CENTER, wraplength=750).grid(row=rowNumber, column=2, pady=20)
        rillWidthVar = StringVar(value=str(f.readline()))
        self.rillWidthInput = Entry(self.frame2, textvariable=rillWidthVar, width=5)
        self.rillWidthInput.grid(row=rowNumber, column=1, pady=20)
        rowNumber += 1

        Frame(self.frame2, width=self.frame2.winfo_screenwidth(), height=5, background="PeachPuff").grid(row=rowNumber, column=0, columnspan=3)
        rowNumber += 1
        self.parameterButton = ttk.Button(self.frame2, text='Generate Parameters', command=self.generate_parameters)
        self.parameterButton.grid(row=rowNumber, column=0)
        self.goButton = ttk.Button(self.frame2, text='Run Model', command=self.generate_input_txt_file,style='RED.TButton')
        self.goButton.grid(row=rowNumber, column=2)
        rowNumber += 1

        Label(self.frame2, text='NOTE: The hydrologic correction step can take a long time if there are lots of depressions in the input DEM and/or if the'
        + ' landscape is very steep. RILLGEN2D can be sped up by increasing the value of fillIncrement or by performing the hydrologic correction step in a'
        + ' different program (e.g., ArcGIS or TauDEM) prior to input into RILLGEN2D.', justify=CENTER, wraplength=750, font='Helvetica 20 bold').grid(row=rowNumber, column=0, sticky=(N,E,S,W), pady=30, columnspan=3)

        if self.first_time_populating_parameters_tab == True:
            w = 0
            h = 0
            for child in self.frame2.winfo_children():
                w += child.winfo_reqwidth()
                h += child.winfo_reqheight()
            self.frame2.bind("<Configure>", self.onFrameConfigure)
            self.frame2.bind_all("<MouseWheel>", self.on_mousewheel)
            self.canvas2.itemconfig(self.parameters_window, height = h)
            self.canvas2.pack(side="left", fill="both", expand=True)
        
        self.first_time_populating_parameters_tab = False
        f.close()
        # The width of rills (in m) as they begin to form. This value is used to localize water flow to a width less than the width of a pixel. 
        # For example, if deltax = 1 m and rillwidth = 20 cm then the flow entering each pixel is assumed, for the purposes of rill development, to be localized in a width equal to one fifth of the pixel width.
        ########################### ^MAIN TAB^ ###########################

    def onFrameConfigure(self, event):
        '''Reset the scroll region to encompass the inner frame'''
        self.canvas2.configure(scrollregion=self.canvas2.bbox("all"))
    

    def on_mousewheel(self, event):
        """Binds scroll events to the second tab in the application"""
        shift = (event.state & 0x1) != 0
        scroll = -1 if event.delta > 0 else 1
        if shift:
            self.canvas2.xview_scroll(scroll, "units")
        else:
            self.canvas2.yview_scroll(scroll, "units")


    def getMask(self):
        if self.flagForMaskVar.get() == 1:
            self.client_socket.send(("Choose a mask.tif file\n\n").encode('utf-8'))
            try:
                maskfile = Path(askopenfilename(initialdir=Path.cwd().parent, filetypes=[('Image Files', ['.tif'])]))
                if maskfile.suffix == '.tar' or maskfile.suffix == '.gz':
                    maskfile = self.extract_geotiff_from_tarfile(maskfile,Path.cwd())

                shutil.copyfile(maskfile, Path.cwd() / "mask.tif")
                self.client_socket.send(("maskfile: is: " + str(maskfile) + "\n\n").encode('utf-8'))
            except Exception:
                self.client_socket.send(("Invalid mask.tif file\n\n").encode('utf-8'))

    def generate_parameters(self):
        """Generate the parameters.txt file using the flags from the second tab"""
        path = Path.cwd() / 'parameters.txt'
        if path.exists():
            Path.unlink(path)
        f = open('parameters.txt', 'w+')
        f.write(str(self.flagForEquationVar.get()) + '\t /* Flag for equation out */ \n')
        f.write(str(self.flagforDynamicModeVar.get()) + '\t /* Flag for dynamicmode out */ \n')
        f.write(str(self.flagForMaskVar.get()) + '\t /* Flag for mask out */ \n')
        f.write(str(self.flagForTaucSoilAndVegVar.get()) + '\t /* Flag for taucsoilandveg out */ \n')
        f.write(str(self.flagFord50Var.get()) + '\t /* Flag for d50 out */ \n')
        f.write(str(self.flagForRockCoverVar.get()) + '\t /* Flag for rockcover out */ \n')
        f.write(self.fillIncrementInput.get().replace("\n", "") + '\t /* fillIncrement out */ \n')
        f.write(self.minslopeInput.get().replace("\n", "") + '\t /* minslope out */ \n')
        f.write(self.expansionInput.get().replace("\n", "") + '\t /* Expansion out */ \n')
        f.write(self.yellowThresholdInput.get().replace("\n", "") + '\t /* Yellow threshold out */ \n')
        f.write(self.lattice_size_xInput.get().replace("\n", "") + '\t /* Lattice Size X out */ \n')
        f.write(self.lattice_size_yInput.get().replace("\n", "") + '\t /* Lattice Size Y out */ \n')
        f.write(self.deltaxInput.get().replace("\n", "") + '\t /* Delta X out */ \n')
        f.write(self.nodataInput.get().replace("\n", "") + '\t /* nodata out */ \n')
        f.write(self.smoothinglengthInput.get().replace("\n", "") + '\t /* smoothing length out */ \n')
        f.write(self.rainInput.get().replace("\n", "") + '\t /* Rain out */ \n')
        f.write(self.taucSoilAndVegeInput.get().replace("\n", "") + '\t /* tauc soil and vege out */ \n')
        f.write(self.d50Input.get().replace("\n", "") + '\t /* d50 out */ \n')
        f.write(self.rockcoverInput.get().replace("\n", "") + '\t /* rock cover out */ \n')
        f.write(self.tanAngleOfInternalFrictionInput.get().replace("\n", "") + '\t /* tangent of the angle of internal friction out*/ \n')
        f.write(self.bInput.get().replace("\n", "") + '\t /* b out */ \n')
        f.write(self.cInput.get().replace("\n", "") + '\t /* c out */ \n')
        f.write(self.rillWidthInput.get().replace("\n", "") + '\t /* rill width out */ \n')
        self.client_socket.send(("Generated parameters.txt\n\n").encode('utf-8'))
        f.close()

    
    def convert_geotiff_to_txt(self, filename):
        
        self.src_ds = gdal.Open(filename + ".tif")
        if self.src_ds is None:
            name = input
            messagebox.showerror(title="ERROR", message="Unable to open " + filename + " for writing")
            sys.exit(1)  
        # Open output format driver, see gdal_translate --formats for list
        format = "XYZ"
        driver = gdal.GetDriverByName( format )

        # Output to new format
        dst_ds = driver.CreateCopy( filename + "_dem.asc", self.src_ds, 0 )

        # Properly close the datasets to flush to disk
        self.src_ds = None
        dst_ds = None

        cmd1 = "gdal_translate -of XYZ " + filename + ".tif " + filename + ".asc"
        self.client_socket.send(subprocess.check_output(cmd1, shell=True) + ('\n').encode('utf-8'))

        cmd2 = "awk '{print $3}' " + filename + ".asc > " + filename + ".txt"
        self.client_socket.send(subprocess.check_output(cmd2, shell=True) + ('\n').encode('utf-8'))

        # remove temporary .asc file to save space
        cmd3 = "rm " + filename + "_dem.asc"
        self.client_socket.send(subprocess.check_output(cmd3, shell=True) + ('\n').encode('utf-8'))

    def generate_input_txt_file(self):
        """Generate the input.txt file using the flags from the second tab.
        
        There are then helper functions, the first of which runs the rillgen.c script
        in order to create xy_f.txt and xy_tau.txt (and xy_inciseddepth.txt if self.flagforDynamicModeVar.get()==1)

        The second helper function then sets the georeferencing information from the original
        geotiff file to xy_f.txt and xy_tau.txt (and xy_inciseddepth.txt if self.flagforDynamicModeVar.get()==1) in order to generate f.tif and tau.tif"""
        if self.t1 != None:
            self.t1.join()
            self.t1 = None
        path = Path.cwd() / 'input.txt'
        if path.exists():
            Path.unlink(path)
        path = Path.cwd()
        f = open('input.txt', 'w')
        f.write(str(self.flagForEquationVar.get()) + '\n')
        f.write(str(self.flagforDynamicModeVar.get()) + '\n')
        if (path / "dynamicinput.txt").exists():
            Path.unlink(path / "dynamicinput.txt")
        if self.flagforDynamicModeVar.get() == 1:
            if (path.parent / "dynamicinput.txt").exists():
                shutil.copyfile(path.parent / "dynamicinput.txt", path / "dynamicinput.txt")
                self.client_socket.send(("dynamicinput.txt found and copied to inner directory\n\n").encode('utf-8'))
            else:
                self.client_socket.send(("dynamicinput.txt not found\n\n").encode('utf-8'))


        f.write(str(self.flagForMaskVar.get())+'\n')  
        if self.flagForMaskVar.get() == 1:
            if (path / "mask.tif").exists():
                self.convert_geotiff_to_txt("mask")
                self.client_socket.send(("mask.txt generated\n\n").encode('utf-8'))
            else:
                self.client_socket.send(("mask.tif not found\n\n").encode('utf-8'))
                self.flagForMaskVar = 0

        f.write(str(self.flagForTaucSoilAndVegVar.get())+'\n')
        if (path / "taucsoilandvegfixed.txt").exists():
            Path.unlink(path / "taucsoilandvegfixed.txt")
        if self.flagForTaucSoilAndVegVar.get() == 1:
            if (path.parent / "taucsoilandvegfixed.txt").exists():
                shutil.copyfile(path.parent / "taucsoilandvegfixed.txt", path / "taucsoilandvegfixed.txt")
                self.client_socket.send(("taucsoilandvegfixed.txt found and copied to inner directory\n\n").encode('utf-8'))
            else:
                self.client_socket.send(("taucsoilandvegfixed.txt not found\n\n").encode('utf-8'))
        f.write(str(self.flagFord50Var.get())+'\n')
        if (path / "d50.txt").exists():
            Path.unlink(path / "d50.txt")
        if self.flagFord50Var.get() == 1:
            if (path.parent / "d50.txt").exists():
                shutil.copyfile(path.parent / "d50.txt", path / "d50.txt")
                self.client_socket.send(("d50.txt found and copied to inner directory\n\n").encode('utf-8'))
            else:
                self.client_socket.send(("d50.txt not found\n\n").encode('utf-8'))
        f.write(str(self.flagForRockCoverVar.get())+'\n')
        if (path / "rockcover.txt").exists():
            path.unlink(path / "rockcover.txt")
        if self.flagForRockCoverVar.get() == 1:
            if (path.parent / "rockcover.txt").exists():
                shutil.copyfile(path.parent / "rockcover.txt", path / "rockcover.txt")
                self.client_socket.send(("rockcover.txt found and copied to inner directory\n\n").encode('utf-8'))
            else:
                self.client_socket.send(("rockcover.txt not found\n\n").encode('utf-8'))
        f.write(self.fillIncrementInput.get().replace("\n", "")+'\n')
        f.write(self.minslopeInput.get().replace("\n", "")+'\n')
        f.write(self.expansionInput.get().replace("\n", "")+'\n')
        f.write(self.yellowThresholdInput.get().replace("\n", "")+'\n')
        f.write(self.lattice_size_xInput.get().replace("\n", "")+'\n')
        f.write(self.lattice_size_yInput.get().replace("\n", "")+'\n')
        f.write(self.deltaxInput.get().replace("\n", "")+'\n')
        f.write(self.nodataInput.get().replace("\n", "")+'\n')
        f.write(self.smoothinglengthInput.get().replace("\n", "")+'\n')
        f.write(self.rainInput.get().replace("\n", "")+'\n')
        f.write(self.taucSoilAndVegeInput.get().replace("\n", "")+'\n')
        f.write(self.d50Input.get().replace("\n", "")+'\n')
        f.write(self.rockcoverInput.get().replace("\n", "")+'\n')
        f.write(self.tanAngleOfInternalFrictionInput.get().replace("\n", "")+'\n')
        f.write(self.bInput.get().replace("\n", "")+'\n')
        f.write(self.cInput.get().replace("\n", "")+'\n')
        f.write(self.rillWidthInput.get().replace("\n", "")+'\n')
        self.client_socket.send(("Generated input.txt\n\n").encode('utf-8'))
        f.close()
        
        t1 = Thread(target=self.hillshade_and_color_relief)
        t1.start()
        self.setup_rillgen()
        t1.join()
        if self.first_time_populating_view_output_tab:
            self.tabControl.add(self.tab3, text="View Output")
            
        self.populate_view_output_tab()
        
        self.set_georeferencing_information()

    def generate_colorramp(self,filename,mode):
        """generates a color ramp from a geotiff image and then uses that in order to produce
        a color-relief for the geotiff"""
        gtif = gdal.Open(filename)
        srcband = gtif.GetRasterBand(1)
        # Get raster statistics
        stats = srcband.GetStatistics(True, True)
        f = open('color-relief.txt', 'w')
        if mode == 2 and stats[1] > 100:
            stats[1] = 100
            if stats[2] > 50:
                stats[2] = 50
        f.writelines([str(stats[0]) + ", 0, 0, 0\n", str(stats[0]+(stats[2]-stats[0])/4) + ", 167, 30, 66\n", str(stats[0]+(stats[2]-stats[0])/2) + ", 51, 69, 131\n", 
        str(stats[0]+3*(stats[2]-stats[0])/4) + ", 101, 94, 190\n", str(stats[2]) + ", 130, 125, 253\n", str(stats[2]+(stats[1]-stats[2])/4) + ", 159, 158, 128\n",
        str(stats[2]+(stats[1]-stats[2])/2) + ", 193, 192, 16\n", str(stats[2]+3*(stats[1]-stats[2])/4) + ", 224, 222, 137\n", str(stats[1]) + ", 255, 255, 255\n"])
        colormap = branca.colormap.LinearColormap([(0, 0, 0),(167, 30, 66),(51, 69, 131),(101, 94, 190),(130, 125, 253),(159, 158, 128),(193, 192, 16),(224, 222, 137),(255, 255, 255)])
        indexarr = [stats[0],stats[0]+(stats[2]-stats[0])/4,stats[0]+(stats[2]-stats[0])/2,stats[0]+3*(stats[2]-stats[0])/4,stats[2],
            stats[2]+(stats[1]-stats[2])/4,stats[2]+(stats[1]-stats[2])/2,stats[2]+3*(stats[1]-stats[2])/4,stats[1]]
        if mode == 1:
            self.colormap = colormap
            self.colormap = self.colormap.to_step(index=indexarr)
            self.colormap.caption = "Elevation (in meters)"
            cmd1 = "gdaldem color-relief " + filename + " color-relief.txt color-relief.png"
        elif mode == 2:
            self.taucolormap = colormap
            self.taucolormap = self.taucolormap.to_step(index=indexarr)
            self.taucolormap.caption = "Tau (in pascals)"
            cmd1 = "gdaldem color-relief " + filename + " color-relief.txt color-relief_tau.png"
        else:
            self.fcolormap = colormap
            self.fcolormap = self.fcolormap.to_step(index=indexarr)
            self.fcolormap.caption = "F (in pascals)"
            cmd1 = "gdaldem color-relief " + filename + " color-relief.txt color-relief_f.png"
        f.close()
        self.client_socket.send(subprocess.check_output(cmd1, shell=True) + ('\n').encode('utf-8'))
        self.client_socket.send(("Hillshade and color relief generated\n\n").encode('utf-8'))
        gtif = None


    def hillshade_and_color_relief(self):
        """Generates the hillshade and color-relief images from the original 
        geotiff image that will be available on the map"""

        self.client_socket.send(("Generating hillshade and color relief...\n\n").encode('utf-8'))
        cmd0 = "gdaldem hillshade " + self.filename + " hillshade.png"
        self.client_socket.send(subprocess.check_output(cmd0, shell=True) + ('\n').encode('utf-8'))
        self.generate_colorramp(self.filename,1)

    def make_popup(self, mode):
        if mode == 1:
            self.popup = tk.Toplevel(root)
            self.popupLabel = tk.Label(self.popup, text="hydrologic correction step in progress")
            self.popupLabel.pack(side=tk.TOP)
            self.progress_bar = ttk.Progressbar(self.popup, orient=HORIZONTAL, length=300, mode='determinate', maximum=100, style='text.Horizontal.TProgressbar')
        else:
            self.popupLabel.configure(text="dynamic mode in progress")
            self.popupLabel.update()
        
        # get screen width and height
        ws = root.winfo_screenwidth()
        hs = root.winfo_screenheight()
        # calculate position x, y
        x = (ws/2) - (350/2)    
        y = (hs/2) - (75/2)
        self.popup.geometry('%dx%d+%d+%d' % (350, 75, x, y))
        self.progress_bar.pack(fill=tk.X, expand=1, side=tk.BOTTOM)

    def update_progressbar(self, value):
        """Updates the value on the progressbar as the 
        hydrologic correction step is carried out"""
        self.progress_bar['value'] = value
        self.style.configure('text.Horizontal.TProgressbar',
                        text='{:g} %'.format(value))
        root.update()


    def setup_rillgen(self):
        """Sets up files for the rillgen.c code by creating topo.txt and xy.txt, and
        imports the rillgen.c code using the CDLL library"""
        mode = 1
        self.client_socket.send(("Running rillgen.c...\n\n").encode('utf-8'))
        self.make_popup(mode)
        cmd0 = "awk '{print $3}' " + self.imagefile.stem + ".asc > topo.txt"
        self.client_socket.send(subprocess.check_output(cmd0, shell=True) + ('\n').encode('utf-8'))
        cmd1 = "awk '{print $1, $2}' " + self.imagefile.stem + ".asc > xy.txt"
        self.client_socket.send(subprocess.check_output(cmd1, shell=True) + ('\n').encode('utf-8'))
        if self.rillgen == None:
            self.rillgen = CDLL(str(Path.cwd().parent / 'rillgen.so'))
        t1 = Thread(target=self.run_rillgen)
        t1.start()
        still_update = True
        self.client_socket.send(("Starting hydrologic correction step...\n\n").encode('utf-8'))
        while still_update:
            if mode == 1:
                currentPercentage = self.rillgen.hydrologic_percentage()
            else:
                currentPercentage = self.rillgen.dynamic_percentage()
            if currentPercentage == 0:
                time.sleep(0.5)
            elif currentPercentage > 0 and currentPercentage < 100:
                self.update_progressbar(currentPercentage)
                time.sleep(0.5)
            else:
                self.update_progressbar(100)
                if mode == 1 and self.flagforDynamicModeVar.get() == 1:
                    mode = 2
                    self.client_socket.send(("Hydrologic correction step completed.\n\n").encode('utf-8'))
                    currentPercentage = 0
                    self.update_progressbar(currentPercentage)
                    self.client_socket.send(("Starting dynamic mode...\n\n").encode('utf-8'))
                    self.make_popup(mode)
                else:
                    if self.flagforDynamicModeVar.get() == 1:
                        self.client_socket.send(("Dynamic mode completed. Creating outputs...\n\n").encode('utf-8'))
                    else:
                        self.client_socket.send(("Hydrologic correction step completed. Creating outputs...\n\n").encode('utf-8'))
                    self.popup.withdraw()
                    self.popup.destroy()
                    still_update = False
        t1.join()
        

    def run_rillgen(self):
        """Runs the rillgen.c library using the CDLL module"""
        self.rillgen.main()
        cmd4 = "paste xy.txt tau.txt > xy_tau.txt"
        self.client_socket.send(subprocess.check_output(cmd4, shell=True) + ('\n').encode('utf-8'))
        cmd5 = "paste xy.txt f.txt > xy_f.txt"
        self.client_socket.send(subprocess.check_output(cmd5, shell=True) + ('\n').encode('utf-8'))


    def populate_view_output_tab(self):
        """Populate the third tab with tkinter widgets. The third tab allows
        the user to generate a folium map based on the rillgen output
        and also allows them to preview the image hillshade and color relief"""
        if self.first_time_populating_view_output_tab:
            self.canvas3 = tk.Canvas(self.tab3, borderwidth=0, highlightthickness=0)
            self.canvas3.bind("<Configure>", self.schedule_resize_canvas)
            self.canvas3.height = self.canvas3.winfo_reqheight()
            self.canvas3.width = self.canvas3.winfo_reqwidth()
            self.frame3 = tk.Frame(self.canvas3)
            self.view_output_window = self.canvas3.create_window((0,0), window=self.frame3, anchor="nw")

        self.canvas3bg = PIL.Image.open(Path.cwd().as_posix() + "/hillshade.png")
        self.canvas3fg = PIL.Image.open(Path.cwd().as_posix() + "/color-relief.png")
        self.bgcpy = self.canvas3bg.copy()
        self.fgcpy = self.canvas3fg.copy()
        self.bgcpy = self.bgcpy.convert("RGBA")
        self.fgcpy = self.fgcpy.convert("RGBA")
        self.alphablended = PIL.Image.blend(self.bgcpy, self.fgcpy, alpha=.4)
        self.canvas3.blended_image = PIL.Image.new("RGBA", self.alphablended.size)
        self.canvas3.blended_image.paste(self.alphablended)
        self.canvas3.blended_image.save("background.png")
        cmd = "gdal_translate background.png background.jpg -of JPEG" # some tkinter versions do not support .png images
        self.client_socket.send(subprocess.check_output(cmd, shell=True) + ('\n').encode('utf-8'))
        self.img3 = PIL.Image.open(Path.cwd().as_posix() + "/background.jpg")
        self.img3 = self.img3.resize((self.canvas3.width, self.canvas3.height))
        self.canvas3img = ImageTk.PhotoImage(self.img3)
        self.client_socket.send(("Preview Complete\n\n").encode('utf-8'))

        if self.first_time_populating_view_output_tab:
            self.canvas3imlbl = Label(self.frame3, image=self.canvas3img)
            self.canvas3imlbl.place(relx=0,rely=0)
            self.canvas3Label = tk.Label(self.frame3, text='Outputs: Preview model outputs in Leaflet Map or open Outputs folder and view previous models', font='Helvetica 18', justify=CENTER, wraplength=800)
            self.canvas3Label.place(relx=0.5, rely=0.25, anchor=CENTER)
            self.button3 = ttk.Button(self.frame3, text="View Outputs Map", command=self.generatemap)
            self.button3.place(relx=0.5, rely=0.5, anchor=CENTER)
            self.button3 = ttk.Button(self.frame3, text="View Outputs Folder", command=self.view_output_folder)
            self.button3.place(relx=0.5, rely=0.75, anchor=CENTER)
            self.canvas3.itemconfig(self.view_output_window, height=self.canvas3.height, width=self.canvas3.width)
            self.canvas3.pack(side="left", fill="both", expand=YES)
            self.resize_canvas()
            self.first_time_populating_view_output_tab = False
            
        self.canvas3imlbl.configure(image=self.canvas3img)
        

    def view_output_folder(self):
        currentDir = Path.cwd()
        outputDir = askdirectory(initialdir=Path.cwd().parent)
        if outputDir != '':
            os.chdir(outputDir)
            self.displayMap()
            os.chdir(currentDir)

    def schedule_resize_canvas(self,event):
        """Schedule resizing the canvas for the view output tab on a user click/drag event.
        The canvas cannot be continuously resized because rendering is too slow"""
        if self.can_redraw:
            self.after_cancel(self.can_redraw)
        self.canvas3.width = event.width
        self.canvas3.height = event.height
        # resize the canvas 
        self.canvas3.config(width=self.canvas3.width, height=self.canvas3.height)
        self.can_redraw = self.after(500,self.resize_canvas)


    def resize_canvas(self):
        """Resizes the canvas for the view output tab"""
        self.canvas3.itemconfig(self.view_output_window, height=self.canvas3.height, width=self.canvas3.width)
        self.canvas3img = self.img3.resize((self.canvas3.width, self.canvas3.height))
        self.canvas3img = ImageTk.PhotoImage(self.canvas3img)
        self.canvas3imlbl.configure(image=self.canvas3img)


    def set_georeferencing_information(self):
        """Sets the georeferencing information for f.tif and tau.tif (and inciseddepth.t if self.flagforDynamicModeVar.get()==1) to be the same as that
        from the original geotiff file"""
        self.client_socket.send(("Setting georeferencing information\n\n").encode('utf-8'))
        if self.filename != None and Path(self.filename).exists():
            ds = gdal.Open(self.filename)
            gt=ds.GetGeoTransform()
            cols = ds.RasterXSize
            rows = ds.RasterYSize
            ext=self.GetExtent(gt,cols,rows)
            src_srs=osr.SpatialReference()
            if int(osgeo.__version__[0]) >= 3:
                # GDAL 3 changes axis order: https://github.com/OSGeo/gdal/issues/1546
                src_srs.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
            proj = ds.GetProjection()
            src_srs.ImportFromWkt(proj)
            tgt_srs = src_srs.CloneGeogCS()

            self.geo_ext=self.ReprojectCoords(ext,src_srs,tgt_srs)
            cmd0 = "gdal_translate xy_tau.txt tau.tif"
            self.client_socket.send(subprocess.check_output(cmd0, shell=True) + ('\n').encode('utf-8'))
            t1 = Thread(target=self.generate_colorramp("tau.tif",2))
            t1.start()
            cmd1 = "gdal_translate xy_f.txt f.tif"
            self.client_socket.send(subprocess.check_output(cmd1, shell=True) + ('\n').encode('utf-8'))
            t2 = Thread(target=self.generate_colorramp("f.tif",3))
            t2.start()
            projection = ds.GetProjection()
            geotransform = ds.GetGeoTransform()

            if projection is None and geotransform is None:
                self.client_socket.send(("No projection or geotransform found on file" + str(self.filename) + "\n\n").encode('utf-8'))
                sys.exit(1)

            for elem in ["tau.tif", "f.tif", "inciseddepth.tif"]:
                if (Path.cwd() / elem).exists():
                    ds2 = gdal.Open(elem, gdal.GA_Update)
                    if ds2 is None:
                        self.client_socket.send(("Unable to open " + elem + " for writing\n\n").encode('utf-8'))
                        print('Unable to open', elem, 'for writing')
                        sys.exit(1)
                    
                    if geotransform is not None and geotransform != (0, 1, 0, 0, 0, 1):
                        ds2.SetGeoTransform(geotransform)

                    if projection is not None and projection != '':
                        ds2.SetProjection(projection)

                    gcp_count = ds.GetGCPCount()
                    if gcp_count != 0:
                        ds2.SetGCPs(ds.GetGCPs(), ds.GetGCPProjection())
                    
                    if elem == "tau.tif":
                        self.client_socket.send(("Translating tau.tif to .png\n\n").encode('utf-8'))
                        cmd2 = "gdal_translate -a_nodata 255 -ot Byte -of PNG " + elem.split(sep='.')[0] + ".tif " + elem.split(sep='.')[0] + ".png"
                    elif elem == "f.tif":
                        self.client_socket.send(("Translating f.tif to .png\n\n").encode('utf-8'))
                        cmd2 = "gdal_translate -a_nodata 255 -ot Byte -scale 0 0.1 -of PNG " + elem.split(sep='.')[0] + ".tif " + elem.split(sep='.')[0] + ".png"
                    else:
                        self.client_socket.send(("Translating inciseddepth.tif to .png\n\n").encode('utf-8'))
                        cmd2 = "gdal_translate -a_nodata 255 -ot Byte -of PNG " + elem.split(sep='.')[0] + ".tif " + elem.split(sep='.')[0] + ".png"
                    self.client_socket.send(subprocess.check_output(cmd2, shell=True) + ('\n').encode('utf-8'))

                ds2 = None
            ds = None
        else: 
            messagebox.showerror(title="FILE NOT FOUND", message="Please select a file in tab 1")
        t1.join()
        t2.join()
        self.client_socket.send(("Georeferencing complete\n\n").encode('utf-8'))
        self.convert_ppm()
        self.client_socket.send(("Outputs complete\n\n").encode('utf-8'))


    def convert_ppm(self):
        """Convert the rills.ppm file to png so that it can be displayed on the map"""
        if not Path("rills.ppm").exists():
            self.client_socket.send(("Unable to open rills.ppm for writing\n\n").encode('utf-8'))
        else:
            self.client_socket.send(("Translating rills.ppm to .png\n\n").encode('utf-8'))
            with im(filename="rills.ppm") as img:
                img.save(filename="P6.ppm")
            cmd = "gdal_translate -of PNG -a_nodata 255 P6.ppm rills.png"
            self.client_socket.send(subprocess.check_output(cmd, shell=True) + ('\n').encode('utf-8'))


    def GetExtent(self,gt,cols,rows):
        """Return list of corner coordinates from a geotransform given the number
        of columns and the number of rows in the dataset"""
        ext=[]
        xarr=[0,cols]
        yarr=[0,rows]

        for px in xarr:
            for py in yarr:
                x=gt[0]+(px*gt[1])+(py*gt[2])
                y=gt[3]+(px*gt[4])+(py*gt[5])
                ext.append([x,y])
            yarr.reverse()
        return ext

    def ReprojectCoords(self, coords,src_srs,tgt_srs):
        """Reproject a list of x,y coordinates. From srs_srs to tgt_srs"""
        trans_coords=[]
        transform = osr.CoordinateTransformation( src_srs, tgt_srs)
        for x,y in coords:
            x,y,z = transform.TransformPoint(x,y)
            trans_coords.append([x,y])
        return trans_coords


    def generatemap(self):
        """Generates a folium map based on the bounds of the geotiff file"""
        mapbounds = [[self.geo_ext[1][1], self.geo_ext[1][0]], [self.geo_ext[3][1], self.geo_ext[3][0]]]
        m = folium.Map(location=[(self.geo_ext[1][1]+self.geo_ext[3][1])/2, (self.geo_ext[1][0]+self.geo_ext[3][0])/2], zoom_start=14, tiles='Stamen Terrain')
        folium.TileLayer('OpenStreetMap').add_to(m)
        folium.TileLayer('Stamen Toner').add_to(m)

        self.layer_control = folium.LayerControl()
        img1 = folium.raster_layers.ImageOverlay(image="hillshade.png", bounds=mapbounds, opacity=0.8, interactive=True, show=True, name="hillshade")
        img2 = folium.raster_layers.ImageOverlay(image="color-relief.png", bounds=mapbounds, opacity=0.6, interactive=True, show=False, name="color-relief")
        img3 = folium.raster_layers.ImageOverlay(image="f.png", bounds=mapbounds, opacity=0.5, interactive=True, show=False, name="f")
        img4 = folium.raster_layers.ImageOverlay(image="tau.png", bounds=mapbounds, opacity=0.5, interactive=True, show=True, name="tau")
        img5 = folium.raster_layers.ImageOverlay(image="rills.png", bounds=mapbounds, opacity=0.5, interactive=True, show=False, name="rills")
        img6 = folium.raster_layers.ImageOverlay(image="color-relief_tau.png", bounds=mapbounds, opacity=0.5, interactive=True, show=False, name="color-relief_tau")
        img7 = folium.raster_layers.ImageOverlay(image="color-relief_f.png", bounds=mapbounds, opacity=0.5, interactive=True, show=False, name="color-relief_f")
        # geotiff_group = folium.FeatureGroup(name="color-relief")
        # geotiff_group.add_child(img1)
        # geotiff_group.add_child(img2)
        # geotiff_group.add_child(self.colormap)
        img1.add_to(m)
        img2.add_to(m)
        img3.add_to(m)
        img4.add_to(m)
        img5.add_to(m)
        img6.add_to(m)
        img7.add_to(m)
        # geotiff_group.add_to(m)
        # m.add_child(geotiff_group)
        self.colormap.add_to(m)
        self.taucolormap.add_to(m)
        self.fcolormap.add_to(m)
        self.layer_control.add_to(m)
        m.save("map.html", close_file=True)
        t1 = Thread(target=self.saveOutput)
        t1.start()
        self.displayMap()
        t1.join()
            

    def saveOutput(self):
        """Save outputs from a run in a timestamp-marked folder"""
        saveDir = "outputs_save-" + str(datetime.now()).replace(" ", "").replace(":", ".")
        Path.mkdir(Path.cwd().parent / saveDir)
        saveDir = Path.cwd().parent / saveDir
        acceptable_files = ["parameters.txt", "input.txt", "map.html", "rills.ppm"]
        for fname in Path.cwd().iterdir():
            file_name = fname.name
            if file_name in acceptable_files or (file_name.endswith(".png") or file_name.endswith(".tif")):
                shutil.copy(file_name, saveDir / file_name)
        shutil.copy(self.filename, saveDir / Path(self.filename).name)

    def displayMap(self):
        """Uses the map.html file to generate a folium map using QtWidgets.QWebEngineView()"""
        if Path("map.html").exists():
            mapfile = QtCore.QUrl.fromLocalFile(Path("map.html").resolve().as_posix())
            if self.app == None:
                self.app = QtWidgets.QApplication([])

            class MainWindow(QMainWindow):
                def __init__(self, *args, **kwargs):
                    super(MainWindow, self).__init__(*args, **kwargs)

                    self.setWindowTitle("View Output")

                    w = QtWebEngineWidgets.QWebEngineView()
                    w.load(mapfile)

                    # Set the central widget of the Window. Widget will expand
                    # to take up all the space in the window by default.
                    self.setCentralWidget(w)

                def closeEvent(self, event):
                    reply = QMessageBox.question(self, "Window Close", "Are you sure you want to close the window?", QMessageBox.No | QMessageBox.Yes, QMessageBox.Yes)
                    if reply == QMessageBox.Yes:
                        event.accept()
                        try:
                            app.quit()
                        except Exception as e:
                            print("exception reached")
                            print(str(e))
                    else: 
                        event.ignore()

            app = self.app.instance()
            main_window = MainWindow()
            main_window.show()
            app.exec_()
        else:
            self.client_socket.send(("No map.html file found\n\n").encode('utf-8'))


if __name__ == "__main__":
    root=tk.Tk()
    root.resizable(True, True)
    root.title("rillgen2D")
    if Path('input.txt').is_file():
        example = Application(root)
        example.pack(side="top", fill="both", expand=True)
        root.mainloop()
    else:
        raise Exception("A file with the name input.txt was not found.")