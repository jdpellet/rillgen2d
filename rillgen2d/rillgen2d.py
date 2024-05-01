from __future__ import annotations
import typing
import osgeo
import folium
import shutil
import subprocess
import os
import sys
import branca
from ctypes import CDLL
from datetime import datetime
from osgeo import gdal, osr
from pathlib import Path
from threading import Thread
from multiprocessing import Process, Queue
# Got a weird issue when I just imported PIL before. Not srue why
from PIL import Image

# Enable exceptions  for GDAL
gdal.UseExceptions()

if typing.TYPE_CHECKING:
    from rillgen2d.parameters import Parameters
# Apparently this API is supposed to be internal atm and seems to rapidly change without documentation between updates
#
# update pillow to accept large images
Image.MAX_IMAGE_PIXELS = 933120000
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

    def __init__(self, params: Parameters, message_queue: Queue):
        self.has_run = False  # Flag set by frontend when calling the .start method
        self.console = message_queue
        self.params = params
        self.temporary_directory = Path(__file__).parents[1] / "tmp"
        # params stores the filepath, but wont have it at the time of initialization
        self.image_path: str = None
        self.filename: str = None
        self.geo_ext: folium.Map = (
            None  # used to get corner coordinates for the projection
        )
        self.dimensions: tuple[
            int, int
        ] = None  # These are the dimensions of the input file that the user chooses
        self.img1: folium.raster_layers.ImageOverlay = None
        self.rillgen: CDLL = None  # Used to import the rillgen.c code
        # Tracking threads in case of exceptions so we can join them before ending the program
        self.threads: list[Thread] = []

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
        self.run_command(
            f"gdaldem hillshade \"{self.filename}\" {self.temporary_directory / 'hillshade.png'}"
        )
        return self.temporary_directory / "hillshade.png"

    @function_decorator
    def update_image_path(self):
        self.image_path = self.params.image_path
        self.filename = str(Path.cwd() / Path(self.params.image_path).name)

    @function_decorator
    def run_command(self, command):
        self.console.put(command)
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"Command failed: {command}\nError: {result.stderr}")
        self.console.put(result.stdout)
        self.console.put(
            str(subprocess.check_output(command, shell=True), "UTF-8"))

    @function_decorator
    def convert_geotiff_to_txt(self, filename):
        self.console.put("Converting geotiff to txt")
        file_path = str(self.temporary_directory/ filename)
        src_ds = gdal.Open(file_path + ".tif")
        src_projection = src_ds.GetProjection()
        src_geotransform = src_ds.GetGeoTransform()
        if not src_projection or src_geotransform == (0, 1, 0, 0, 0, 1):
            self.console.put("No Input Projection or Geotransform found. Assigning null island location.")
            null_geotransform = (0.0, 1.0, 0.0, 0.0, 0.0, 1.0)
            src_ds.SetGeoTransform(null_geotransform)
            srs = osr.SpatialReference()
            srs.ImportFromEPSG(4326)  # WGS84
            src_ds.SetProjection(srs.ExportToWkt())
        else:
            self.console.put("Input Projection information found.")
            self.console.put("Input Projection: " + src_projection)
            self.console.put("Input Geotransform: " + str(src_geotransform))

        if src_ds is None:
            raise Exception("ERROR: Unable to open " +
                            file_path + ".tif" + " for writing")

        # Open output format driver, see gdal_translate --formats for list
        format = "XYZ"
        driver = gdal.GetDriverByName(format)

        # Output to new format
        #dst_ds = driver.CreateCopy(file_path + "_dem.asc", src_ds, 0)

        # Properly close the datasets to flush to disk
        src_ds = None
        #dst_ds = None
        self.run_command(
            f"gdal_translate -of XYZ " + file_path + ".tif " + file_path + ".asc"
        )
        self.run_command("awk '{print $3}' " + file_path + ".asc > " + file_path + ".txt")

        # remove temporary .asc file to save space
        #self.run_command("rm " + file_path + "_dem.asc")

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

        # TODO: figure out what this is supposed to do so I can clarify it
        if caption.startswith("Tau") and stats[1] > 100:
            stats[1] = 100
            if stats[2] > 50:
                stats[2] = 50

        index_array = [
            stats[0],
            stats[0] + (stats[2] - stats[0]) / 4,
            stats[0] + (stats[2] - stats[0]) / 2,
            stats[0] + 3 * (stats[2] - stats[0]) / 4,
            stats[2],
            stats[2] + (stats[1] - stats[2]) / 4,
            stats[2] + (stats[1] - stats[2]) / 2,
            stats[2] + 3 * (stats[1] - stats[2]) / 4,
            stats[1],
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
            (255, 255, 255),
        ]
        f = open("color-relief.txt", "w")
        for i in range(len(index_array)):
            # Making a line in the format "index, r, g, b\n"
            line = ", ".join(map(str, (index_array[i], *colors[i]))) + "\n"
            f.write(line)
        f.close()
        colormap = branca.colormap.LinearColormap(
            colors).to_step(index=index_array)
        colormap.caption = caption
        setattr(self, colormap_name, colormap)
        self.run_command(
            f'gdaldem color-relief "{filename}" color-relief.txt color-relief_{Path(filename).stem}.png'
        )

        self.console.put("Hillshade and color relief generated")
        gtif = None

    @function_decorator
    def setup_rillgen(self):
        """Sets up files for the rillgen.c code by creating topo.txt and xy.txt, and
        imports the rillgen.c code using the CDLL library"""
        self.run_command(
            f"gcc -Wall -shared -fPIC {Path(__file__).parent}/rillgen2d.c -o {self.temporary_directory}/rillgen.so"
        )
        # NOTE the CDLL arguemnt has to be a string for windows filepaths?
        self.rillgen = CDLL(str(self.temporary_directory / "rillgen.so"))
        self.console.put("Setting up Rillgen")

        self.console.put("Hydrologic correction step in progress")
        self.run_command("awk '{print $3}' " +
                         self.image_path.stem + ".asc > topo.txt")
        self.run_command(
            "awk '{print $1, $2}' " + self.image_path.stem + ".asc > xy.txt"
        )
        if self.rillgen == None:
            self.rillgen = CDLL(str(Path.cwd().parent / "rillgen.so"))
        self.run_rillgen()
        self.console.put(
            "Hydrologic correction step completed. Creating outputs...")

    @function_decorator
    def run_rillgen(self):
        """Runs the rillgen.c library using the CDLL module"""
        self.console.put("Running Rillgen")
        self.rillgen.main()
        self.run_command("paste xy.txt tau.txt > xy_tau.txt")
        self.run_command("paste xy.txt f1.txt > xy_f1.txt")
        self.run_command("paste xy.txt f2.txt > xy_f2.txt")
        if self.params.get_value("mode") == 1: #NA Added inciseddepth if dynamic mode
            self.run_command("paste xy.txt inciseddepth.txt > xy_inciseddepth.txt")


    @function_decorator
    def add_thread(self, function, *args, **kwargs):
        thread = Thread(target=function, args=args, kwargs=kwargs)
        self.threads.append(thread)
        thread.start()
        return thread

    @function_decorator
    def set_georeferencing_information(self):
        """Sets the georeferencing information for f.tif and tau.tif (and incised depth.t if self.flagForDynamicVar==1) to be the same as that
        from the original geotiff file"""

        self.console.put("Setting georeferencing information\n")
        if self.filename is None and not Path(self.filename).exists():
            self.console.put("FILE NOT FOUND: Please select a file in tab 1")
            return
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

        if not proj:
            self.console.put("DEM has no projection information. Assigning null island location.")
            null_geotransform = (0.0, 1.0, 0.0, 0.0, 0.0, 1.0)
            ds.SetGeoTransform(null_geotransform)
            ds.SetProjection('NULL')

            # No need for reprojection, set geo_ext directly
            self.geo_ext = self.GetExtent(null_geotransform, cols, rows)

        else:
            src_srs.ImportFromWkt(proj)

        tgt_srs = src_srs.CloneGeogCS()
        self.geo_ext = self.ReprojectCoords(ext, src_srs, tgt_srs)
        cmd01 = "gdal_translate -f GTiff xy_tau.txt tau.tif"
        self.run_command(cmd01)
        cmd11 = "gdal_translate -f GTiff xy_f1.txt f1.tif"
        self.run_command(cmd11)
        cmd21 = "gdal_translate -f GTiff xy_f2.txt f2.tif"
        self.run_command(cmd21)

        if self.params.get_value("mode") == 1: #NA Added inciseddepth if dynamic mode
            cmd31 = "gdal_translate -f GTiff xy_inciseddepth.txt inciseddepth.tif"
            self.run_command(cmd31)

        projection = ds.GetProjection()
        geotransform = ds.GetGeoTransform()

        if projection is None and geotransform is None:
            self.console.put(
                "No projection or geotransform found on file" +
                str(self.filename)
            )
            sys.exit(1)

        for elem in ["tau.tif", "f1.tif", "f2.tif", "inciseddepth.tif"]:
            if (Path.cwd() / elem).exists():
                ds2 = gdal.Open(elem, gdal.GA_Update)
                if ds2 is None:
                    self.console.put(
                        ("Unable to open " + elem + " for writing\n\n"))
                    sys.exit(1)

                if geotransform is not None and geotransform != (0, 1, 0, 0, 0, 1):
                    ds2.SetGeoTransform(geotransform)

                if projection is not None and projection != "":
                    ds2.SetProjection(projection)

                gcp_count = ds.GetGCPCount()
                if gcp_count != 0:
                    ds2.SetGCPs(ds.GetGCPs(), ds.GetGCPProjection())

                if elem == "tau.tif":

                    gtiff = gdal.Open("tau.tif")#NA next 5 lines
                    stats = gtiff.GetRasterBand(1).GetStatistics(0,1) # get max value stats[1]
                    f = open("whiteredTau.txt", "w") # write color_text_file for gdaldem in /tmp using 0 - max value
                    f.write("0 255 255 255\n")
                    f.write(f"{stats[1]} 255 0 0\n")
                    f.close()
                    self.console.put(("Translating tau.tif to .png\n\n"))
                    cmd3 = (
                        f"gdaldem color-relief tau.tif whiteredTau.txt tau.png -of PNG"
                    )
                elif elem == "f1.tif":
                    self.console.put("Translating f1.tif to .png\n\n")
                    cmd3 = (
                        "gdal_translate -a_nodata 0 -ot Byte -scale 0 2 -of PNG " #NA scale and no data changed
                        + elem.split(sep=".")[0]
                        + ".tif "
                        + elem.split(sep=".")[0]
                        + ".png"
                    )
                elif elem == "f2.tif":
                    self.console.put("Translating f2.tif to .png\n\n")
                    cmd3 = (
                        "gdal_translate -a_nodata 0 -ot Byte -scale 0 2 -of PNG " #NA scale and no data changed
                        + elem.split(sep=".")[0]
                        + ".tif "
                        + elem.split(sep=".")[0]
                        + ".png"
                    )
                else:

                    gtif = gdal.Open("inciseddepth.tif") #NA 5 next lines
                    stats = gtif.GetRasterBand(1).GetStatistics(0,1) # get max value stats[1]
                    f = open("whiteredID.txt", "w") # write color_text_file for gdaldem in /tmp using 0 - max value
                    f.write("0 255 255 255\n")
                    f.write(f"{stats[1]} 255 0 0\n")
                    f.close()
                    self.console.put(
                        ("Translating inciseddepth.tif to .png\n\n"))
                    cmd3 = (
                        f"gdaldem color-relief inciseddepth.tif whiteredID.txt inciseddepth.png -of PNG" #NA changed from gdal_translate to gdaldem
                    )

                self.run_command(cmd3)

            ds2 = None

        ds = None
        self.console.put("Georeferencing complete\n")
        self.convert_ppm()
        self.console.put("Success!\n")

    @function_decorator
    def convert_ppm(self):
        """Convert the rills.ppm file to png so that it can be displayed on the map"""
        # Note, the ppm is encoded in P3 format, so we need to use wand to actually convert it to the P6 format
        if not Path("rills.ppm").exists():
            self.console.put("Unable to open rills.ppm for writing")
        else:
            self.console.put("Translating rills.ppm to .png")
            with Image.open("rills.ppm") as img:
                img.save("P6.ppm")
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
                x = gt[0] + (px * gt[1]) + (py * gt[2])
                y = gt[3] + (px * gt[4]) + (py * gt[5])
                ext.append([x, y])
            yarr.reverse()
        return ext

    @function_decorator
    def ReprojectCoords(
        self, coords: list, src_srs: osr.SpatialReference, tgt_srs: osr.SpatialReference
    ) -> list:
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
        map_bounds = [
            (self.geo_ext[1][1], self.geo_ext[1][0]),
            (self.geo_ext[3][1], self.geo_ext[3][0]),
        ]
        self.m = folium.Map(
            location=[
                (self.geo_ext[1][1] + self.geo_ext[3][1]) / 2,
                (self.geo_ext[1][0] + self.geo_ext[3][0]) / 2,
            ],
            zoom_start=16,
        )

        folium.TileLayer("OpenStreetMap").add_to(self.m)

        self.layer_control = folium.LayerControl()
        img1 = folium.raster_layers.ImageOverlay(
            image="hillshade.png",
            bounds=map_bounds,
            opacity=1.0,
            interactive=True,
            show=False,
            name="Hillshade",
        )
        img2 = folium.raster_layers.ImageOverlay(
            image="rills.png",
            bounds=map_bounds,
            opacity=0.5,
            interactive=True,
            show=True,
            name="Rills",
        )
        img3 = folium.raster_layers.ImageOverlay(
            image="tau.png",
            bounds=map_bounds,
            opacity=0.5,
            interactive=True,
            show=True,
            name="Tau",
        )
        img4 = folium.raster_layers.ImageOverlay(
            image="f2.png",
            bounds=map_bounds,
            opacity=0.5,
            interactive=True,
            show=True,
            name="f",
        )
        if self.params.get_value("mode") == 1: #NA Added inciseddepth to overlay if dynamic mode
            img5 = folium.raster_layers.ImageOverlay(
            image="inciseddepth.png",
            bounds=map_bounds,
            opacity=0.5,
            interactive=True,
            show=True,
            name="inciseddepth",
        )
        img1.add_to(self.m)
        img2.add_to(self.m)
        img3.add_to(self.m)
        img4.add_to(self.m)
        if self.params.get_value("mode") == 1: #NA Added inciseddepth to overlay if dynamic mode
                img5.add_to(self.m)
        self.layer_control.add_to(self.m)
        self.m.save("map.html", close_file=False)
        return self.m

    @function_decorator
    def save_image_as_txt(self, image_path: str | Path):
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
                shutil.copyfile(
                    str(image_path) + ".aux.xml",
                    str(self.temporary_directory /
                        image_path.stem) + ".aux.xml",
                )

        # Open existing dataset
        self.console.put("GDAL converting .tif to .txt...")
        self.console.put("Filename is: " + Path(filename).name)
        src_ds = gdal.Open(filename)
        band = src_ds.GetRasterBand(1)

        geotransform = src_ds.GetGeoTransform()
        pixel_size_x = geotransform[1]
        pixel_size_y = geotransform[5]

        arr = band.ReadAsArray()
        dimensions = [arr.shape[0], arr.shape[1]]
        self.console.put("GEO Tiff successfully converted")
        self.console.put("Parameters Tab now available")
        self.console.put("Click Parameters Tab for next selections")
        return filename, dimensions[1], dimensions[0], pixel_size_x, pixel_size_y

    def save_output(self):
        """Save outputs from a run in a timestamp-marked folder"""
        saveDir = "outputs_save-" + str(datetime.now()).replace(" ", "").replace(
            ":", "."
        )
        
        Path.mkdir(self.temporary_directory.parent / saveDir)
        saveDir = self.temporary_directory.parent / saveDir
        acceptable_files = ["parameters.txt",
                            "input.txt", "map.html", "rills.ppm"]
        for fname in self.temporary_directory.iterdir():
            file_name = fname.name
            if file_name in acceptable_files or (
                file_name.endswith(".png") or file_name.endswith(".tif")
            ):
                shutil.copy(self.temporary_directory /
                            file_name, saveDir / file_name)
        return saveDir
