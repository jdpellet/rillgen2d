import shutil
import PIL
import requests
import os
import tarfile
from pathlib import Path
# Threading makes sense here, since C code doesn't have global interpreter lock?
from threading import Thread
from queue import Queue
import streamlit as st
try:
    import rillgen2d as rg2d
except ModuleNotFoundError:
    os.chdir("..")
    import rillgen2d as rg2d



class App:
    def __init__(self):
        if "console_log" not in st.session_state:
            st.session_state.console_log = []
        if "hillshade_generated" not in st.session_state:
            st.session_state.hillshade_generated = False
        if "console" not in st.session_state:
            st.session_state.console = Queue()
        if "rillgen2d" not in st.session_state:
            st.session_state.rillgen2d = None
        if "imagePath" not in st.session_state:
            st.session_state.imagePath = None

        self.get_parameter_values()
        self.initialize_parameter_fields()

    def initialize_parameter_fields(self, force=False):
        """
        Initialize the parameter fields to the correct types, set values to null
        """
        if "flagformodeVar" not in st.session_state:
            st.session_state.flagformodeVar = False
        if "flagforroutingmethodVar" not in st.session_state:
            st.session_state.flagforroutingmethodVar = 0
        if "flagforsheerstressequationVar" not in st.session_state:    
            st.session_state.flagforsheerstressequationVar = False
        if "flagformaskVar" not in st.session_state:    
            st.session_state.flagformaskVar = False
        if "flagfortaucsoilandvegVar" not in st.session_state:    
            st.session_state.flagfortaucsoilandvegVar = False
        if "flagford50Var" not in st.session_state:    
            st.session_state.flagford50Var = False
        if "flagforrockthicknessVar" not in st.session_state:    
            st.session_state.flagforrockthicknessVar = False
            st.session_state.flagforrockcoverVar = False
            st.session_state.fillincrementVar = 0.01
            st.session_state.minslopeVar = 0.03
            st.session_state.expansionVar = 2
            st.session_state.yellowthresholdVar = 1.25
            st.session_state.lattice_size_xVar = 0
            st.session_state.lattice_size_yVar = 0
            st.session_state.deltaxVar = 0.5
            st.session_state.nodataVar = -9999
            st.session_state.smoothinglengthVar = 0
            st.session_state.manningsnVar = 0.5
            st.session_state.depthweightfactorVar = 0.6
            st.session_state.numberofslicesVar = 10
            st.session_state.numberofsweepsVar = 3
            st.session_state.rainVar = 73
            st.session_state.taucsoilandvegeVar = 0
            st.session_state.d50Var = 0.1
            st.session_state.rockthicknessVar = 0.3
            st.session_state.rockcoverVar = 1
            st.session_state.tanangleofinternalfrictionVar = 0.6
            st.session_state.bVar = 1
            st.session_state.cVar = 0.87
            st.session_state.rillwidthcoefficientVar = 1.5
            st.session_state.rillwidthexponentVar = 0.3
            st.session_state.show_parameters = False
    
    def get_parameter_values(self):
    # Open the input.txt file for reading
        with open('input.txt', 'r') as f:
            def read_first_column():
                return f.readline().split('\t')[0].strip()
        # Use the helper function to read the values
            st.session_state.flagformodeVar = int(read_first_column())
            st.session_state.flagforroutingmethodVar = int(read_first_column())
            st.session_state.flagforshearstressequationVar = int(read_first_column())
            st.session_state.flagformaskVar = int(read_first_column())
            st.session_state.flagfortaucsoilandvegVar = int(read_first_column())
            st.session_state.flagford50Var = int(read_first_column())
            st.session_state.flagforrockthickVar = int(read_first_column())
            st.session_state.flagforrockcoverVar = int(read_first_column())
            st.session_state.fillincrementVar = float(read_first_column())
            st.session_state.minslopeVar = float(read_first_column())
            st.session_state.expansionVar = int(read_first_column())
            st.session_state.yellowthresholdVar = float(read_first_column())
            # Skip the next two lines
            f.readline()
            f.readline()
            st.session_state.deltaxVar = float(read_first_column())
            st.session_state.nodataVar = int(read_first_column())
            st.session_state.smoothinglengthVar = int(read_first_column())
            st.session_state.manningsnVar = float(read_first_column())
            st.session_state.depthweightfactorVar = float(read_first_column())
            st.session_state.numberofslicesVar = int(read_first_column())
            st.session_state.numberofsweepsVar = int(read_first_column())
            st.session_state.rainVar = int(read_first_column())
            st.session_state.taucsoilandvegeVar = int(read_first_column())
            st.session_state.d50Var = float(read_first_column())
            st.session_state.rockthicknessVar = float(read_first_column())
            st.session_state.rockcoverVar = int(read_first_column())
            st.session_state.tanangleofinternalfrictionVar = float(read_first_column())
            st.session_state.bVar = int(read_first_column())
            st.session_state.cVar = float(read_first_column())
            st.session_state.rillwidthcoefficientVar = float(read_first_column())
            st.session_state.rillwidthexponentVar = float(read_first_column())
            st.session_state.show_parameters = True
            f.close()

    def get_image_from_url(self, url):
        """Given the url of an image when a raster is generated or located online,
        extract the geotiff image from the url and display it on the canvas """
        try:
            r = requests.get(url, allow_redirects=True)
            path = Path.cwd()
            if path.as_posix().endswith('tmp'):
                path = path.parent
            downloaded = os.path.basename(url)
            img = downloaded
            open((path / downloaded), 'wb').write(r.content)
            if downloaded.endswith(".gz"):
                tarpath = path / downloaded
                imagefile = self.extract_geotiff_from_tarfile(tarpath, path)
                os.remove(path / downloaded)
            else:
                imagefile = (path / img)

        except Exception:
            return
        else:
            return imagefile

    def extract_geotiff_from_tarfile(self, tarpath, outputpath):
        img = tarpath
        tar = tarfile.open(tarpath)
        for filename in tar.getnames():
            if filename.endswith('.tif'):
                tar.extract(filename, path=str(outputpath))
                img = filename
                break
        desiredfile = (outputpath / img)
        return desiredfile

    def generate_parameters_button_callback(self):
        imagePath = st.session_state.imagePathInput1 or st.session_state.imagePathInput2
        if imagePath.startswith("http"):
            imagePath = str(self.get_image_from_url(imagePath))
        if not Path(imagePath).is_file():
            st.error("Invalid image path or URL")
            return
        if imagePath.endswith("gz"):
            tarpath = imagePath
            imagePath = self.extract_geotiff_from_tarfile(
                tarpath, Path(imagePath))
        else:
            imagePath = Path(imagePath)
        self.get_parameter_values()
        try:
            filename, st.session_state.lattice_size_xVar, st.session_state.lattice_size_yVar =\
                rg2d.save_image_as_txt(imagePath, st.session_state.console)
        except AttributeError as e:
            st.error(f"Error converting {imagePath.stem} to txt")
            os.chdir("..")
            return

        rg2d.hillshade_and_color_relief(filename, st.session_state.console)
        st.session_state.hillshade_generated = True
        st.session_state.imagePath = imagePath

    def save_callback(self):
        rg2d.save_output()

    def getMask(self, filepath):
        # TODO Figure out input for filepath
        if st.session_state.flagformaskVar == 1:
            try:
                maskfile = Path(filepath)
                if maskfile.suffix == '.tar' or maskfile.suffix == '.gz':
                    maskfile = self.extract_geotiff_from_tarfile(
                        maskfile, Path.cwd())

                shutil.copyfile(maskfile, Path.cwd() / "mask.tif")
                st.session_state.console.put("maskfile: is: " + str(maskfile))
            except Exception:
                raise Exception("Invalid mask.tif file")
  
    def populate_parameters_tab(self):
        """Populate the second tab in the application with tkinter widgets. This tab holds editable parameters
        that will be used to run the rillgen2dwitherode.c script. lattice_size_x and lattice_size_y are read in from the
        geometry of the geotiff file"""
        with st.sidebar:
            # On click the app will rerun and the other parameters will not display
            view_output = st.checkbox(
                "Reload a Prior Model Run", 
                value=False, 
                help="Load a prior model run by selecting a valid directory",
                key="view_output_checkbox")
            if view_output:
                st.text_input("Output Directory Path",
                              value=Path.cwd(), key="output_path")

                st.button(
                    "View Output Directory",
                    key="view_output"
                )
            else:
                st.header("Input DEM")
                st.text_input(
                    "Load DEM (`.tif`) from Web URL (`https://`)",
                    key="imagePathInput1",
                    value="",
                    help="Load valid raster (`.tif`) from a URL (`https://`), the file will be downloaded",
                    on_change=app.input_change_callback
                ),  
                st.text_input(
                    "Locally saved DEM file (`.tif`)",
                    key="imagePathInput2",
                    value="",
                    help="Load valid DEM raster (`.tif`) in the same directory as `rillgen2d.py` or use a full path (e.g., `C:/yourname/Downloads/rasters/dem.tif`, or `/Users/yourname/Downloads/rasters/dem.tif`)",
                    on_change=app.input_change_callback
                )
                st.header("Parameters")
                #####            
                # If I switch to the file upload look at this for rasterio docs on in memory files: https://rasterio.readthedocs.io/en/latest/topics/memory-files.html
                st.button(
                    "Generate Parameters",
                    on_click=app.generate_parameters_button_callback,
                    key="genParameter")

                # Run Model
                st.button(
                    "Run Model",
                    disabled=not st.session_state.show_parameters,
                    on_click=self.run_callback,
                    args=(
                        st.session_state.imagePath,
                        st.session_state.console,
                        #st.session_state.flagformodeVar,
                    ),
                    key="goButton1"
                )
                
                # Open Map

                # Flag for dynamic mode variable
                st.checkbox(
                    "Enable Dynamic Mode (optional)",
                    value=st.session_state.flagformodeVar,
                    disabled=not st.session_state.show_parameters,
                    help="Default: unchecked, checked requires file named `dynamicinput`, \
                            unchecked uses 'peak mode' with spatially uniform rainfall",
                    key="flagformodeVar"
                )
                if st.session_state.flagformodeVar:
                    st.text_input("Path to required file named `dynamicinput`",
                                  key="modeInputPath",
                                  help="Path to required file named `dynamicinput` as either `.tif` or `.txt`")

                # Flag for routing method variable
                # fill increment variable
                st.number_input(
                    "Routing Method (0,1,2)):",
                    value=st.session_state.flagforroutingmethodVar,
                    step=1,
                    disabled=not st.session_state.show_parameters,
                    help="Default: ",
                    key="flagforroutingmethodVar"
                )


                # Flag for sheer strength equation variable
                st.checkbox(
                    "Rock Armor Sheer Strength",
                    value=st.session_state.flagforsheerstressequationVar,
                    disabled=not st.session_state.show_parameters,
                    help="Default: checked, checked uses [Pelletier et al. (2021)]() equation, \
                          unchecked implements the rock armor shear strength equation of [Haws and Erickson (2020)]()", 
                    key="flagforsheerstressequationVar"
                )
                # Flag for mask variable
                st.checkbox(
                    "Mask (optional)",
                    value=st.session_state.flagformaskVar,
                    disabled=not st.session_state.show_parameters,
                    help="Default: unchecked, checked requires file named `mask`. If a raster (`mask`) is provided, \
                          the run restricts the model to certain portions of the input DEM \
                          (`mask values = 1` means run the model, `0` means ignore these areas).",
                    key="flagformaskVar"
                )
                if st.session_state.flagformaskVar:
                    st.text_input("Path to required file named `mask`", key="maskPath")

                # flag for taucsoilandveg variable
                st.checkbox(
                    "Soil & Vegetation Layer (optional):",
                    value=st.session_state.flagfortaucsoilandvegVar,
                    disabled=not st.session_state.show_parameters,
                    help="Default: unchecked,checked requires file named `taucsoilandveg`. If a raster `taucsoilandveg` \
                          is provided the model applies the shear strength of soil and veg, \
                          unchecked means a fixed value will be used.",
                    key="flagfortaucsoilandvegVar"
                )
                if st.session_state.flagfortaucsoilandvegVar:
                    st.text_input("Path to required file named `taucsoilandveg`",
                                  key="taucsoilandvegPath",

                                  help="Path to required file named `taucsoilandveg` as either `.tif` or `.txt`")
                
                # Flag for d50 variable
                st.checkbox(
                    "Rock Armor Layer (optional):",
                    value=st.session_state.flagford50Var,
                    disabled=not st.session_state.show_parameters,
                    help="Default: unchecked, checked requires file named `d50`. If a raster `d50` is provided the model \
                          applies the median rock diameter, unchecked means a fixed value will be used.",
                    key="flagford50Var"
                )
                if st.session_state.flagford50Var:
                    st.text_input("Path to required file named `d50`",
                                  key="d50InputPath",

                                  help="Path to required file named `d50` as either `.tif` or `.txt")
                
                # Flag for rock thickness variable
                st.checkbox(
                    "Rock Thickness (optional):",
                    value=st.session_state.flagforrockthicknessVar,
                    disabled=not st.session_state.show_parameters,
                    help="Default: unchecked, checked requires file named `rockthickness`. If a raster (`rockthickness`) is provided \
                          the model applies variable rock thickness fractions, unchecked means \
                          a fixed rock thickness value will be used.",
                    key="flagforrockthicknessVar",
                )
                if st.session_state.flagforrockthicknessVar:
                    st.text_input("Path to required file named `rockthickness`",
                                  key="rockthicknessInputPath",
                                  help="Path to required file named `rockthickness` as either `.tif` or `.txt")

                # Flag for rockcover
                st.checkbox(
                    "Rock Cover (optional):",
                    value=st.session_state.flagforrockcoverVar,
                    disabled=not st.session_state.show_parameters,
                    help="Default: unchecked, checked requires file named `rockcover`. If a raster (`rockcover`) is provided \
                          the model applies the rock cover fraction, unchecked means \
                          a fixed value  will be used.",
                    key="flagforrockcoverVar",
                )
                if st.session_state.flagforrockcoverVar:
                    st.text_input("Path to required file named `rockcover`",
                                  key="rockcoverInputPath",
                                  help="Path to required file named `rockcover` as either `.tif` or `.txt")

                # fill increment variable
                st.number_input(
                    "Fill increment (m):",
                    value=st.session_state.fillincrementVar,
                    step=0.001,
                    format="%.3f",
                    disabled=not st.session_state.show_parameters,
                    help="Value in meters (m) used to fill pits and flats for the hydrologic correction step. \
                          `0.01` is a reasonable default value for lidar-based DEMs.",
                    key="fillincrementVar"
                )

                # minslope variable
                st.number_input(
                    "Minimum Slope Angle (degrees):",
                    value=st.session_state.minslopeVar,
                    step=0.001,
                    format="%.3f",
                    disabled=not st.session_state.show_parameters,
                    help="Value used to halt runoff from areas below a threshold slope steepness. \
                          Setting this value larger than 0 is useful for eliminating runoff from \
                          portions of the landscape that the user expects are too flat to produce \
                          significant runoff.",
                    key="minslopeVar"
                )

                # Expansion variable
                st.number_input(
                    "Expansion (pixels):",
                    value=st.session_state.expansionVar,
                    disabled=not st.session_state.show_parameters,
                    help="Value (pixels) used to expand the zone where rills are predicted in \
                          the output raster. This is useful for making the areas where rilling \
                          is predicted easier to see in the model output.",
                    key="expansionVar"
                )

                # yellowThreshold variable
                st.number_input(
                    "Rilling Threshold (f):",
                    value=st.session_state.yellowthresholdVar,
                    disabled=not st.session_state.show_parameters,
                    help="Threshold value of `f` used to indicate an area that is close to but \
                          less than the threshold for generating rills (yellow). The model will \
                          visualize any location with a `f` value between this value and 1 as \
                          potentially prone to rill generation (any area with a `f` value larger \
                          than 1 is considered prone to rill generation and is colored red).",
                    key='yellowthresholdVar'
                )

                # Lattice_size_x variable
                st.number_input(
                    "Lattice X (pixels):",
                    value=st.session_state.lattice_size_xVar,
                    disabled=True,
                    help="Pixels along the East to West direction in the DEM.",
                    key="lattice_size_xVar"
                )
                # Lattice_size_y variable
                st.number_input(
                    "Lattice Y (pixels):",
                    value=st.session_state.lattice_size_yVar,
                    disabled=True,
                    key="lattice_size_yVar",
                    help="Pixels along the North to South direction in the DEM.",
                )

                # Deltax variable
                st.number_input(
                    "DEM Resolution (m)",
                    value=st.session_state.deltaxVar,
                    disabled=not st.session_state.show_parameters,
                    help="Resolution (m) $\Delta$X of the DEM is derived from the `.tif` file metadata. \
                          Review for accuracy, do not change unless something looks wrong.",
                    key="deltaxVar"
                )

                # Nodata variable
                st.number_input(
                    "NoData (null)",
                    value=st.session_state.nodataVar,
                    disabled=not st.session_state.show_parameters,
                    help="the no data null value of the DEM (m) which will be masked, defaults to `-9999`",
                    key="nodataVar",
                )

                # Smoothing length variable
                st.number_input(
                    "Smoothing Length (pixels)",
                    value=st.session_state.smoothinglengthVar,
                    disabled=not st.session_state.show_parameters,
                    help="Length scale (pixels) for smoothing of the slope map. A length of 1 has no smoothing",
                    key="smoothinglengthVar"
                )

                # Manning's n variable
                st.number_input(
                    "Manning's n (m^(1/3)/s)",
                    value=st.session_state.manningsnVar,
                    disabled=not st.session_state.show_parameters,
                    help="Manning's N",
                    key="manningsnVar"
                )

                # Depth weight factor variable
                st.number_input(
                    "Depth Weight Factor",
                    value=st.session_state.depthweightfactorVar,
                    disabled=not st.session_state.show_parameters,
                    help="Depth weight factor",
                    key="depthweightfactorVar"
                )

                # number of slices variable
                st.number_input(
                    "Number of Slices",
                    value=st.session_state.numberofslicesVar,
                    disabled=not st.session_state.show_parameters,
                    help="Number of slices",
                    key="numberofslicesVar"
                )

                # number of sweeps variable
                st.number_input(
                    "Number of Sweeps",
                    value=st.session_state.numberofsweepsVar,
                    disabled=not st.session_state.show_parameters,
                    help="Number of sweeps",
                    key="numberofsweepsVar"
                )

                # Rain fixed variable
                st.number_input(
                    "Peak rainfall intensity (mm/hr).",
                    value=st.session_state.rainVar,
                    disabled=not st.session_state.show_parameters,
                    help="Uniform rainfall used in 'peak' mode. This value is ignored if 'Enable Dynamic Mode' flag is checked above.",
                    key="rainVar"
                )

                # tauc soil and vege fixed variable
                st.number_input(
                    "Threshold shear stress for soil and vegetation (Pa)",
                    value=st.session_state.taucsoilandvegeVar,
                    disabled=not st.session_state.show_parameters,
                    help="Tau C for soil and vegetation",
                    key="taucsoilandvegeVar"
                )

                # d50 fixed
                st.number_input(
                    "Median rock armor diameter (mm)",
                    value=st.session_state.d50Var,
                    disabled=not st.session_state.show_parameters,
                    help="This value is ignored if Rock Armor Flag (`d50`) is checked above.",
                    key="d50Var"
                )

                # Rock thickness fixed variable
                st.number_input(
                    "Rock Thickness (m)",
                    value=st.session_state.rockthicknessVar,
                    disabled=not st.session_state.show_parameters,
                    help="This value depth of rock armor. \
                          Defaults as 1 for continuous rock armors. \
                          This value is ignored if flag for 'Rock Thickness' is checked above.",
                    key="rockthicknessVar"
                )

                # Rock cover fixed variable
                st.number_input(
                    "Rock Cover (ratio)",
                    value=st.session_state.rockcoverVar,
                    disabled=not st.session_state.show_parameters,
                    help="This value indicates the fraction of area covered by rock armor. \
                          Will be 1 for continuous rock armors, <1 for partial rock cover. \
                          This value is ignored if flag for 'Rock Cover' is checked above.",
                    key="rockcoverVar"
                )
                
                # tanAngleOfInternalFriction fixed variable
                st.number_input(
                    "Tangent of the angle of internal friction",
                    value=st.session_state.tanangleofinternalfrictionVar,
                    disabled=not st.session_state.show_parameters,
                    help="Values typically in the range of 0.5 to 0.8.",
                    key="tanangleofinternalfrictionVar"
                )

                # b variable
                st.number_input(
                    "Coefficient of runoff to contributing area (b)",
                    value=st.session_state.bVar,
                    disabled=not st.session_state.show_parameters,
                    help="This value is the coefficient in the model component that predicts the relationship between runoff and contributing area.",
                    key="bVar"
                )
                # c variable
                st.number_input(
                    "Exponent of runoff to contributing area (c)",
                    value=st.session_state.cVar,
                    disabled=not st.session_state.show_parameters,
                    help="This value is the exponent in the model component that predicts the relationship between runoff and contributing area.",
                    key="cVar"
                )

                # rill width coefficient variable
                st.number_input(
                    "Rill Width Coefficient (m)",
                    value=st.session_state.rillwidthcoefficientVar,
                    disabled=not st.session_state.show_parameters,
                    help="The width of rills (m) as they begin to form. This value is used to localize water flow to a width less than the width of a pixel. For example, if deltax = 1 m and rillwidth = 20 cm then the flow entering each pixel is assumed, for the purposes of rill development, to be localized in a width equal to one fifth of the pixel width.",
                    key="rillwidthcoefficientVar"
                )

                # rill width exponent variable
                st.number_input(
                    "Rill Width Exponent (m)",
                    value=st.session_state.rillwidthexponentVar,
                    disabled=not st.session_state.show_parameters,
                    help="The width of rills (m) as they begin to form. This value is used to localize water flow to a width less than the width of a pixel. For example, if deltax = 1 m and rillwidth = 20 cm then the flow entering each pixel is assumed, for the purposes of rill development, to be localized in a width equal to one fifth of the pixel width.",
                    key="rillwidthexponentVar"
                )

                self.parameterButton = st.button(
                    'Generate Parameters',
                    on_click=self.generate_parameters,
                    disabled=not st.session_state.show_parameters,
                    key="parameterButton"
                )
                self.goButton = st.button(
                    'Run Model',
                    disabled=not st.session_state.show_parameters,
                    on_click=self.run_callback,
                    args=(
                        st.session_state.imagePath,
                        st.session_state.console,
                        #st.session_state.flagformodeVar,
                    ),
                    key="goButton2"
                )

                st.caption('NOTE: The hydrologic correction step can take a long time if there are lots of depressions in the input DEM and/or if the'
                           + ' landscape is very steep. RILLGEN2D can be sped up by increasing the value of "fillincrement" or by performing the hydrologic correction step in a'
                           + ' different program (e.g., ArcGIS or TauDEM) prior to input into RILLGEN2D.')
        # The width of rills (in m) as they begin to form. This value is used to localize water flow to a width less than the width of a pixel.
        # For example, if deltax = 1 m and rillwidth = 20 cm then the flow entering each pixel is assumed, for the purposes of rill development, to be localized in a width equal to one fifth of the pixel width.
        ########################### ^MAIN TAB^ ###########################

    def validate_file_paths(self):
        flag_path_pairs = [
            ("flagformodeVar", "modeInputPath"),
            ("flagford50Var", "d50InputPath"),
            ("flagforrockthicknessVar", "rockthicknessInputPath"),
            ("flagforrockcoverVar", "rockcoverInputPath"),
            ("flagfortaucsoilandvegVar", "taucsoilandvegPath"),
        ]
        valid_paths = True
        for flag, path in flag_path_pairs:

            if st.session_state[flag] and not (st.session_state[path] or Path.is_file(Path(st.session_state[path]))):
                valid_paths = False
                st.error(
                    f"Invalid path for {path}, if you don't want to use this input, uncheck {flag}")
        return valid_paths

    def delete_temp_dir(self):
        path = Path.cwd() / "tmp"
        if path.exists():
            shutil.rmtree(path.as_posix())

    def input_change_callback(self):
        self.initialize_parameter_fields(force=True)
        t = Thread(target=self.delete_temp_dir)
        t.start()
        for key in st.session_state:
            if key == "imagePathInput1" or key == "imagePathInput2" or key == "imagePath":
                continue
            del st.session_state[key]
        t.join()
        st.session_state.console_log = []
        st.session_state.console = Queue()
        st.session_state.rillgen2d = None

    def generate_parameters(self):
        """Generate parameters.txt file"""
        path = Path.cwd() / 'parameters.txt'
        if path.exists():
            Path.unlink(path)
        f = open('parameters.txt', 'w+')
        f.write(str(int(st.session_state.flagformodeVar)) +
                '\t /* Flag for mode out */ \n')
        f.write(str(int(st.session_state.flagforroutingmethodVar)) +
                '\t /* Flag for routing method out */ \n')
        f.write(str(int((st.session_state.flagforsheerstressequationVar))) +
                '\t /* Flag for sheer stress equation out */ \n')
        f.write(str(int(st.session_state.flagformaskVar)) +
                '\t /* Flag for mask out */ \n')
        f.write(str(int(st.session_state.flagfortaucsoilandvegVar)) +
                '\t /* Flag for taucsoilandveg out */ \n')
        f.write(str(int(st.session_state.flagford50Var)) +
                '\t /* Flag for d50 out */ \n')
        f.write(str(int(st.session_state.flagforrockthicknessVar)) +
                '\t /* Flag for rockthickness out */ \n')
        f.write(str(int(st.session_state.flagforrockcoverVar)) +
                '\t /* Flag for rockcover out */ \n')
        f.write(str(st.session_state.fillIncrementVar).replace(
            "\n", "") + '\t /* fillincrement out */ \n')
        f.write(str(st.session_state.minslopeVar).replace(
            "\n", "") + '\t /* minslope out */ \n')
        f.write(str(st.session_state.expansionVar).replace(
            "\n", "") + '\t /* Expansion out */ \n')
        f.write(str(st.session_state.yellowthresholdVar).replace(
            "\n", "") + '\t /* Yellow threshold out */ \n')
        f.write(str(st.session_state.lattice_size_xVar).replace(
            "\n", "") + '\t /* Lattice Size X out */ \n')
        f.write(str(st.session_state.lattice_size_yVar).replace(
            "\n", "") + '\t /* Lattice Size Y out */ \n')
        f.write(str(st.session_state.deltaxVar).replace(
            "\n", "") + '\t /* Delta X out */ \n')
        f.write(str(st.session_state.nodataVar).replace(
            "\n", "") + '\t /* nodata out */ \n')
        f.write(str(st.session_state.smoothinglengthVar).replace(
            "\n", "") + '\t /* smoothing length out */ \n')
        f.write(str(st.session_state.manningsnVar).replace(
            "\n", "") + '\t /* manningsn out */ \n')
        f.write(str(st.session_state.depthweightfactorVar).replace(
            "\n", "") + '\t /* depth weight factor out */ \n')
        f.write(str(st.session_state.numberofslicesVar).replace(
            "\n", "") + '\t /* number of slices out */ \n')
        f.write(str(st.session_state.numberofsweepsVar).replace(
            "\n", "") + '\t /* number of sweeps out */ \n')
        f.write(str(st.session_state.rainVar).replace(
            "\n", "") + '\t /* Rain out */ \n')
        f.write(str(st.session_state.taucsoilandvegeVar).replace(
            "\n", "") + '\t /* tauc soil and vege out */ \n')
        f.write(str(st.session_state.d50Var).replace(
            "\n", "") + '\t /* d50 out */ \n')
        f.write(str(st.session_state.rockthicknessVar).replace(
            "\n", "") + '\t /* rock thickness out */ \n')
        f.write(str(st.session_state.rockCoverVar).replace(
            "\n", "") + '\t /* rock cover out */ \n')
        f.write(str(st.session_state.tanangleofinternalfrictionVar).replace(
            "\n", "") + '\t /* tangent of the angle of internal friction out*/ \n')
        f.write(str(st.session_state.bVar).replace(
            "\n", "") + '\t /* b out */ \n')
        f.write(str(st.session_state.cVar).replace(
            "\n", "") + '\t /* c out */ \n')
        f.write(str(st.session_state.rillwidthcoefficientVar).replace(
            "\n", "") + '\t /* rill width coefficient out */ \n')
        f.write(str.st_session_state.rillwidthexponentVar.replace(
            "\n", "") + '\t /* rill width exponent out */ \n')
        st.success("Generated parameters.txt\n\n"+'\n'+"Click on Run Model\n")
        f.close()

    def run_callback(self, imagePath, console):
        """Run callback"""
        no_error = True
        if not self.validate_file_paths():
            no_error = False
        if st.session_state.flagformaskVar:
            try:
                self.getMask(st.session_state.maskPath)
            except:
                st.error(
                    "Error: Mask file not found. Please check the path and try again.")
                return
        if not no_error:
            return
        rg2d.generate_input_txt_file(
            st.session_state.flagformodeVar,
            st.session_state.flagforroutingmethodVar,
            st.session_state.flagforsheerstressequationVar,
            st.session_state.flagformaskVar,
            st.session_state.flagfortaucsoilandvegVar,
            st.session_state.flagford50Var,
            st.session_state.flagforrockthicknessVar,
            st.session_state.flagforrockcoverVar,
            st.session_state.fillincrementVar,
            st.session_state.minslopeVar,
            st.session_state.expansionVar,
            st.session_state.yellowthresholdVar,
            st.session_state.lattice_size_xVar,
            st.session_state.lattice_size_yVar,
            st.session_state.deltaxVar,
            st.session_state.nodataVar,
            st.session_state.smoothinglengthVar,
            st.session_state.manningsnVar,
            st.session_state.depthweightfactorVar,
            st.session_state.numberofslicesVar,
            st.session_state.numberofsweepsVar,
            st.session_state.rainVar,
            st.session_state.taucsoilandvegeVar,
            st.session_state.d50Var,
            st.session_state.rockthicknessVar,
            st.session_state.rockcoverVar,
            st.session_state.tanangleofinternalfrictionVar,
            st.session_state.bVar,
            st.session_state.cVar,
            st.session_state.rillwidthcoefficientVar,
            st.session_state.rillwidthexponentVar,
            st.session_state.console
        )

        if st.session_state.rillgen2d is None or not st.session_state.rillgen2d.is_alive():
            st.session_state.rillgen2d = Thread(
                target=rg2d.main, args=(imagePath, console))
            st.session_state.rillgen2d.start()

# update display of the bash console
# change the color of the background of display_console to black
    def display_console(self):
        """Update the console with the latest 6 messages"""
        while not st.session_state.console.empty():
            message = st.session_state.console.get()
            if message:
                st.session_state.console_log.append(message)
        with st.expander("Terminal", True):
            for line in st.session_state.console_log[-7:-1:1]:
                st.write(line)
            st.markdown(
            """
            <style>
            .streamlit-expanderContent > div > div > div {
                background-color: black;
                color: white;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )

    def display_preview(self):
        """Preview of the landscape."""
        imagePath = "hillshade.png"
        imagePath = "./" + "tmp/" * \
            int(not Path(imagePath).is_file()) + imagePath
        with st.expander("Check DEM landscape", True):
            if st.session_state.hillshade_generated:
                st.image(
                    PIL.Image.open(r"./hillshade.png"),
                    caption="Hillshade generated from expected DEM raster")


    # display the Leaflet Folium Map
    def display_map(self):
        """Display the raster map """
        with st.container():
            st.components.html(Path("./map.html").read_text(),
                            height=500, width=700)
            st.button(
                "Save Output", key="saveButton",
                on_click=self.save_callback
            )
    # Add the Legend below the Leaflet Map for Tau and F
    def display_tau(self):
        """Display the legends"""
        imagePath = "color-relief_tau.png"
        imagePath = "./" + "tmp/" * \
            int(not Path(imagePath).is_file()) + imagePath
        with st.expander("Check Tau Results", True):
            if st.session_state.hillshade_generated:
                st.image(
                    PIL.Image.open(r"color-relief_tau.png"),
                    caption="Tau C (Pa)")

    def view_output(self, output_path):
        if not (Path(output_path) / "map.html").exists():
            st.warning("Output file not found at " + output_path)
        else:
            with st.container():
                st.components.html((Path(output_path) / "map.html").read_text())

    def app_is_running(self):
        return \
            "rillgen2d" in st.session_state \
            and st.session_state.rillgen2d\
            and st.session_state.rillgen2d.is_alive()

    def main_page(self):
        """Main page of the app."""
        st.title("rillgen2d")
        app_tab, readme = st.tabs(["Parameters", "User Manual"])
        self.populate_parameters_tab()
        with app_tab:
            if st.session_state.view_output_checkbox and st.session_state.view_output:
                self.view_output(st.session_state.output_path)
            else:
                self.display_console()
                self.display_preview()
                if Path("./map.html").exists() and "rillgen2d" in st.session_state and st.session_state.rillgen2d:
                    self.display_map()
                    self.display_tau()

        if self.app_is_running():
            st.experimental_rerun()


app = App()
app.main_page()
