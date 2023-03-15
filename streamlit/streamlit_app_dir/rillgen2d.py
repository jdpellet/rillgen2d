

from wand.image import Image as im
from threading import Thread
from socket import *
from pathlib import Path
from osgeo import gdal, osr
from datetime import datetime
from ctypes import CDLL
import branca
import os
import subprocess
import shutil
import sys
import time
import folium
import osgeo
import PIL
# Apparently this API is supposed to be internal atm and seems to rapidly change without documentation between upadtes
PIL.Image.MAX_IMAGE_PIXELS = 933120000
# multiprocessing might be good instead, depedning on the function

"""This is the main rillgen2d file which handles the gui and communicates with console.py
and rillgen.c in order to perform the rillgen calculations"""


class Rillgen2d():
    def __init__(self, imagePath, queueObject, flagForDynamicVar):
        """Initializing the tkinter application and its tabs.
        The PyQt5 Application must go where it can be initialized
        only once in order to avoid bugs; otherwise the garbage
        collector does not handle it correctly."""
        self.console = queueObject
        self.imagePath = Path(imagePath)
        path = Path.cwd()
        self.filename = str(path / Path(self.imagePath).name)
        self.geo_ext = None  # used to get corner coordinates for the projection
        self.dimensions = None  # These are the dimensions of the input file that the user chooses
        # socket for the connection between rillgen2d.py and console.py; client socket
        self.rillgen = None  # Used to import the rillgen.c code

        self.img1 = None
        self.flagForDynamicVar = flagForDynamicVar
        # figure that will preview the image via rasterio

        """We only want the first tab for now; the others appear in order after the 
        processes carried out in a previous tab are completed"""
        self.first_time_populating_parameters_tab = True
        self.first_time_populating_view_output_tab = True

    def generate_color_ramp(self, filename, mode):
        """generates a color ramp from a geotiff image and then uses that in order to produce
        a color-relief for the geotiff"""
        self.console.put("Generating color ramp")
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
                      str(stats[0]+3*(stats[2]-stats[0])/4) + ", 101, 94, 190\n", str(stats[2]) +
                      ", 130, 125, 253\n", str(
                          stats[2]+(stats[1]-stats[2])/4) + ", 159, 158, 128\n",
                      str(stats[2]+(stats[1]-stats[2])/2) + ", 193, 192, 16\n", str(stats[2]+3*(stats[1]-stats[2])/4) + ", 224, 222, 137\n", str(stats[1]) + ", 255, 255, 255\n"])
        colormap = branca.colormap.LinearColormap([(0, 0, 0), (167, 30, 66), (51, 69, 131), (
            101, 94, 190), (130, 125, 253), (159, 158, 128), (193, 192, 16), (224, 222, 137), (255, 255, 255)])
        indexarr = [stats[0], stats[0]+(stats[2]-stats[0])/4, stats[0]+(stats[2]-stats[0])/2, stats[0]+3*(stats[2]-stats[0])/4, stats[2],
                    stats[2]+(stats[1]-stats[2])/4, stats[2]+(stats[1]-stats[2])/2, stats[2]+3*(stats[1]-stats[2])/4, stats[1]]
        if mode == 1:
            self.colormap = colormap
            self.colormap = self.colormap.to_step(index=indexarr)
            self.colormap.caption = "Elevation (in meters)"
            cmd1 = "gdaldem color-relief " + filename + " color-relief.txt color-relief.png"
        elif mode == 2:
            self.taucolormap = colormap
            self.taucolormap = self.taucolormap.to_step(index=indexarr)
            self.taucolormap.caption = "Tau (Pascals)"
            cmd1 = "gdaldem color-relief " + filename + \
                " color-relief.txt color-relief_tau.png"
        else:
            self.fcolormap = colormap
            self.fcolormap = self.fcolormap.to_step(index=indexarr)
            self.fcolormap.caption = "F (Pascals)"
            cmd1 = "gdaldem color-relief " + filename + \
                " color-relief.txt color-relief_f.png"
        f.close()
        self.run_command(cmd1)
        self.console.put(str(subprocess.check_output(cmd1, shell=True)))
        self.console.put("Hillshade and color relief generated\n")
        gtif = None

        #self.generate_color_ramp(self.filename, 1)

    def make_popup(self, mode):
        if mode == 1:
            self.console.put("hydrologic correction step in progress")
        else:
            self.console.put("dynamic mode in progress")

    def setup_rillgen(self):
        """Sets up files for the rillgen.c code by creating topo.txt and xy.txt, and
        imports the rillgen.c code using the CDLL library"""
        self.console.put("Setting up Rillgen")
        mode = 1
        self.make_popup(mode)
        cmd0 = "awk '{print $3}' " + self.imagePath.stem + ".asc > topo.txt"
        self.run_command(cmd0)
        cmd1 = "awk '{print $1, $2}' " + self.imagePath.stem + ".asc > xy.txt"
        self.run_command(cmd1)
        if self.rillgen == None:
            self.rillgen = CDLL(
                str(Path.cwd().parent / 'rillgen.so'))
        t1 = Thread(target=self.run_rillgen)
        t1.start()
        still_update = True
        while still_update:
            if mode == 1:
                currentPercentage = self.rillgen.hydrologic_percentage()
            else:
                currentPercentage = self.rillgen.dynamic_percentage()
            if currentPercentage == 0:
                time.sleep(0.5)
            elif currentPercentage > 0 and currentPercentage < 100:
                self.console.put(currentPercentage)
                time.sleep(0.5)
            else:
                self.console.put(100)
                if mode == 1 and self.flagForDynamicVar == 1:
                    mode = 2
                    self.console.put("Hydrologic correction step completed.")
                    currentPercentage = 0
                    self.console.put("Starting dynamic mode...")
                    self.make_popup(mode)
                else:
                    if self.flagForDynamicVar == 1:
                        self.console.put(
                            "Dynamic mode completed. Creating outputs...")
                    else:
                        self.console.put(
                            ("Hydrologic correction step completed. Creating outputs..."))
                    still_update = False
        t1.join()

    def run_rillgen(self):
        """Runs the rillgen.c library using the CDLL module"""
        self.console.put("Running Rillgen")
        self.rillgen.main()
        cmd4 = "paste xy.txt tau.txt > xy_tau.txt"
        self.run_command(cmd4)
        cmd5 = "paste xy.txt f.txt > xy_f.txt"
        self.run_command(cmd5)

    def populate_view_output_tab(self):
        """Populate the third tab with tkinter widgets. The third tab allows
        the user to generate a folium map based on the rillgen output
        and also allows them to preview the image hillshade and color relief"""
        self.canvas3bg = PIL.Image.open(
            Path.cwd().as_posix() + "/hillshade.png")
        self.canvas3fg = PIL.Image.open(
            Path.cwd().as_posix() + "/color-relief.png")
        self.bgcpy = self.canvas3bg.copy()
        self.fgcpy = self.canvas3fg.copy()
        self.bgcpy = self.bgcpy.convert("RGBA")
        self.fgcpy = self.fgcpy.convert("RGBA")
        self.alphablended = PIL.Image.blend(self.bgcpy, self.fgcpy, alpha=.4)
        # some tkinter versions do not support .png images
        (("Preview Complete\n\n"))
        return self.generatemap()

    def run_command(self, command):
        self.console.put(command)
        self.console.put(
            str(subprocess.check_output(command, shell=True), "UTF-8"))

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
        src_srs.ImportFromWkt(proj)
        tgt_srs = src_srs.CloneGeogCS()

        self.geo_ext = self.ReprojectCoords(ext, src_srs, tgt_srs)
        cmd0 = "gdal_translate xy_tau.txt tau.tif"
        self.run_command(cmd0)
        t1 = Thread(target=self.generate_color_ramp("tau.tif", 2))
        t1.start()
        cmd1 = "gdal_translate xy_f.txt f.tif"
        self.run_command(cmd1)
        t2 = Thread(target=self.generate_color_ramp("f.tif", 3))
        t2.start()
        projection = ds.GetProjection()
        geotransform = ds.GetGeoTransform()

        if projection is None and geotransform is None:
            self.console.put(
                "No projection or geotransform found on file" + str(self.filename) + "\n\n")
            sys.exit(1)

        for elem in ["tau.tif", "f.tif", "inciseddepth.tif"]:
            if (Path.cwd() / elem).exists():
                ds2 = gdal.Open(elem, gdal.GA_Update)
                if ds2 is None:
                    self.console.put(
                        ("Unable to open " + elem + " for writing\n\n"))
                    sys.exit(1)

                if geotransform is not None and geotransform != (0, 1, 0, 0, 0, 1):
                    ds2.SetGeoTransform(geotransform)

                if projection is not None and projection != '':
                    ds2.SetProjection(projection)

                gcp_count = ds.GetGCPCount()
                if gcp_count != 0:
                    ds2.SetGCPs(ds.GetGCPs(), ds.GetGCPProjection())

                if elem == "tau.tif":
                    self.console.put(
                        ("Translating tau.tif to .png\n\n"))
                    cmd2 = "gdal_translate -a_nodata 255 -ot Byte -of PNG " + \
                        elem.split(sep='.')[0] + ".tif " + \
                        elem.split(sep='.')[0] + ".png"
                elif elem == "f.tif":
                    self.console.put(
                        "Translating f.tif to .png\n\n")
                    cmd2 = "gdal_translate -a_nodata 255 -ot Byte -scale 0 0.1 -of PNG " + \
                        elem.split(sep='.')[0] + ".tif " + \
                        elem.split(sep='.')[0] + ".png"
                else:
                    self.console.put(
                        ("Translating inciseddepth.tif to .png\n\n"))
                    cmd2 = "gdal_translate -a_nodata 255 -ot Byte -of PNG " + \
                        elem.split(sep='.')[0] + ".tif " + \
                        elem.split(sep='.')[0] + ".png"
                self.run_command(cmd2)
            ds2 = None

        ds = None
        t1.join()
        t2.join()
        self.console.put("Georeferencing complete\n")
        self.convert_ppm()
        self.console.put("Model Output Successfully Created\n")
        self.console.put("Click on View Outputs Tab\n")

    def convert_ppm(self):
        """Convert the rills.ppm file to png so that it can be displayed on the map"""
        if not Path("rills.ppm").exists():
            self.console.put(
                ("Unable to open rills.ppm for writing\n\n"))
        else:
            self.console.put(
                ("Translating rills.ppm to .png\n\n"))
            with im(filename="rills.ppm") as img:
                img.save(filename="P6.ppm")
            cmd = "gdal_translate -of PNG -a_nodata 255 P6.ppm rills.png"
            self.run_command(cmd)

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

    def ReprojectCoords(self, coords, src_srs, tgt_srs):
        """Reproject a list of x,y coordinates. From srs_srs to tgt_srs"""
        trans_coords = []
        transform = osr.CoordinateTransformation(src_srs, tgt_srs)
        for x, y in coords:
            x, y, z = transform.TransformPoint(x, y)
            trans_coords.append([x, y])
        return trans_coords

    def generatemap(self):
        """Generate Leaflet Folium Map"""
        mapbounds = [[self.geo_ext[1][1], self.geo_ext[1][0]],
                     [self.geo_ext[3][1], self.geo_ext[3][0]]]
        self.m = folium.Map(location=[(self.geo_ext[1][1]+self.geo_ext[3][1])/2,
                                      (self.geo_ext[1][0]+self.geo_ext[3][0])/2], zoom_start=14, tiles='Stamen Terrain')
        folium.TileLayer('OpenStreetMap').add_to(self.m)
        folium.TileLayer('Stamen Toner').add_to(self.m)

        self.layer_control = folium.LayerControl()
        img1 = folium.raster_layers.ImageOverlay(
            image="hillshade.png", bounds=mapbounds, opacity=0.8, interactive=True, show=True, name="Hillshade")
        # img2 = folium.raster_layers.ImageOverlay(image="color-relief.png", bounds=mapbounds, opacity=0.6, interactive=True, show=False, name="color-relief")
        # img3 = folium.raster_layers.ImageOverlay(image="f.png", bounds=mapbounds, opacity=0.5, interactive=True, show=False, name="f")
        # img4 = folium.raster_layers.ImageOverlay(image="tau.png", bounds=mapbounds, opacity=0.5, interactive=True, show=True, name="tau")
        img5 = folium.raster_layers.ImageOverlay(
            image="rills.png", bounds=mapbounds, opacity=0.5, interactive=True, show=False, name="Rills")
        img6 = folium.raster_layers.ImageOverlay(
            image="color-relief_tau.png", bounds=mapbounds, opacity=0.5, interactive=True, show=False, name="Tau")
        img7 = folium.raster_layers.ImageOverlay(
            image="color-relief_f.png", bounds=mapbounds, opacity=0.5, interactive=True, show=False, name="f")
        # geotiff_group = folium.FeatureGroup(name="color-relief")
        # geotiff_group.add_child(img1)
        # geotiff_group.add_child(img2)
        # geotiff_group.add_child(self.colormap)
        img1.add_to(self.m)
        # img2.add_to(m)
        # img3.add_to(m)
        # img4.add_to(m)
        img5.add_to(self.m)
        img6.add_to(self.m)
        img7.add_to(self.m)
        # geotiff_group.add_to(m)
        # m.add_child(geotiff_group)
        # self.colormap.add_to(m)
        self.taucolormap.add_to(self.m)
        self.fcolormap.add_to(self.m)
        self.layer_control.add_to(self.m)
        self.m.save("map.html", close_file=False)
        return self.m


def generate_input_txt_file(
        flagForEquationVar,
        flagforDynamicModeVar,
        flagForMaskVar,
        flagForTaucSoilAndVegVar,
        flagFord50Var,
        flagForRockCoverVar,
        fillIncrementVar,
        minSlopeVar,
        expansionVar,
        yellowThresholdVar,
        lattice_size_xVar,
        lattice_size_yVar,
        deltaXVar,
        noDataVar,
        smoothingLengthVar,
        rainVar,
        taucSoilAndVegeVar,
        d50Var,
        rockCoverVar,
        tanAngleOfInternalFrictionVar,
        bVar,
        cVar,
        rillWidthVar,
        console
):
    """Generate the input.txt file using the flags from the second tab.

    There are then helper functions, the first of which runs the rillgen.c script
    in order to create xy_f.txt and xy_tau.txt (and xy_inciseddepth.txt if flagforDynamicModeVar==1)

    The second helper function then sets the georeferencing information from the original
    geotiff file to xy_f.txt and xy_tau.txt (and xy_inciseddepth.txt if flagforDynamicModeVar==1) in order to generate f.tif and tau.tif"""
    path = Path.cwd() / 'input.txt'
    if path.exists():
        Path.unlink(path)
    path = Path.cwd()
    f = open('input.txt', 'w')
    f.write(str(int(flagForEquationVar)) + '\n')
    f.write(str(int(flagforDynamicModeVar)) + '\n')
    if (path / "dynamicinput.txt").exists():
        Path.unlink(path / "dynamicinput.txt")
    if flagforDynamicModeVar == 1:
        if (path.parent / "dynamicinput.txt").exists():
            shutil.copyfile(path.parent / "dynamicinput.txt",
                            path / "dynamicinput.txt")
            console.put(
                "dynamicinput.txt found and copied to inner directory\n\n")
        else:
            console.put("dynamicinput.txt not found\n")

    f.write(str(int(flagForMaskVar))+'\n')
    if flagForMaskVar == 1:
        if (path / "mask.tif").exists():
            convert_geotiff_to_txt("mask")
            console.put("mask.txt generated\n")
        else:
            console.put("mask.tif not found\n")
            flagForMaskVar = 0

    f.write(str(int(flagForTaucSoilAndVegVar))+'\n')
    if (path / "taucsoilandvegfixed.txt").exists():
        Path.unlink(path / "taucsoilandvegfixed.txt")
    if int(flagForTaucSoilAndVegVar) == 1:
        if (path.parent / "taucsoilandvegfixed.txt").exists():
            shutil.copyfile(
                path.parent / "taucsoilandvegfixed.txt", path / "taucsoilandvegfixed.txt")
            console.put(
                ("taucsoilandvegfixed.txt found and copied to inner directory\n\n"))
        else:
            console.put("taucsoilandvegfixed.txt not found\n")
    f.write(str(int(flagFord50Var))+'\n')
    if (path / "d50.txt").exists():
        Path.unlink(path / "d50.txt")
    if int(flagFord50Var) == 1:
        if (path.parent / "d50.txt").exists():
            shutil.copyfile(path.parent / "d50.txt", path / "d50.txt")
            console.put(
                ("d50.txt found and copied to inner directory\n\n"))
        else:
            console.put(
                ("d50.txt not found\n\n"))
    f.write(str(int(flagForRockCoverVar))+'\n')
    if (path / "rockcover.txt").exists():
        path.unlink(path / "rockcover.txt")
    if int(flagForRockCoverVar) == 1:
        if (path.parent / "rockcover.txt").exists():
            shutil.copyfile(path.parent / "rockcover.txt",
                            path / "rockcover.txt")
            console.put(
                "rockcover.txt found and copied to inner directory\n\n")
        else:
            console.put("rockcover.txt not found\n")
    f.write(str(fillIncrementVar)+'\n')
    f.write(str(minSlopeVar)+'\n')
    f.write(str(expansionVar)+'\n')
    f.write(str(yellowThresholdVar)+'\n')
    f.write(str(lattice_size_xVar)+'\n')
    f.write(str(lattice_size_yVar)+'\n')
    f.write(str(deltaXVar)+'\n')
    f.write(str(noDataVar)+'\n')
    f.write(str(smoothingLengthVar)+'\n')
    f.write(str(rainVar)+'\n')
    f.write(str(taucSoilAndVegeVar)+'\n')
    f.write(str(d50Var)+'\n')
    f.write(str(rockCoverVar)+'\n')
    f.write(str(tanAngleOfInternalFrictionVar)+'\n')
    f.write(str(bVar)+'\n')
    f.write(str(cVar)+'\n')
    f.write(str(rillWidthVar)+'\n')
    console.put(("Generated input.txt\n"))
    f.close()


def save_image_as_txt(imagePath, console):
    """Prepares the geotiff file for the rillgen2D code by getting its dimensions (for the input.txt file) and converting it to
    .txt format"""
    if imagePath == None or imagePath == "":
        console.put("NO FILENAME CHOSEN Please choose a valid file")
    else:
        if Path.cwd().name == "tmp":
            os.chdir("..")

        path = Path.cwd() / "tmp"
        if path.exists():
            shutil.rmtree(path.as_posix())
        Path.mkdir(path)
        filename = str(path / Path(imagePath).name)
        shutil.copyfile(str(imagePath), filename)
        if Path(str(imagePath) + ".aux.xml").exists():
            shutil.copyfile(str(imagePath) + ".aux.xml",
                            str(path / imagePath.stem) + ".aux.xml")
        shutil.copyfile("input.txt", path / "input.txt")
        """This portion compiles the rillgen2d.c file in order to import it as a module"""

        # compile the c file so that it will be useable later
        cmd = "gcc -Wall -shared -fPIC ../rillgen2d.c -o rillgen.so"
        console.put(str(subprocess.check_output(cmd, shell=True), "UTF-8"))

        for fname in Path.cwd().iterdir():
            if fname.suffix == ".tif":
                Path(fname).unlink()
        os.chdir(str(path))

        # Open existing dataset
        console.put(("GDAL converting .tif to .txt...\n\n") +
                    '\n'+"Filename is: " +
                    (Path(filename).name + "\n\n"))
        src_ds = gdal.Open(filename)
        band = src_ds.GetRasterBand(1)
        arr = band.ReadAsArray()
        dimensions = [arr.shape[0], arr.shape[1]]
        console.put("GEO Tiff successfully converted")
        console.put("Parameters Tab now available")
        console.put("Click Parameters Tab for next selections")
        return (filename, dimensions[1], dimensions[0])


def convert_geotiff_to_txt(filename, console):
    console.put("Converting geotiff to txt")
    src_ds = gdal.Open(filename + ".tif")
    if src_ds is None:
        console.put("ERROR: Unable to open " +
                    filename + " for writing")
        sys.exit(1)
    # Open output format driver, see gdal_translate --formats for list
    format = "XYZ"
    driver = gdal.GetDriverByName(format)

    # Output to new format
    dst_ds = driver.CreateCopy(filename + "_dem.asc", src_ds, 0)

    # Properly close the datasets to flush to disk
    src_ds = None
    dst_ds = None

    cmd1 = "gdal_translate -of XYZ " + filename + ".tif " + filename + ".asc"
    console.put(cmd1)
    console.put(str(subprocess.check_output(cmd1, shell=True)))

    cmd2 = "awk '{print $3}' " + filename + \
        ".asc > " + filename + ".txt"
    console.put(str(subprocess.check_output(cmd2, shell=True), 'UTF-8'))
    console.put(cmd2)
    # remove temporary .asc file to save space
    cmd3 = "rm " + filename + "_dem.asc"
    console.put(str(subprocess.check_output(cmd3, shell=True), "UTF-8"))
    console.put(cmd3)


def hillshade_and_color_relief(filename, console):
    """Generates the hillshade and color-relief images from the original 
    geotiff image that will be available on the map"""

    console.put(
        "Generating hillshade and color relief...\n")
    cmd0 = "gdaldem hillshade " + filename + " hillshade.png"
    console.put(cmd0)
    console.put(str(subprocess.check_output(cmd0, shell=True), 'UTF-8'))


def save_output():
    """Save outputs from a run in a timestamp-marked folder"""
    saveDir = "outputs_save-" + \
        str(datetime.now()).replace(" ", "").replace(":", ".")
    Path.mkdir(Path.cwd().parent / saveDir)
    saveDir = Path.cwd().parent / saveDir
    acceptable_files = ["parameters.txt",
                        "input.txt", "map.html", "rills.ppm"]
    for fname in Path.cwd().iterdir():
        file_name = fname.name
        if file_name in acceptable_files or (file_name.endswith(".png") or file_name.endswith(".tif")):
            shutil.copy(file_name, saveDir / file_name)


def main(imagePath, console, flagForDyanmicModeVar):
    rillgen = Rillgen2d(
        imagePath,
        console,
        flagForDyanmicModeVar
    )
    convert_geotiff_to_txt(Path(imagePath).stem, console)
    t1 = Thread(target=rillgen.generate_color_ramp,
                args=(rillgen.filename, 1))
    t1.start()
    rillgen.setup_rillgen()
    t1.join()
    rillgen.set_georeferencing_information()
    rillgen.populate_view_output_tab()
