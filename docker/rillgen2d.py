import io
import os
import subprocess
import shutil
import sys
import tarfile
import tkinter as tk
import urllib.request as urllib

import folium
import matplotlib.pyplot as plt
import osgeo
import rasterio

from datetime import datetime
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg)
from matplotlib.figure import Figure
from osgeo import gdal, osr
from PyQt5 import QtWidgets, QtWebEngineWidgets, QtCore
from PyQt5.QtWidgets import QApplication, QMessageBox, QMainWindow
from rasterio.plot import show
from threading import Thread
from tkinter import *
from tkinter import messagebox
from tkinter import ttk
from tkinter.filedialog import askopenfilename

class Application(tk.Frame):
    def __init__(self, parent):
        """Initializing the tkinter application and its tabs.
        The PyQt5 Application must go where it can be initialized
        only once in order to avoid bugs; otherwise the garbage
        collector does not handle it correctly."""
        tk.Frame.__init__(self, parent)
        self.imagefile = None # This is the image file that will be used
        self.filename = None  #this is the name of the input file the user chooses
        self.app = None  # This is the associated PyQt application that handles the map in View Output
        self.dimensions = None  # These are the dimensions of the input file that the user chooses
        self.starterimg = None  # This is the image to be displayed in the input_dem tab
        self.popup = None  # This is the popup that comes up during the hydrologic correction step 
        self.tabControl = ttk.Notebook(self)
        self.tab1 = ttk.Frame(self.tabControl)
        self.tab2 = ttk.Frame(self.tabControl)
        self.tab3 = ttk.Frame(self.tabControl)

        """We only want the first tab for now; the others appear in order after the 
        processes carried out in a previous tab are completed"""
        self.tabControl.add(self.tab1, text="Input DEM") 
        self.tabControl.pack(expand=1, fill="both")
        self.first_time_populating_parameters_tab = True
        self.first_time_populating_view_output_tab = True
        self.populate_input_dem_tab()


    def populate_input_dem_tab(self):
        """This populates the first tab in the application with tkinter widgets.
        The first tab allows a user to select an geotiff image from either their 
        local filesystem or from a url. """
        
        self.button1 = ttk.Button(self.tab1, text="Choose DEM (.tif) locally", command=self.get_image_locally)
        self.button1.grid(row=0, column=0)

        self.entry1 = Entry(self.tab1, width=55)
        self.entry1.insert(0, "Or enter in a url for a DEM (.tif) image in this box and press the button below")
        self.entry1.first_time_clicked = True

        def delete_default_text(event):
            if self.entry1.first_time_clicked == True:
                self.entry1.delete(0, "end")
                self.entry1.first_time_clicked = False

        self.entry1.bind("<Button-1>", delete_default_text)
        self.entry1.grid(row=1, column=0)

        self.button2 = ttk.Button(self.tab1, text="Go", command=self.get_image_from_url)
        self.button2.grid(row=2, column=0)

        self.img1 = Label(self.tab1)

        self.fig = Figure(figsize=(5, 5), dpi=100)

        self.canvas1 = FigureCanvasTkAgg(self.fig, master=self.img1)
        self.canvas1.draw()
        self.canvas1.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1, padx=0, pady=0)
        self.canvas1._tkcanvas.pack(side=TOP, fill=BOTH, expand=1, padx=0, pady=0)

        self.img1.grid(row=0, column=2, rowspan=3, sticky=N+S+E+W)

        style = ttk.Style()
        style.configure('W.TButton', font="Helvetica", foreground='red')

        self.save_image = ttk.Button(self.tab1, text="Save Image", style='W.TButton', command=self.saveimageastxt)
        self.save_image.grid(row=3, column=1)
        self.tab1.columnconfigure(0, weight=1)
        self.tab1.columnconfigure(1, weight=1)
        self.tab1.columnconfigure(2, weight=1)
        self.tab1.rowconfigure(0, weight=5)
        self.tab1.rowconfigure(1, weight=1)
        self.tab1.rowconfigure(2, weight=1)
        self.tab1.rowconfigure(3, weight=1)


    def get_image_locally(self):
        """Given a geotiff image, either in .tar format or directly, extract the image and display
        it on the canvas"""
        try:
            self.imagefile = askopenfilename()
            if (str(self.imagefile)[-4:] == '.tar'):
                self.extract_geotiff_from_tarfile(self.imagefile, mode=1)
        except:
            messagebox.showerror(title="ERROR", message="Invalid file type. Please select an image file")
        else:
            self.preview_geotiff(mode=1)

    
    def get_image_from_url(self):
        """Given the url of an image when a raster is generated or located online, extract the geotiff image from the 
        url and display it on the canvas """
        try: 
            entry1 = str(self.entry1.get())
            if (entry1[-3:] == '.gz'):
                file_handler = urllib.urlopen(entry1)
                self.extract_geotiff_from_tarfile(file_handler, mode=2)
            else: # Given a geotiff image directly from url
                raw_data = urllib.urlopen(entry1).read()
                self.starterimg = rasterio.open(io.BytesIO(raw_data))
        except Exception:
            messagebox.showerror(title="ERROR", message="Invalid url. Please use the url for an image")
        else:
            self.preview_geotiff(mode=2)

    
    def extract_geotiff_from_tarfile(self, file_to_open, mode):
        """If the geotiff image is contained within a .tar file,
        extract the geotiff image from the file"""
        tar = None
        if mode == 1:
            tar = tarfile.open(file_to_open)
        else:
            tar = tarfile.open(fileobj=file_to_open, mode="r|gz")
        endreached = False
        while(endreached == False):
            nextfile = tar.next()
            if (nextfile == None):
                endreached = True
            else:
                if (nextfile.name[-4:] == '.tif'):
                    self.imagefile = nextfile.name
                    endreached = True
        tar.extract(nextfile)
        tar.close()

    def preview_geotiff(self, mode):
        """Display the geotiff on the canvas of the first tab"""
        try:
            self.starterimg = rasterio.open(self.imagefile)
            if (self.imagefile[-4:] == '.tif'):
                ax = self.fig.add_subplot(111)
                self.fig.subplots_adjust(bottom=0, right=1, top=1, left=0, wspace=0, hspace=0)

                with self.starterimg as src_plot:
                    show(src_plot, ax=ax)
                plt.close()
                ax.set(title="",xticks=[], yticks=[])
                ax.spines["top"].set_visible(False)
                ax.spines["right"].set_visible(False)
                ax.spines["left"].set_visible(False)
                ax.spines["bottom"].set_visible(False)
                self.canvas1.draw()
            else:
                messagebox.showerror(title="ERROR", message="Invalid File Format. Supported files must be in TIFF format")
        except Exception as e:
                messagebox.showerror(title="ERROR", message="The exception was: " + str(e))

    def saveimageastxt(self):
        """Prepares the geotiff file for the rillgen2D code by getting its dimensions (for the input.txt file) and converting it to
        .txt format"""
        if (self.imagefile == None or self.imagefile == ""):
            messagebox.showerror(title="NO FILENAME CHOSEN", message="Please choose a valid file")
        else:
            if (os.getcwd().split("/")[-1] == "tmp"):
                os.chdir("..")
            if os.path.exists(os.getcwd() + "/tmp"):
                shutil.rmtree(os.getcwd() + "/tmp")
            os.mkdir(os.getcwd() + "/tmp/")
            self.filename = os.getcwd() + "/tmp/" + self.imagefile.split("/")[-1]
            shutil.copyfile(self.imagefile, self.filename)
            shutil.copyfile("template_input.txt", os.getcwd() + "/tmp/" + "input.txt")
            os.chdir(os.getcwd() + "/tmp")
            
        # Open existing dataset
            self.src_ds = gdal.Open(self.filename)
            band = self.src_ds.GetRasterBand(1)
            arr = band.ReadAsArray()
            self.dimensions = [arr.shape[0], arr.shape[1]]
            t1 = Thread(target=self.populate_parameters_tab)
            t1.start()  # Populates the second tab since now the user has chosen a file
            if self.src_ds is None:
                name = input
                messagebox.showerror(title="ERROR", message="Unable to open" + name + "for writing")
                print('Unable to open', input, 'for writing')
                sys.exit(1)    
            
            # Open output format driver, see gdal_translate --formats for list
            format = "XYZ"
            driver = gdal.GetDriverByName( format )

            # Output to new format
            dst_ds = driver.CreateCopy( "input_dem.asc", self.src_ds, 0 )

            # Properly close the datasets to flush to disk
            dst_ds = None

            # Create the `.txt` with `awk` but in Python using `os` call:
            cmd0 = "gdal_translate -ot Float32 -of XYZ " + self.filename + " output_tin.asc"
            returned_value = os.system(cmd0)  # returns the exit code in unix
            print('returned value:', returned_value)

            cmd1 = "awk '{print $3}' input_dem.asc > input_dem.txt"

            returned_value = os.system(cmd1)  # returns the exit code in unix
            print('returned value:', returned_value)

            # remove temporary .asc file to save space
            cmd2 = "rm input_dem.asc"
            returned_value = os.system(cmd2)  # returns the exit code in unix
            print('returned value:', returned_value)
            if self.first_time_populating_parameters_tab == True:
                self.tabControl.add(self.tab2, text="Parameters")
                self.tabControl.pack(expand=1, fill="both")

    def populate_parameters_tab(self):
        """Populate the second tab in the application with tkinter widgets. This tab holds editable parameters
        that will be used to run the rillgen2d.c script. lattice_size_x and lattice_size_y are read in from the
        geometry of the geotiff file"""

        if self.first_time_populating_parameters_tab == True:
            self.canvas2 = tk.Canvas(self.tab2, borderwidth=0)
            self.frame2 = tk.Frame(self.canvas2)
            self.hsb = tk.Scrollbar(self.tab2, orient="horizontal", command=self.canvas2.xview)
            self.vsb = tk.Scrollbar(self.tab2, orient="vertical", command=self.canvas2.yview)
            self.canvas2.configure(xscrollcommand=self.hsb.set, yscrollcommand=self.vsb.set)

            self.hsb.pack(side="bottom", fill="x")
            self.vsb.pack(side="right", fill="y")
            self.canvas2.pack(side="left", fill="both", expand=True)
            self.canvas2.create_window((4,4), window=self.frame2, anchor="nw",
                                    height=root.winfo_screenheight()*3.5, width=root.winfo_screenwidth(), tags="self.frame")
            self.frame2.bind("<Configure>", self.onFrameConfigure)
            self.frame2.bind_all("<MouseWheel>", self.on_mousewheel)
        
        f = open('input.txt', 'r')

        # LABELS
        Label(self.frame2, text='rillgen2d', font='Helvetica 40 bold italic underline').grid(row=1, column=1, sticky=(N), pady=20)
        Label(self.frame2, text='Inputs', font='Halvetica 20 bold underline').grid(row=2, column=0, sticky=(N,E,S,W), pady=20)
        Label(self.frame2, text='Input Descriptions', font='Halvetica 20 bold underline').grid(row=2, column=2, sticky=(N,E,S,W), pady=50)
        self.parameterButton = ttk.Button(self.frame2, text='Generate Parameters', command=self.generate_parameters)
        self.parameterButton.grid(row=55, column=0)
        self.goButton = ttk.Button(self.frame2, text='Run Rillgen', command=self.generate_input_txt_file)
        self.goButton.grid(row=55, column=2)


        # Flag for mask variable
        Label(self.frame2, text='Flag for mask.txt:', font='Helvetica 25 bold').grid(row=3, column=0, pady=20)
        Label(self.frame2, text='Should be checked if the user provides a raster (mask.txt) that restricts the model to certain portions of the input DEM.', font='Helvetica 20',justify=CENTER, wraplength=750).grid(row=3, column=2, pady=20)
        
        self.flagformaskVar = IntVar(value=int(f.readline()))
        Checkbutton(self.frame2, variable=self.flagformaskVar, width=5).grid(row=3, column=1, pady=20)

        Frame(self.frame2, width=self.frame2.winfo_screenwidth(), height=5, background="PeachPuff").grid(row=4, column=0, columnspan=3, padx=0)

        # Flag for slope variable
        Label(self.frame2, text='Flag for slope.txt:', font='Helvetica 25 bold').grid(row=5, column=0, pady=20)
        Label(self.frame2, text='Should be checked if the user provides a raster (slope.txt) of slope is provided by the user.', font='Helvetica 20',justify=CENTER, wraplength=750).grid(row=5, column=2, pady=20)
        self.flagforslopeVar = IntVar(value=int(f.readline()))
        Checkbutton(self.frame2, variable=self.flagforslopeVar, width=5).grid(row=5, column=1, pady=20)

        Frame(self.frame2, width=self.frame2.winfo_screenwidth(), height=5, background="PeachPuff").grid(row=6, column=0, columnspan=3, padx=0)

        #Flag for rain variable
        Label(self.frame2, text='Flag for rain.txt:', font='Helvetica 25 bold').grid(row=7, column=0, pady=20)
        Label(self.frame2, text='Should be checked if the user provides a raster (rain.txt) that maps the peak 5 minute rainfall intensity.\nIf unchecked, a fixed value equal to rainfixed will be used.', font='Helvetica 20',justify=CENTER, wraplength=750).grid(row = 7, column=2, pady=20)
        self.flagforRainVar = IntVar(value=int(f.readline()))
        Checkbutton(self.frame2, variable=self.flagforRainVar, width=5).grid(row=7, column=1, pady=20)

        Frame(self.frame2, width=self.frame2.winfo_screenwidth(), height=5, background="PeachPuff").grid(row=8, column=0, columnspan=3)

        # Flagfortaucsoilandveg variable
        Label(self.frame2, text='Flag for taucsoilandveg.txt:', font='Helvetica 25 bold').grid(row=9, column=0, pady=20)
        Label(self.frame2, text='Should be checked if the user provides a raster of the shear strength of the soil and vegetation\n(taucsoilandveg.txt) equal to in size and resolution to the input DEM.', font='Helvetica 20',justify=CENTER, wraplength=750).grid(row=9, column=2, pady=20)
        self.flagfortaucsoilandvegVar = IntVar(value=int(f.readline()))
        flagfortaucsoilandvegInput = Checkbutton(self.frame2, variable=self.flagfortaucsoilandvegVar, width=5, pady=20)
        flagfortaucsoilandvegInput.grid(row=9, column=1, pady=20)
        # Should be 1 if the user provides a raster of the shear strength of the soil and vegetation (taucsoilandveg.txt) equal to in size and resolution to the input DEM.

        Frame(self.frame2, width=self.frame2.winfo_screenwidth(), height=5, background="PeachPuff").grid(row=10, column=0, columnspan=3)
   
        # Flag for d50 variable
        Label(self.frame2, text='Flag for d50.txt:', font='Helvetica 25 bold').grid(row=11, column=0, pady=20)
        Label(self.frame2, text='Should be checked if the user provides a raster of median rock armor particle diameter (d50.txt)\nequal in size and resolution to the input DEM.', font='Helvetica 20',justify=CENTER, wraplength=750).grid(row=11, column=2, pady=20)
        self.flagford50Var = IntVar(value=int(f.readline()))
        flagford50Input = Checkbutton(self.frame2, variable=self.flagford50Var, width=5, pady=20)
        flagford50Input.grid(row=11, column=1)
        # Should be 1 if the user provides a raster (d50.txt) that maps the median rock diameter, 0 means a fixed value equal to d50fixed will be used.

        Frame(self.frame2, width=self.frame2.winfo_screenwidth(), height=5, background="PeachPuff").grid(row=12, column=0, columnspan=3)

        # Flag for cu variable        
        Label(self.frame2, text='Flag for cu.txt:', font='Helvetica 25 bold').grid(row=13, column=0, pady=20)
        Label(self.frame2, text='Should be checked if the user provides a raster (cu.txt) that maps the coefficient of uniformity, 0 means a fixed value equal to cufixed will be used.', font='Helvetica 20', justify=CENTER, wraplength=750).grid(row=13, column=2, pady=20)
        self.flagforcuVar = IntVar(value=int(f.readline()))
        flagforcuInput = Checkbutton(self.frame2, variable=self.flagforcuVar, width=5, pady=20)
        flagforcuInput.grid(row=13, column=1)
        # Should be 1 if the user provides a raster (cu.txt) that maps the coefficient of uniformity, 0 means a fixed value equal to cufixed will be used.

        Frame(self.frame2, width=self.frame2.winfo_screenwidth(), height=5, background="PeachPuff").grid(row=14, column=0, columnspan=3)

        # Flag for thickness variable
        Label(self.frame2, text='Flag for thickness.txt:', font='Helvetica 25 bold').grid(row=15, column=0, pady=20)
        Label(self.frame2, text='Should be checked if the user provides a raster (thickness.txt) that maps the rock armor thickness, unchecked means a fixed value equal to thicknessfixed will be used.', font='Helvetica 20',justify=CENTER, wraplength=750).grid(row=15, column=2, pady=20)
        self.flagforthicknessVar = IntVar(value=int(f.readline()))
        flagforthicknessInput = Checkbutton(self.frame2, variable=self.flagforthicknessVar, width=5, pady=20)
        flagforthicknessInput.grid(row=15, column=1)
        # Should be 1 if the user provides a raster (thickness.txt) that maps the rock armor thickness, 0 means a fixed value equal to thicknessfixed will be used.

        Frame(self.frame2, width=self.frame2.winfo_screenwidth(), height=5, background="PeachPuff").grid(row=16, column=0, columnspan=3)

        # Flag for rockcover
        Label(self.frame2, text='Flag for rockcover.txt:', font='Helvetica 25 bold').grid(row=17, column=0, pady=20)
        Label(self.frame2, text='Should be checked if the user provides a raster (rockcover.txt) that maps the rock cover fraction, unchecked means a fixed value equal to rockcoverfixed will be used.', font='Helvetica 20', justify=CENTER, wraplength=750).grid(row=17, column=2, pady=20)
        self.flagforrockcoverVar = IntVar(value=int(f.readline()))
        flagforrockcoverInput = Checkbutton(self.frame2, variable=self.flagforrockcoverVar, width=5, pady=20)
        flagforrockcoverInput.grid(row=17, column=1)
        # Should be 1 if the user provides a raster (rockcover.txt) that maps the rock cover fraction, 0 means a fixed value equal to rockcoverfixed will be used.

        Frame(self.frame2, width=self.frame2.winfo_screenwidth(), height=5, background="PeachPuff").grid(row=18, column=0, columnspan=3)

        # Fillincrement variable
        Label(self.frame2, text='fillincrement:', font='Helvetica 25 bold').grid(row=19, column=0, pady=20)
        Label(self.frame2, text='This value (in meters) is used to fill in pits and flats for hydrologic correction. 0.01 is a reasonable default value.', font='Helvetica 20',justify=CENTER, wraplength=750).grid(row=19, column=2, pady=20)
        fillincrementVar = StringVar(root, value=str(f.readline()))
        self.fillincrementInput = Entry(self.frame2, textvariable=fillincrementVar, width=5)
        self.fillincrementInput.grid(row=19, column=1, pady=20)
        # This value (in meters) is used to fill in pits and flats for hydrologic correction. 0.01 is a reasonable default value.

        Frame(self.frame2, width=self.frame2.winfo_screenwidth(), height=5, background="PeachPuff").grid(row=20, column=0, columnspan=3)
    
        # Threshslope variable
        Label(self.frame2, text='threshslope:', font='Helvetica 25 bold').grid(row=21, column=0, pady=20)
        Label(self.frame2, text='This value (unitless) is used to halt runoff from areas below a threshold slope steepness. Setting this value larger than 0 is useful for eliminating runoff from portions of the landscape that the user expects are too flat to produce significant runoff.', font='Helvetica 20', justify=CENTER, wraplength=750).grid(row=21, column=2, pady=20)
        threshslopeVar = StringVar(value=str(f.readline()))
        self.threshslopeInput = Entry(self.frame2, textvariable=threshslopeVar, width=5)
        self.threshslopeInput.grid(row=21, column=1, pady=20)
        # This value (unitless) is used to halt runoff from areas below a threshold slope steepness. Setting this value larger than 0 is useful for eliminating runoff from portions of the landscape that the user expects are too flat to produce significant runoff.

        Frame(self.frame2, width=self.frame2.winfo_screenwidth(), height=5, background="PeachPuff").grid(row=22, column=0, columnspan=3)

        # Expansion variable
        Label(self.frame2, text='expansion:', font='Helvetica 25 bold').grid(row=23, column=0, pady=20)
        Label(self.frame2, text='This value (in number of pixels) is used to expand the zones where rills are predicted in the output raster. This is useful for making the areas where rilling is predicted easier to see in the model output.', font='Helvetica 20',justify=CENTER, wraplength=750).grid(row=23, column=2, pady=20)
        expansionVar = StringVar(value=str(f.readline()))
        self.expansionInput = Entry(self.frame2, textvariable=expansionVar, width=5)
        self.expansionInput.grid(row=23, column=1, pady=20)
        # This value (in number of pixels) is used to expand the zones where rills are predicted in the output raster. This is useful for making the areas where rilling is predicted easier to see in the model output.

        Frame(self.frame2, width=self.frame2.winfo_screenwidth(), height=5, background="PeachPuff").grid(row=24, column=0, columnspan=3)
    
        # Yellowthreshold variable
        Label(self.frame2, text='yellowthreshold:', font='Helvetica 25 bold').grid(row=25, column=0, pady=20)
        Label(self.frame2, text='This is a threshold value of f used to indicate an area that is close to but less than the threshold for generating rills. The model will visualize any location with a f value between this value and\n1 as potentially prone to rill generation(any area with a f value larger than 1 is considered prone to rill generation and is colored red).', font='Helvetica 20',justify=CENTER, wraplength=750).grid(row=25, column=2, pady=20)
        yellowthresholdVar = StringVar(value=str(f.readline()))
        self.yellowthresholdInput = Entry(self.frame2, textvariable=yellowthresholdVar, width=5)
        self.yellowthresholdInput.grid(row=25, column=1, pady=20)
        # This is a threshold value of f used to indicate an area that is close to but less than the threshold for generating rills. The model will visualize any location with a f value between this value and 1 as potentially prone to rill generation (any area with a f value larger than 1 is considered prone to rill generation and is colored red)

        Frame(self.frame2, width=self.frame2.winfo_screenwidth(), height=5, background="PeachPuff").grid(row=26, column=0, columnspan=3)
    
        # Lattice_size_x variable
        Label(self.frame2, text='lattice_size_x:', font='Helvetica 25 bold').grid(row=27, column=0, pady=20)
        Label(self.frame2, text='The number of pixels along the east-west direction in the DEM.', font='Helvetica 20',justify=CENTER, wraplength=750).grid(row=27, column=2, pady=20)
        lattice_size_xVar = StringVar(value=self.dimensions[0])
        self.lattice_size_xInput = Entry(self.frame2, textvariable=lattice_size_xVar, width=5)
        self.lattice_size_xInput.grid(row=27, column=1, pady=20)
        self.lattice_size_xInput.config(state=DISABLED)
        # The number of pixels along the east-west direction in the DEM.

        Frame(self.frame2, width=self.frame2.winfo_screenwidth(), height=5, background="PeachPuff").grid(row=28, column=0, columnspan=3)

        # Lattice_size_y variable
        Label(self.frame2, text='lattice_size_y:', font='Helvetica 25 bold').grid(row=29, column=0, pady=20)
        Label(self.frame2, text='The number of pixels along the east-west direction in the DEM.', font='Helvetica 20', justify=CENTER, wraplength=750).grid(row=29, column=2, pady=20)
        lattice_size_yVar = StringVar(value=self.dimensions[1])
        self.lattice_size_yInput = Entry(self.frame2, textvariable=lattice_size_yVar, width=5)
        self.lattice_size_yInput.grid(row=29, column=1, pady=20)
        self.lattice_size_yInput.config(state=DISABLED)
        # The number of pixels along the east-west direction in the DEM.

        Frame(self.frame2, width=self.frame2.winfo_screenwidth(), height=5, background="PeachPuff").grid(row=30, column=0, columnspan=3)
        f.readline() # We do not want to read in the previous lattice_x and lattice_y
        f.readline() # Since they came from another geotiff file
  
        # Deltax variable
        Label(self.frame2, text='deltax:', font='Helvetica 25 bold').grid(row=31, column=0, pady=20)
        Label(self.frame2, text='The resolution (in meters/pixel) of the DEM and additional optional raster inputs.', font='Helvetica 20', justify=CENTER, wraplength=750).grid(row=31, column=2, pady=20)
        deltaxVar = StringVar(value=str(f.readline()))
        self.deltaxInput = Entry(self.frame2, textvariable=deltaxVar, width=5)
        self.deltaxInput.grid(row=31, column=1, pady=20)
        # The resolution (in meters/pixel) of the DEM and additional optional raster inputs.

        Frame(self.frame2, width=self.frame2.winfo_screenwidth(), height=5, background="PeachPuff").grid(row=32, column=0, columnspan=3)

        # Rain fixed variable
        Label(self.frame2, text='rain fixed:', font='Helvetica 25 bold').grid(row=33, column=0, pady=20)
        Label(self.frame2, text='Peak 5 minute rainfall intensity (in mm/hr).', font='Helvetica 20', justify=CENTER, wraplength=750).grid(row=33, column=2, pady=20)
        rainVar = StringVar(value=str(f.readline()))
        self.rainInput = Entry(self.frame2, textvariable=rainVar, width=5)
        self.rainInput.grid(row=33, column=1, pady=20)
        # Peak 5 minute rainfall intensity (in mm/hr)

        Frame(self.frame2, width=self.frame2.winfo_screenwidth(), height=5, background="PeachPuff").grid(row=34, column=0, columnspan=3)

        # tauc soil and vege fixed variable
        Label(self.frame2, text='tauc soil and vege fixed:', font='Helvetica 25 bold').grid(row=35, column=0, pady=20)
        Label(self.frame2, text='TauC for soil and vegetation. This value is ignored if flag for tauc soil and vege is checked.', font='Helvetica 20',justify=CENTER, wraplength=750).grid(row=35, column=2, pady=20)
        taucsoilandvegeVar = StringVar(value=str(f.readline()))
        self.taucsoilandvegeInput = Entry(self.frame2, textvariable=taucsoilandvegeVar, width=5)
        self.taucsoilandvegeInput.grid(row=35, column=1, pady=20)

        Frame(self.frame2, width=self.frame2.winfo_screenwidth(), height=5, background="PeachPuff").grid(row=36, column=0, columnspan=3)

        # d50 fixed variable
        Label(self.frame2, text='d50 fixed:', font='Helvetica 25 bold').grid(row=37, column=0, pady=20)
        Label(self.frame2, text='Effective infiltration rate (in mm/hr). This value is ignored if flag for d50 is checked.', font='Helvetica 20',justify=CENTER, wraplength=750).grid(row=37, column=2, pady=20)
        d50Var = StringVar(value=str(f.readline()))
        self.d50Input = Entry(self.frame2, textvariable=d50Var, width=5)
        self.d50Input.grid(row=37, column=1, pady=20)
        # Median rock armor diameter (in mm). This value is ignored if flagford50=1.

        Frame(self.frame2, width=self.frame2.winfo_screenwidth(), height=5, background="PeachPuff").grid(row=38, column=0, columnspan=3)

        # Coefficient of uniformity fixed variable
        Label(self.frame2, text='cu:', font='Helvetica 25 bold').grid(row=39, column=0, pady=20)
        Label(self.frame2, text='Median rock armor diameter (in mm). This value is ignored if flag for cu is checked, or if d50 or thickness equals 0.', font='Helvetica 20', justify=CENTER, wraplength=750).grid(row=39, column=2, pady=20)
        cuVar = StringVar(value=str(f.readline()))
        self.cuInput = Entry(self.frame2, textvariable=cuVar, width=5)
        self.cuInput.grid(row=39, column=1, pady=20)
        # Cofficient of uniformity (unitless) of the rock armor. This value is ignored if flagforcu=1 or if d50 or thickness equals 0.

        Frame(self.frame2, width=self.frame2.winfo_screenwidth(), height=5, background="PeachPuff").grid(row=40, column=0, columnspan=3)

        # Thickness fixed variable
        Label(self.frame2, text='thickness:', font='Helvetica 25 bold').grid(row=41, column=0, pady=20)
        Label(self.frame2, text='The thickness of the rock armor layer in multiples of the median grain diameter. For example, if d50 is 10 cm and the rock armor is 30 cm thick then this value should be 3. This value is ignored if flag for thickness is checked.', font='Helvetica 20',justify=CENTER, wraplength=750).grid(row=41, column=2, pady=20)
        thicknessVar = StringVar(value=str(f.readline()))
        self.thicknessInput = Entry(self.frame2, textvariable=thicknessVar, width=5)
        self.thicknessInput.grid(row=41, column=1, pady=20)
        # The thickness of the rock armor layer in multiples of the median grain diameter. For example, if d50 is 10 cm and the rock armor is 30 cm thick then this value should be 3. This value is ignored if flagforthickness=1.

        Frame(self.frame2, width=self.frame2.winfo_screenwidth(), height=5, background="PeachPuff").grid(row=42, column=0, columnspan=3)

        # Rockcover fixed variable
        Label(self.frame2, text='rockcover:', font='Helvetica 25 bold').grid(row=43, column=0, pady=20)
        Label(self.frame2, text='This value indicates the fraction of area covered by rock armor. Will be 1 for continuous rock armors, less than one for partial rock cover. This value is ignored if flag for rockcover is checked.', font='Helvetica 20',justify=CENTER, wraplength=750).grid(row=43, column=2, pady=20)
        rockcoverVar = StringVar(value=str(f.readline()))
        self.rockcoverInput = Entry(self.frame2, textvariable=rockcoverVar, width=5)
        self.rockcoverInput.grid(row=43, column=1, pady=20)
        # This value indicates the fraction of area covered by rock armor. Will be 1 for continuous rock armors, less than one for partial rock cover. This value is ignored if flagforrockcover=1.

        Frame(self.frame2, width=self.frame2.winfo_screenwidth(), height=5, background="PeachPuff").grid(row=44, column=0, columnspan=3)

        # Rockcover fixed variable
        Label(self.frame2, text='tanangleofinternalfriction:', font='Helvetica 25 bold').grid(row=45, column=0, pady=20)
        Label(self.frame2, text='Tangent of the angle of internal friction. Values will typically be in the range of 0.6-1.', font='Helvetica 20',justify=CENTER, wraplength=750).grid(row=45, column=2, pady=20)
        tanangleofinternalfrictionVar = StringVar(value=str(f.readline()))
        self.tanangleofinternalfrictionInput = Entry(self.frame2, textvariable=tanangleofinternalfrictionVar, width=5)
        self.tanangleofinternalfrictionInput.grid(row=45, column=1, pady=20)
        # This value indicates the fraction of area covered by rock armor. Will be 1 for continuous rock armors, less than one for partial rock cover. This value is ignored if flagforrockcover=1.

        Frame(self.frame2, width=self.frame2.winfo_screenwidth(), height=5, background="PeachPuff").grid(row=46, column=0, columnspan=3)

        # Reducedspecificgravity variable
        Label(self.frame2, text='reducedspecificgravity:', font='Helvetica 25 bold').grid(row=47, column=0, pady=20)
        Label(self.frame2, text='Reduced specific gravity of the rock armor particles. 1.65 is a reasonable default value for quartz-rich rocks.', font='Helvetica 20', justify=CENTER, wraplength=750).grid(row=47, column=2, pady=20)
        reducedspecificgravityVar = StringVar(value=str(f.readline()))
        self.reducedspecificgravityInput = Entry(self.frame2, textvariable=reducedspecificgravityVar, width=5)
        self.reducedspecificgravityInput.grid(row=47, column=1, pady=20)
        # Reduced specific gravity of the rock armor particles. 1.65 is a reasonable default value for quartz-rich rocks.

        Frame(self.frame2, width=self.frame2.winfo_screenwidth(), height=5, background="PeachPuff").grid(row=48, column=0, columnspan=3)

        # b variable
        Label(self.frame2, text='b:', font='Helvetica 25 bold').grid(row=49, column=0, pady=20)
        Label(self.frame2, text='This value is the coefficient in the model component that predicts the relationship between runoff and contributing area.', font='Helvetica 20',justify=CENTER, wraplength=750).grid(row=49, column=2, pady=20)
        bVar = StringVar(value=str(f.readline()))
        self.bInput = Entry(self.frame2, textvariable=bVar, width=5)
        self.bInput.grid(row=49, column=1, pady=20)
        # This value is the coefficient in the model component that predicts the relationship between runoff and contributing area.

        Frame(self.frame2, width=self.frame2.winfo_screenwidth(), height=5, background="PeachPuff").grid(row=50, column=0, columnspan=3)

        # c variable
        Label(self.frame2, text='c:', font='Helvetica 25 bold').grid(row=51, column=0, pady=20)
        Label(self.frame2, text='This value is the exponent in the model component that predicts the relationship between runoff and contributing area.', font='Helvetica 20', justify=CENTER, wraplength=750).grid(row=51, column=2, pady=20)
        cVar = StringVar(value=str(f.readline()))
        self.cInput = Entry(self.frame2, textvariable=cVar, width=5)
        self.cInput.grid(row=51, column=1, pady=20)
        # This value is the exponent in the model component that predicts the relationship between runoff and contributing area.

        Frame(self.frame2, width=self.frame2.winfo_screenwidth(), height=5, background="PeachPuff").grid(row=52, column=0, columnspan=3)

        # Rillwidth variable
        Label(self.frame2, text='rillwidth:', font='Helvetica 25 bold').grid(row=53, column=0, pady=20)
        Label(self.frame2, text='The width of rills (in m) as they begin to form. This value is used to localize water flow to a width less than the width of a pixel. For example, if deltax = 1 m and rillwidth = 20 cm then the flow entering each pixel is assumed, for the purposes of rill development, to be localized in a width equal to one fifth of the pixel width.', font='Helvetica 20', justify=CENTER, wraplength=750).grid(row=53, column=2, pady=20)
        rillwidthVar = StringVar(value=str(f.readline()))
        self.rillwidthInput = Entry(self.frame2, textvariable=rillwidthVar, width=5)
        self.rillwidthInput.grid(row=53, column=1, pady=20)

        Frame(self.frame2, width=self.frame2.winfo_screenwidth(), height=5, background="PeachPuff").grid(row=54, column=0, columnspan=3)

        self.first_time_populating_parameters_tab = False
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


    def generate_parameters(self):
        """Generate the parameters.txt file using the flags from the second tab"""

        if os.path.isfile('parameters.txt'):
            os.remove('parameters.txt')
        f = open('parameters.txt', 'w+')
        f.write(str(self.flagformaskVar.get()) + '\t /* Flag for mask out */ \n')
        f.write(str(self.flagforslopeVar.get())+ '\t /* Flag for slope out */ \n')
        f.write(str(self.flagforRainVar.get()) + '\t /* Flag for rain out */ \n')
        f.write(str(self.flagfortaucsoilandvegVar.get()) + '\t /* Flag for taucsoilandveg out */ \n')
        f.write(str(self.flagford50Var.get()) + '\t /* Flag for d50 out */ \n')
        f.write(str(self.flagforcuVar.get()) + '\t /* Flag for cu out */ \n')
        f.write(str(self.flagforthicknessVar.get()) + '\t /* Flag for thickness out */ \n')
        f.write(str(self.flagforrockcoverVar.get()) + '\t /* Flag for rockcover out */ \n')
        f.write(self.fillincrementInput.get().replace("\n", "") + '\t /* Fillincrement out */ \n')
        f.write(self.threshslopeInput.get().replace("\n", "") + '\t /* Threshslope out */ \n')
        f.write(self.expansionInput.get().replace("\n", "") + '\t /* Expansion out */ \n')
        f.write(self.yellowthresholdInput.get().replace("\n", "") + '\t /* Yellow threshold out */ \n')
        f.write(self.lattice_size_xInput.get().replace("\n", "") + '\t /* Lattice Size X out */ \n')
        f.write(self.lattice_size_yInput.get().replace("\n", "") + '\t /* Lattice Size Y out */ \n')
        f.write(self.deltaxInput.get().replace("\n", "") + '\t /* Delta X out */ \n')
        f.write(self.rainInput.get().replace("\n", "") + '\t /* Rain out */ \n')
        f.write(self.taucsoilandvegeInput.get().replace("\n", "") + '\t /* tauc soil and vege out */ \n')
        f.write(self.d50Input.get().replace("\n", "") + '\t /* d50 out */ \n')
        f.write(self.cuInput.get().replace("\n", "") + '\t /* cu out */ \n')
        f.write(self.thicknessInput.get().replace("\n", "") + '\t /* thickness out */ \n')
        f.write(self.rockcoverInput.get().replace("\n", "") + '\t /* rock cover out */ \n')
        f.write(self.tanangleofinternalfrictionInput.get().replace("\n", "") + '\t /* tangent of the angle of internal friction out*/ \n')
        f.write(self.reducedspecificgravityInput.get().replace("\n", "") + '\t /* reduced specific gravity out */ \n')
        f.write(self.bInput.get().replace("\n", "") + '\t /* b out */ \n')
        f.write(self.cInput.get().replace("\n", "") + '\t /* c out */ \n')
        f.write(self.rillwidthInput.get().replace("\n", "") + '\t /* rill width out */ \n')

    
    def generate_input_txt_file(self):
        """Generate the input.txt file using the flags from the second tab.
        
        There are then helper functions, the first of which runs the rillgen.c script
        in order to create xy_f.txt and xy_tau.txt

        The second helper function then sets the georeferencing information from the original
        geotiff file to xy_f.txt and xy_tau.txt in order to generate f.tif and tau.tif"""

        if os.path.isfile('input.txt'):
            os.remove('input.txt')
        f = open('input.txt', 'w')
        f.write(str(self.flagformaskVar.get())+'\n') 
        f.write(str(self.flagforslopeVar.get())+'\n')
        f.write(str(self.flagforRainVar.get())+'\n')
        f.write(str(self.flagfortaucsoilandvegVar.get())+'\n')
        f.write(str(self.flagford50Var.get())+'\n')
        f.write(str(self.flagforcuVar.get())+'\n')
        f.write(str(self.flagforthicknessVar.get())+'\n')
        f.write(str(self.flagforrockcoverVar.get())+'\n')
        f.write(self.fillincrementInput.get().replace("\n", "")+'\n')
        f.write(self.threshslopeInput.get().replace("\n", "")+'\n')
        f.write(self.expansionInput.get().replace("\n", "")+'\n')
        f.write(self.yellowthresholdInput.get().replace("\n", "")+'\n')
        f.write(self.lattice_size_xInput.get().replace("\n", "")+'\n')
        f.write(self.lattice_size_yInput.get().replace("\n", "")+'\n')
        f.write(self.deltaxInput.get().replace("\n", "")+'\n')
        f.write(self.rainInput.get().replace("\n", "")+'\n')
        f.write(self.taucsoilandvegeInput.get().replace("\n", "")+'\n')
        f.write(self.d50Input.get().replace("\n", "")+'\n')
        f.write(self.cuInput.get().replace("\n", "")+'\n')
        f.write(self.thicknessInput.get().replace("\n", "")+'\n')
        f.write(self.rockcoverInput.get().replace("\n", "")+'\n')
        f.write(self.tanangleofinternalfrictionInput.get().replace("\n", "")+'\n')
        f.write(self.reducedspecificgravityInput.get().replace("\n", "")+'\n')
        f.write(self.bInput.get().replace("\n", "")+'\n')
        f.write(self.cInput.get().replace("\n", "")+'\n')
        f.write(self.rillwidthInput.get().replace("\n", "")+'\n')
        f.close()
        
        t1 = Thread(target=self.hillshade_and_color_relief)
        # t2 = Thread(target=self.run_rillgen)
        t1.start()
        self.run_rillgen()
        # t2.start()
        if self.first_time_populating_view_output_tab:
            self.tabControl.add(self.tab3, text="View Output")
            self.populate_view_output_tab()
        t1.join()
        # t2.join()
        self.set_georeferencing_information(self.filename)

    
    def hillshade_and_color_relief(self):
        """Generates the hillshade and color-relief images from the original 
        geotiff image that will be available on the map"""
        cmd0 = "gdaldem hillshade " + self.filename + " hillshade.png"
        os.system(cmd0)
        # self.formatColorRelief(self.filename)
        gtif = gdal.Open(self.filename)
        srcband = gtif.GetRasterBand(1)
        # Get raster statistics
        stats = srcband.GetStatistics(True, True)
        # Print the min, max, mean, stdev based on stats index
        f = open('color-relief.txt', 'w')
        f.writelines([str(stats[0]) + " 110 220 110\n", str(stats[2]-stats[3]) + " 240 250 160\n", str(stats[2]) + " 230 220 170\n", str(stats[2]+stats[3]) + " 220 220 220\n", str(stats[1]) + " 250 250 250\n"])
        f.close()
        cmd1 = "gdaldem color-relief " + self.filename + " color-relief.txt color-relief.png"
        os.system(cmd1)

    def make_popup(self):
        self.popup = tk.Toplevel(root)
        popupLabel = tk.Label(self.popup, text="hydrologic correction step in progress")
        # popupLabel.grid(row=0, column=0)
        popupLabel.pack(side=tk.TOP)
        self.progress_bar = ttk.Progressbar(self.popup, orient=HORIZONTAL, length=300, mode='determinate', maximum=100)
        # progress_bar.grid(row=1, column=0)
        self.progress_bar.pack(fill=tk.X, expand=1, side=tk.BOTTOM)
        root.update()

    def update_progressbar(self, value):
        self.progress_bar['value'] = value
        root.update()

    def run_rillgen(self):
        self.make_popup()
        cmd0 = "awk '{print $3}' output_tin.asc > topo.txt"
        os.system(cmd0)
        self.update_progressbar(10)
        cmd1 = "awk '{print $1, $2}' output_tin.asc > xy.txt"
        os.system(cmd1)
        self.update_progressbar(20)
        # cmd2 = "docker run -it -v ${PWD}:/data 485urjnste8rdf/rillgen2d:experimental"
        # os.system(cmd2)
        cmd2 = "gcc ../rillgen2d.c"
        os.system(cmd2)
        self.update_progressbar(40)
        cmd3 = "../rillgen2d"
        os.system(cmd3)
        self.update_progressbar(80)
        cmd4 = "paste xy.txt tau.txt > xy_tau.txt"
        os.system(cmd4)
        self.update_progressbar(90)
        cmd5 = "paste xy.txt f.txt > xy_f.txt"
        returned_value = os.system(cmd5)
        self.update_progressbar(100)
        print('returned value:', returned_value)
        self.popup.destroy()


    def set_georeferencing_information(self, dem):
        ds = gdal.Open(dem)

        if ds is None:
            print('Unable to open', str(dem), 'for reading')
            sys.exit(1)
        
        projection = osr.SpatialReference(wkt=ds.GetProjection())
        if int(osgeo.__version__[0]) >= 3:
            # GDAL 3 changes axis order: https://github.com/OSGeo/gdal/issues/1546
            # pylint: disable=no-member
            projection.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
        # proj = osr.SpatialReference(wkt=ds.GetProjection()).GetAttrValue('AUTHORITY',1)
        proj = projection.GetAttrValue('AUTHORITY',1)
        
        cmd0 = "gdal_translate -a_srs EPSG:" + str(proj) + " xy_tau.txt tau.tif"
        os.system(cmd0)
        cmd1 = "gdal_translate -a_srs EPSG:" + str(proj) + " xy_f.txt f.tif"
        os.system(cmd1)

        projection = ds.GetProjection()
        geotransform = ds.GetGeoTransform()

        if projection is None and geotransform is None:
            print('No projection or geotransform found on file' + str(self.filename))
            sys.exit(1)

        for elem in ["tau.tif", "f.tif"]:
            ds2 = gdal.Open(elem, gdal.GA_Update)
            if ds2 is None:
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
                cmd2 = "gdal_translate -ot Byte -of PNG " + elem.split(sep='.')[0] + ".tif " + elem.split(sep='.')[0] + ".png"
            else:
                cmd2 = "gdal_translate -ot Byte -scale 0 0.1 -of PNG " + elem.split(sep='.')[0] + ".tif " + elem.split(sep='.')[0] + ".png"
            returned_value = os.system(cmd2)
            print('returned value:', returned_value)

            ds2 = None
        ds = None

    
    def populate_view_output_tab(self):
        """Populate the third tab with tkinter widgets. The third tab allows
        the user to generate a folium map based on the rillgen output"""
        self.prompt = Label(self.tab3, text='Here you can generate a leaflet map based on the file chosen in tab 1', font='Helvetica 40 bold', justify=CENTER, wraplength=500)
        self.prompt.grid(row=0, column=0)
        self.button1 = ttk.Button(self.tab3, text="Generate Map", command=self.generatemap)
        self.button1.grid(row=1, column=0)

        self.img3 = Label(self.tab3)
        self.fig3 = Figure(figsize=(5, 5), dpi=100)

        self.canvas3 = FigureCanvasTkAgg(self.fig3, master=self.img3)
        self.canvas3.draw()

        self.canvas3.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1, padx=0, pady=0)

        self.canvas3._tkcanvas.pack(side=TOP, fill=BOTH, expand=1, padx=0, pady=0)

        self.img3.grid(row=0, column=1, rowspan=2, sticky=N+S+E+W)

        self.tab3.columnconfigure(0, weight=3)
        self.tab3.columnconfigure(1, weight=1)
        self.tab3.rowconfigure(0,weight=1)
        self.tab3.rowconfigure(1,weight=1)
        self.first_time_populating_view_output_tab = False


    def generatemap(self):
        """Generates a folium map based on the bounds of the geotiff file"""
        if self.filename != None and os.path.isfile(self.filename):
            GdalInfo = subprocess.check_output('gdalinfo {}'.format(self.filename), shell=True)
            GdalInfo = str(GdalInfo)
            GdalInfo = GdalInfo.split(r'\n')
            location = []
            location_ll = []
            location_ur = []
            for line in GdalInfo:
                if line[:6] == 'Center':
                    location = self.GetLatLon(line)
                if line[:10] == 'Lower Left':
                    location_ll = self.GetLatLon(line)
                if line[:11] == 'Upper Right':
                    location_ur = self.GetLatLon(line)
            m = folium.Map(location, zoom_start=14, tiles='Stamen Terrain')
            img1 = folium.raster_layers.ImageOverlay(image="tau.png", bounds=[location_ll,location_ur], opacity=0.8, interactive=True, name="tau")
            img2 = folium.raster_layers.ImageOverlay(image="hillshade.png", bounds=[location_ll,location_ur], opacity=0.6, interactive=True, name="hillshade")
            img3 = folium.raster_layers.ImageOverlay(image="color-relief.png", bounds=[location_ll,location_ur], opacity=0.4, interactive=True, name="color-relief")
            img4 = folium.raster_layers.ImageOverlay(image="f.png", bounds=[location_ll,location_ur], opacity=0.8, interactive=True, show=False, name="f")
            img1.add_to(m)
            img2.add_to(m)
            img3.add_to(m)
            img4.add_to(m)
            folium.LayerControl().add_to(m)
            m.save("map.html", close_file=True)
            t1 = Thread(target=self.saveOutput)
            t1.start()
            self.displayMap()
            
        else: 
            messagebox.showerror(title="FILE NOT FOUND", message="Please select a file in tab 1")

    def saveOutput(self):
        saveDir = "../outputs(save-" + str(datetime.now()).replace(" ", "") + ")"
        os.mkdir(saveDir)
        src_files = os.listdir(os.getcwd())
        acceptable_files = [self.filename, "parameters.txt", "input.txt", "map.html", "rills.ppm"]
        for file_name in src_files:
            if file_name in acceptable_files or (file_name.endswith(".png") or file_name.endswith(".tif")):
                shutil.copy(file_name, saveDir + "/" + file_name)

    def GetLatLon(self, line):
        """Gets the latitude and longitude coordinates of a corner or center of the geotiff file
        (whichever is specified) using gdalinfo"""
        coords = line.split(') (')[1]
        coords = coords[:-1]
        LonStr, LatStr = coords.split(',')
        # Longitude
        LonStr = LonStr.split('d')    # Get the degrees, and the rest
        LonD = int(LonStr[0])
        LonStr = LonStr[1].split(r'\'')# Get the arc-m, and the rest
        LonM = int(LonStr[0])
        LonStr = LonStr[1].split('"') # Get the arc-s, and the rest
        LonS = float(LonStr[0])
        Lon = LonD + LonM/60. + LonS/3600.
        if LonStr[1] in ['W', 'w']:
            Lon = -1*Lon
        # Same for Latitude
        LatStr = LatStr.split('d')
        LatD = int(LatStr[0])
        LatStr = LatStr[1].split(r'\'')
        LatM = int(LatStr[0])
        LatStr = LatStr[1].split('"')
        LatS = float(LatStr[0])
        Lat = LatD + LatM/60. + LatS/3600.
        if LatStr[1] in ['S', 's']:
            Lat = -1*Lat
        return [Lat, Lon]

    
    def displayMap(self):
        mapfile = QtCore.QUrl.fromLocalFile(os.path.abspath("map.html"))
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
        

if __name__ == "__main__":
    root=tk.Tk()
    root.resizable(True, True)
    root.title("rillgen2D")
    if os.path.isfile('template_input.txt'):
        example = Application(root)
        example.pack(side="top", fill="both", expand=True)
        root.mainloop()
    else:
        raise Exception("A file with the name template_input.txt was not found.")