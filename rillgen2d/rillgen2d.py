from __future__ import annotations

from wand.image import Image as im
from multiprocessing import Process, Queue
from threading import Thread, current_thread
from pathlib import Path
from osgeo import gdal, osr
from datetime import datetime
from ctypes import CDLL
import branca
import os

import subprocess
import shutil
import folium
import osgeo
import PIL

import typing


# Apparently this API   is supposed to be internal atm and seems to rapidly change without documentation between upadtes
PIL.Image.MAX_IMAGE_PIXELS = 933120000
# multiprocessing might be good instead, depedning on the function


def function_decorator(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(e)
            raise e
    return wrapper


class Rillgen2d(Process):
    """
        Context manager for changing directories. Useful abstracting away tracking the current directory.
    """
    
    def __init__(self, params, message_queue : Queue):
        self.console = message_queue
        self.params = params

        # params stores the filepath, but wont have it at the time of initialization
        self.image_path : str = None
        self.filename : str = None
        self.geo_ext = None  # used to get corner coordinates for the projection
        self.dimensions = None  # These are the dimensions of the input file that the user chooses
        self.img1 = None
        self.rillgen = None  # Used to import the rillgen.c code
        # Tracking threads in case of exceptions so we can join them before ending the program
        self.threads = []
        self.temporary_directory = Path(__file__).parents[1] / "tmp"
        # Call the Thread constructor
        Process.__init__(self)
    
    """ 
        In all of the functions, we want to log the error to the console then re-raise it
        so, we are just using a function to simplify the process
    """
    def hillshade_and_color_relief(self):
        """
            Generates the hillshade and color-relief images from the original 
            geotiff image that will be available on the map
        """
        
        self.console.put("Generating hillshade and color relief...")
        self.run_command(f"gdaldem hillshade '{self.filename}' {self.temporary_directory}/hillshade.png")
        return self.temporary_directory / "hillshade.png"
    
    @function_decorator
    def update_image_path(self):
        self.image_path = self.params.image_path
        self.filename = str(Path.cwd() / Path(self.params.image_path).name)

    @function_decorator
    def run_command(self, command):
        self.console.put(command)
        a =  str(subprocess.check_output(command, shell=True), "UTF-8")
        print(a)
        self.console.put(a)
    
    @function_decorator
    def convert_geotiff_to_txt(self, filename):
        self.console.put("Converting geotiff to txt")
        src_ds = gdal.Open(filename + ".tif")
        if src_ds is None:
            raise Exception(
                "ERROR: Unable to open " +filename + " for writing")
        # Open output format driver, see gdal_translate --formats for list
        format = "XYZ"
        driver = gdal.GetDriverByName(format)
    
        # Output to new format
        dst_ds = driver.CreateCopy(filename + "_dem.asc", src_ds, 0)
    
        # Properly close the datasets to flush to disk
        src_ds = None
        dst_ds = None
        self.run_command("gdal_translate -of XYZ " + filename + ".tif " + filename + ".asc")
        self.run_command("awk '{print $3}' " + filename + ".asc > " + filename + ".txt")
        # remove temporary .asc file to save space
        self.run_command("rm " + filename + "_dem.asc")
    
    
    def run(self):
        self.image_path = self.params.image_path
        os.chdir(self.temporary_directory)
        self.convert_geotiff_to_txt(Path(self.image_path).stem)
        self.setup_rillgen()
        self.set_georeferencing_information()
        self.generate_map()

    @function_decorator
    def generate_color_ramp(self, filename, colormap_name, caption):
        """generates a color ramp from a geotiff image and then uses that in order to produce
        a color-relief for the geotiff"""
        self.console.put("Generating color ramp")
        gtif = gdal.Open(filename)
        srcband = gtif.GetRasterBand(1)

        # Get raster statistics
        stats = srcband.GetStatistics(True, True)

        
        #TODO: figure out what this is supposed to do so I can clarify it
        if caption.startswith("Tau") and stats[1] > 100:
            stats[1] = 100
            if stats[2] > 50:
                stats[2] = 50
        
        index_array = [
            stats[0], 
            stats[0]+(stats[2]-stats[0])/4,
            stats[0]+(stats[2]-stats[0])/2,
            stats[0]+3*(stats[2]-stats[0])/4,
            stats[2],
            stats[2]+(stats[1]-stats[2])/4,
            stats[2]+(stats[1]-stats[2])/2, 
            stats[2]+3*(stats[1]-stats[2])/4, 
            stats[1]
        ]
        colors = [
            (0, 0, 0),
            (167, 30, 66),
            (51, 69, 131),
            (101, 94, 190), 
            (130, 125, 253), 
            (159, 158, 128), 
            (193, 192, 16),
            (224, 222, 137), 
            (255, 255, 255)
        ]
        f = open('color-relief.txt', 'w')
        for i in range(len(index_array)):
            # Making a line in the format "index, r, g, b\n"
            line = ", ".join(map(str, (index_array[i], *colors[i]))) + "\n"
            f.write(line)
        f.close()
        colormap = branca.colormap.LinearColormap(colors).to_step(index=index_array)
        colormap.caption =caption 
        setattr(self, colormap_name, colormap)
        self.run_command(f"gdaldem color-relief \"{filename}\" color-relief.txt color-relief_{Path(filename).stem}.png")

        self.console.put("Hillshade and color relief generated")
        gtif = None

    @function_decorator
    def setup_rillgen(self):
        """Sets up files for the rillgen.c code by creating topo.txt and xy.txt, and
        imports the rillgen.c code using the CDLL library"""
        self.run_command(f"gcc -Wall -shared -fPIC {Path(__file__).parent}/rillgen2d.c -o {self.temporary_directory}/rillgen.so")
        self.rillgen = CDLL( self.temporary_directory / 'rillgen.so') 
        self.console.put("Setting up Rillgen")
        mode = 1
        self.console.put("Hydroilic correction step in progress")
        self.run_command(
            "awk '{print $3}' " + self.image_path.stem + ".asc > topo.txt"
        )
        self.run_command(
            "awk '{print $1, $2}' " + self.image_path.stem + ".asc > xy.txt"
        )
        t1 = self.add_thread(self.run_rillgen)
        t1.join()
        self.console.put("Hydrologic correction step completed. Creating outputs...")
    
    @function_decorator
    def run_rillgen(self):
        """Runs the rillgen.c library using the CDLL module"""
        self.console.put("Running Rillgen")
        self.rillgen.main()
        self.run_command("paste xy.txt tau.txt > xy_tau.txt")
        self.run_command("paste xy.txt f1.txt > xy_f1.txt")
        self.run_command("paste xy.txt f2.txt > xy_f2.txt")
    
    @function_decorator
    def add_thread(self, function, *args, **kwargs):
        thread = Thread(target=function, args=args,kwargs=kwargs)
        self.threads.append(thread)
        thread.start()
        return thread

    @function_decorator
    def set_georeferencing_information(self):
        """Sets the georeferencing information for f.tif and tau.tif (and incised depth.t if self.flagForDynamicVar==1) to be the same as that
        from the original geotiff file"""
        self.console.put("Setting georeferencing information")

        # Throwing an exception for the Frontend to handle
        if not self.filename or not Path(self.filename).exists():
            raise FileNotFoundError("No file selected")
        ds = gdal.Open(self.filename)
        gt = ds.GetGeoTransform()
        cols = ds.RasterXSize
        rows = ds.RasterYSize
        ext = self.GetExtent(gt, cols, rows)
        src_srs = osr.SpatialReference()
        if int(osgeo.__version__[0]) >= 3:
            # GDAL 3 changes axis order: https://github.com/OSGeo/gdal/issues/1546
            src_srs.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
        proj = ds.GetProjection()
        src_srs.ImportFromWkt(proj)
        tgt_srs = src_srs.CloneGeogCS()

        self.geo_ext = self.ReprojectCoords(ext, src_srs, tgt_srs)
        
        self.run_command("gdal_translate xy_tau.txt tau.tif")
        t1 = self.add_thread(self.generate_color_ramp, "tau.tif", "tau_colormap", "Tau (Pascals)")
        
        self.run_command("gdal_translate xy_f1.txt f1.tif")
        t2 = self.add_thread(self.generate_color_ramp, "f1.tif", "f1_colormap", "F1 (Pascals)" )
        self.run_command("gdal_translate xy_f2.txt f2.tif")
        t3 = self.add_thread(self.generate_color_ramp, "f2.tif", "f2_colormap", "F2 (Pascals)")
    
        projection = ds.GetProjection()
        geotransform = ds.GetGeoTransform()

        if projection is None and geotransform is None:
            raise FileNotFoundError("No projection or geotransform found on file" + str(self.filename))

        for elem in ["tau.tif", "f1.tif","f2.tif", "inciseddepth.tif"]:
            if not (Path.cwd() / elem).exists():
                continue
            
            ds2 = gdal.Open(elem, gdal.GA_Update)
            if ds2 is None:
                raise PermissionError(f"Unable to open {elem} for writing")

            if geotransform is not None and geotransform != (0, 1, 0, 0, 0, 1):
                ds2.SetGeoTransform(geotransform)

            if projection is not None and projection != '':
                ds2.SetProjection(projection)

            gcp_count = ds.GetGCPCount()
            if gcp_count != 0:
                ds2.SetGCPs(ds.GetGCPs(), ds.GetGCPProjection())
            file_base = elem.split(sep='.')[0]
            if elem.startswith("f"):
                command_base = "gdal_translate -a_nodata 255 -ot Byte -scale 0 0.1 -of PNG "
            else:
                command_base = "gdal_translate -a_nodata 255 -ot Byte -of PNG "
            self.console.put(f"Translating {elem} to .png")
            self.run_command(command_base + file_base+ ".tif " + file_base + ".png")
            ds2 = None

        
        ds = None
        t1.join()
        t2.join()
        t3.join()
        self.console.put("Georeferencing complete")
        self.convert_ppm()
        self.console.put("Model Output Successfully Created")
        self.console.put("Click on View Outputs Tab")

    @function_decorator
    def convert_ppm(self):
        """Convert the rills.ppm file to png so that it can be displayed on the map"""
        # Note, the ppm is encoded in P3 format, so we need to use wand to actually convert it to the P6 format
        if not Path("rills.ppm").exists():
            self.console.put("Unable to open rills.ppm for writing")
        else:
            self.console.put("Translating rills.ppm to .png")
            with im(filename="rills.ppm") as img:
                img.save(filename="P6.ppm")
            cmd = "gdal_translate -of PNG -a_nodata 255 P6.ppm rills.png"
            self.run_command(cmd)
    
    @function_decorator
    def GetExtent(self, gt, cols, rows):
        """Return list of corner coordinates from a geotransform given the number
        of columns and the number of rows in the dataset"""
        ext = []
        xarr = [0, cols]
        yarr = [0, rows]

        for px in xarr:
            for py in yarr:
                x = gt[0]+(px*gt[1])+(py*gt[2])
                y = gt[3]+(px*gt[4])+(py*gt[5])
                ext.append([x, y])
            yarr.reverse()
        return ext
    
    @function_decorator
    def ReprojectCoords(self, coords, src_srs, tgt_srs):
        """Reproject a list of x,y coordinates. From srs_srs to tgt_srs"""
        trans_coords = []
        transform = osr.CoordinateTransformation(src_srs, tgt_srs)
        for x, y in coords:
            x, y, z = transform.TransformPoint(x, y)
            trans_coords.append([x, y])
        return trans_coords
    
    @function_decorator
    def generate_map(self):
        """Generate Leaflet Folium Map"""

        map_bounds = [[self.geo_ext[1][1], self.geo_ext[1][0]],
                      [self.geo_ext[3][1], self.geo_ext[3][0]]]
        self.m = folium.Map(location=[(self.geo_ext[1][1]+self.geo_ext[3][1])/2,
                                      (self.geo_ext[1][0]+self.geo_ext[3][0])/2], zoom_start=14, tiles='Stamen Terrain')
        folium.TileLayer('OpenStreetMap').add_to(self.m)
        folium.TileLayer('Stamen Toner').add_to(self.m)

        self.layer_control = folium.LayerControl()
        hillshade = folium.raster_layers.ImageOverlay(
            image="hillshade.png", bounds=map_bounds, opacity=0.8, interactive=True, show=True, name="Hillshade")
        rills = folium.raster_layers.ImageOverlay(
            image="rills.png", bounds=map_bounds, opacity=0.5, interactive=True, show=False, name="Rills")
        tau = folium.raster_layers.ImageOverlay(
            image="color-relief_tau.png", bounds=map_bounds, opacity=0.5, interactive=True, show=False, name="Tau")
        f1 = folium.raster_layers.ImageOverlay(
            image="color-relief_f1.png", bounds=map_bounds, opacity=0.5, interactive=True, show=False, name="f1")
        f2 = folium.raster_layers.ImageOverlay(
            image="color-relief_f2.png", bounds=map_bounds, opacity=0.5, interactive=True, show=False, name="f2")
            
        hillshade.add_to(self.m)

        rills.add_to(self.m)
        tau.add_to(self.m)
        f1.add_to(self.m)
        f2.add_to(self.m)
        self.tau_colormap.add_to(self.m)
        self.f1_colormap.add_to(self.m)
        self.f2_colormap.add_to(self.m)
        self.layer_control.add_to(self.m)
        self.m.save("map.html", close_file=False)
        return self.m
    
    @function_decorator
    def save_image_as_txt(self, image_path):
        """Prepares the geotiff file for the rillgen2D code by getting its dimensions (for the input.txt file) and converting it to
        .txt format"""
        if image_path == None or image_path == "":
            print("File not selected")
            raise FileNotFoundError("No image selected")
            
        filename = str(self.temporary_directory / Path(image_path).name)
        # Not sure if the os.path.normapath is necessary here, but it's here just in case
        # This is to account for downloading the GeoTiff directly into the tmp folder
        if not os.path.normpath(filename) == os.path.normpath(image_path):
            shutil.copyfile(str(image_path), filename)
            if Path(str(image_path) + ".aux.xml").exists():
                shutil.copyfile(str(image_path) + ".aux.xml",
                                str(self.temporary_directory / image_path.stem) + ".aux.xml")
        
        # Open existing dataset
        self.console.put("GDAL converting .tif to .txt...")
        self.console.put("Filename is: " + Path(filename).name)
        src_ds = gdal.Open(filename)
        band = src_ds.GetRasterBand(1)

        arr = band.ReadAsArray()
        dimensions = [arr.shape[0], arr.shape[1]]
        self.console.put("GEO Tiff successfully converted")
        self.console.put("Parameters Tab now available")
        self.console.put("Click Parameters Tab for next selections")
        return filename, dimensions[1], dimensions[0]
    
    def save_output(self):
        """Save outputs from a run in a timestamp-marked folder"""
        saveDir = "outputs_save-" + \
            str(datetime.now()).replace(" ", "").replace(":", ".")

        Path.mkdir(self.temporary_directory.parent / saveDir)
        saveDir = self.temporary_directory.parent / saveDir
        acceptable_files = [
            "parameters.txt","input.txt", "map.html", "rills.ppm"
        ]
        for fname in Path.cwd().iterdir():
            file_name = fname.name
            if file_name in acceptable_files or (file_name.endswith(".png") or file_name.endswith(".tif")):
                shutil.copy(file_name, saveDir / file_name)
