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
import rillgen2d as rg2d
import streamlit.components.v1 as components


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

        self.initialize_parameter_fields()

    def initialize_parameter_fields(self, force=False):
        """
        Initialize the parameter fields to the correct types
        """
        if 'flagForEquationVar' not in st.session_state or force:
            st.session_state.flagForEquationVar = True
        if 'flagforDynamicModeVar' not in st.session_state or force:
            st.session_state.flagforDynamicModeVar = False
        if 'flagForMaskVar' not in st.session_state or force:
            st.session_state.flagForMaskVar = False
            st.session_state.flagForTaucSoilAndVegVar = False
            st.session_state.flagFord50Var = False
            st.session_state.flagForRockCoverVar = False
            st.session_state.fillIncrementVar = 0.0
            st.session_state.minSlopeVar = 0.0
            st.session_state.expansionVar = 0
            st.session_state.yellowThresholdVar = 0.0
            st.session_state.lattice_size_xVar = 0
            st.session_state.lattice_size_yVar = 0
            st.session_state.deltaXVar = 0.0
            st.session_state.noDataVar = 0
            st.session_state.smoothingLengthVar = 0
            st.session_state.rainVar = 0
            st.session_state.taucSoilAndVegeVar = 0
            st.session_state.d50Var = 0.0
            st.session_state.rockCoverVar = 0
            st.session_state.tanAngleOfInternalFrictionVar = 0.0
            st.session_state.bVar = 0
            st.session_state.cVar = 0.0
            st.session_state.rillWidthVar = 0.0
            st.session_state.show_parameters = False

    def get_parameter_values(self):
        # TODO I can just hardcode these values? I guess the value is that the user can define the defaults?
        f = open('input.txt', 'r')
        st.session_state.flagForEquationVar = int(f.readline().strip())
        st.session_state.flagforDynamicModeVar = int(f.readline().strip())
        st.session_state.flagForMaskVar = int(f.readline().strip())
        st.session_state.flagForTaucSoilAndVegVar = int(f.readline().strip())
        st.session_state.flagFord50Var = int(f.readline().strip())
        st.session_state.flagForRockCoverVar = int(f.readline().strip())
        st.session_state.fillIncrementVar = float(f.readline().strip())
        st.session_state.minSlopeVar = float(f.readline().strip())
        st.session_state.expansionVar = int(f.readline().strip())
        st.session_state.yellowThresholdVar = float(f.readline().strip())
        # st.session_state.lattice_size_xVar = self.dimensions[1]
        # st.session_state.lattice_size_yVar = self.dimensions[0]
        f.readline()
        f.readline()
        st.session_state.deltaXVar = float(f.readline().strip())
        st.session_state.noDataVar = int(f.readline().strip())
        st.session_state.smoothingLengthVar = int(f.readline().strip())
        st.session_state.rainVar = int(f.readline().strip())
        st.session_state.taucSoilAndVegeVar = int(f.readline().strip())
        st.session_state.d50Var = float(f.readline().strip())
        st.session_state.rockCoverVar = int(f.readline().strip())
        st.session_state.tanAngleOfInternalFrictionVar = float(
            f.readline().strip())
        st.session_state.bVar = int(f.readline().strip())
        st.session_state.cVar = float(f.readline().strip())
        st.session_state.rillWidthVar = float(f.readline().strip())
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
            st.sesson_state.console.put("Error downloading from url")
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
        imagePath = st.session_state.imagePathInput
        if imagePath.startswith("http"):
            print("here")
            imagePath = str(self.get_image_from_url(imagePath))
        if imagePath.endswith("gz"):
            tarpath = imagePath
            imagePath = self.extract_geotiff_from_tarfile(
                tarpath, Path(imagePath))
        else:
            imagePath = Path(imagePath)
        self.get_parameter_values()
        filename, st.session_state.lattice_size_xVar, st.session_state.lattice_size_yVar =\
            rg2d.save_image_as_txt(imagePath, st.session_state.console)
        rg2d.hillshade_and_color_relief(filename, st.session_state.console)
        st.session_state.hillshade_generated = True
        st.session_state.imagePath = imagePath

    def save_callback(self):
        rg2d.save_output()

    def getMask(self, filepath):
        # TODO Figure out input for filepath
        if st.session_state.flagForMaskVar == 1:
            st.text(
                ("Choose a mask.tif file\n\n"))
            try:
                maskfile = Path(filepath)
                if maskfile.suffix == '.tar' or maskfile.suffix == '.gz':
                    maskfile = self.extract_geotiff_from_tarfile(
                        maskfile, Path.cwd())

                shutil.copyfile(maskfile, Path.cwd() / "mask.tif")
                (
                    ("maskfile: is: " + str(maskfile) + "\n\n"))
            except Exception:
                (
                    ("Invalid mask.tif file\n\n"))

    def populate_parameters_tab(self):
        """Populate the second tab in the application with tkinter widgets. This tab holds editable parameters
        that will be used to run the rillgen2dwitherode.c script. lattice_size_x and lattice_size_y are read in from the
        geometry of the geotiff file"""

        # Flag for equation variable
        with st.sidebar:
            st.checkbox(
                "Equation",
                value=st.session_state.flagForEquationVar,
                disabled=not st.session_state.show_parameters,
                help="Default: checked,\
                        implements the rock armor shear strength equation of Haws and Erickson (2020),\
                        if checked uses Pelletier et al. (2021) equation",
                key="flagForEquationVar"
            )

            # Flag for dynamic node variable
            st.checkbox(
                "Enable Dynamic Mode",
                value=st.session_state.flagforDynamicModeVar,
                disabled=not st.session_state.show_parameters,
                help='Default: unchecked, Note: when checked uses file "dynamicinput.txt".\
                        File must be provided in the same directory as the rillgen2d.py. When flag is unchecked uses "peak mode" with \
                        spatially uniform rainfall.',
                key="flagforDynamicModeVar"
            )
            # Flag for mask variable
            st.checkbox(
                "Mask",
                value=st.session_state.flagForMaskVar,
                disabled=not st.session_state.show_parameters,
                help='Default: unchecked, If a raster (mask.tif) is provided, the run restricts the model to certain portions of the input DEM\
                        (mask values = 1 means run the model, 0 means ignore these areas).',
                key="flagForMaskVar"
            )
            if st.session_state.flagForMaskVar:
                st.text_input("Path to mask file", key="maskPath")

            # flagForTaucSoilAndVeg variable
            st.checkbox(
                "Tau C soil & veg:",
                value=st.session_state.flagForTaucSoilAndVegVar,
                disabled=not st.session_state.show_parameters,
                help="Default: unchecked, If a raster (taucsoilandveg.txt) is provided the model applies the shear strength of soil and veg, unchecked means a fixed value will be used.",
                key="flagForTaucSoilAndVegVar"
            )
            # Flag for d50 variable
            st.checkbox(
                "d50:",
                value=st.session_state.flagFord50Var,
                disabled=not st.session_state.show_parameters,
                help='Default: unchecked, If a raster (d50.txt) is provided the model applies the median rock diameter, unchecked means a fixed value will be used.',
                key="flagFord50Var"
            )

            # Flag for rockcover
            st.checkbox(
                "Rock Cover:",
                value=st.session_state.flagForRockCoverVar,
                disabled=not st.session_state.show_parameters,
                help="",
                key="flagForRockCoverVar",
            )

            # fillIncrement variable
            st.number_input(
                "Fill increment:",
                value=st.session_state.fillIncrementVar,
                disabled=not st.session_state.show_parameters,
                help="Value in meters (m) used to fill in pits and flats for hydrologic correction. 0.01 m is a reasonable default value for lidar-based DEMs.",
                key="fillIncrementVar"
            )

            # minslope variable
            st.number_input(
                "Min Slope:",
                value=st.session_state.minSlopeVar,
                disabled=not st.session_state.show_parameters,
                help="Value (unitless) used to halt runoff from areas below a threshold slope steepness. Setting this value larger than 0 is useful for eliminating runoff from portions of the landscape that the user expects are too flat to produce significant runoff.",
                key="minSlopeVar"
            )
            # Expansion variable
            st.number_input(
                "Expansion:",
                value=st.session_state.expansionVar,
                disabled=not st.session_state.show_parameters,
                help="Value (pixel) used to expand the zones where rills are predicted in the output raster. This is useful for making the areas where rilling is predicted easier to see in the model output.",
                key="expansionVar"
            )
            # yellowThreshold variable
            st.number_input(
                "Yellow Threshold:",
                value=st.session_state.yellowThresholdVar,
                disabled=not st.session_state.show_parameters,
                help="Threshold value of f used to indicate an area that is close to but less than the threshold for generating rills. The model will visualize any location with a f value between this value and 1 as potentially prone to rill generation (any area with a f value larger than 1 is considered prone to rill generation and is colored red).",
                key='yellowThresholdVar'
            )

            # Lattice_size_x variable
            st.number_input(
                "Lattice Size X:",
                value=st.session_state.lattice_size_xVar,
                disabled=True,
                help="Pixels along the east-west direction in the DEM.",
                key="lattice_size_xVar"
            )
            # Lattice_size_y variable
            st.number_input(
                "Lattice Size Y:",
                value=st.session_state.lattice_size_yVar,
                disabled=True,
                key="lattice_size_yVar",
                help="Pixels along the north-south direction in the DEM.",
            )

            # Deltax variable
            st.number_input(
                "$\Delta$X",
                value=st.session_state.deltaXVar,
                disabled=not st.session_state.show_parameters,
                help="Resolution (meters)  of the DEM and additional optional raster inputs.",
                key="deltaXVar"
            )

            # Nodata variable
            st.number_input(
                "nodata",
                value=st.session_state.noDataVar,
                disabled=not st.session_state.show_parameters,
                help="Elevation less than or equal to the nodata value will be masked.",
                key="noDataVar",
            )

            # Smoothinglength variable
            st.number_input(
                "Smoothing Length",
                value=st.session_state.smoothingLengthVar,
                disabled=not st.session_state.show_parameters,
                help="Length scale (pixels) for smoothing of the slope map. A length of 1 has no smoothing",
                key="smoothingLengthVar"
            )
            # Rain fixed variable
            st.number_input(
                "Rain Fixed",
                value=st.session_state.rainVar,
                disabled=not st.session_state.show_parameters,
                help="Peak rainfall intensity (mm/hr). This value is ignored if flag is checked.",
                key="rainVar"
            )

            # tauc soil and vege fixed variable
            st.number_input(
                "tauc soil and vege fixed",
                value=st.session_state.taucSoilAndVegeVar,
                disabled=not st.session_state.show_parameters,
                help="Threshold shear stress for soil and vegetation.",
                key="taucSoilAndVegeVar"
            )

            # d50 fixed
            st.number_input(
                "d50 Fixed",
                value=st.session_state.d50Var,
                disabled=not st.session_state.show_parameters,
                help="Median rock armor diameter (in mm). This value is ignored if flag for d50 is checked.",
                key="d50Var"
            )

            # Rockcover fixed variable
            st.number_input(
                "Rock Cover",
                value=st.session_state.rockCoverVar,
                disabled=not st.session_state.show_parameters,
                help="This value indicates the fraction of area covered by rock armor. Will be 1 for continuous rock armors, less than one for partial rock cover. This value is ignored if flag for rock cover is checked",
                key="rockCoverVar"
            )
            # tanAngleOfInternalFriction fixed variable
            st.number_input(
                "tanAngleOfInternalFriction",
                value=st.session_state.tanAngleOfInternalFrictionVar,
                disabled=not st.session_state.show_parameters,
                help="Tangent of the angle of internal friction. Values will typically be in the range of 0.5-0.8.",
                key="tanAngleOfInternalFrictionVar"
            )

            # b variable
            st.number_input(
                "b",
                value=st.session_state.bVar,
                disabled=not st.session_state.show_parameters,
                help="This value is the coefficient in the model component that predicts the relationship between runoff and contributing area.",
                key="bVar"
            )
            # c variable
            st.number_input(
                "c",
                value=st.session_state.cVar,
                disabled=not st.session_state.show_parameters,
                help="This value is the exponent in the model component that predicts the relationship between runoff and contributing area.",
                key="cVar"
            )

            # rillWidth variable
            st.number_input(
                "rillWidth",
                value=st.session_state.rillWidthVar,
                disabled=not st.session_state.show_parameters,
                help="The width of rills (in m) as they begin to form. This value is used to localize water flow to a width less than the width of a pixel. For example, if deltax = 1 m and rillwidth = 20 cm then the flow entering each pixel is assumed, for the purposes of rill development, to be localized in a width equal to one fifth of the pixel width.",
                key="rillWidthVar"
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
                    st.session_state.flagforDynamicModeVar,
                ),
                key="goButton"
            )

            st.text('NOTE: The hydrologic correction step can take a long time if there are lots of depressions in the input DEM and/or if the'
                    + ' landscape is very steep. RILLGEN2D can be sped up by increasing the value of "fillIncrement" or by performing the hydrologic correction step in a'
                    + ' different program (e.g., ArcGIS or TauDEM) prior to input into RILLGEN2D.')
        # The width of rills (in m) as they begin to form. This value is used to localize water flow to a width less than the width of a pixel.
        # For example, if deltax = 1 m and rillwidth = 20 cm then the flow entering each pixel is assumed, for the purposes of rill development, to be localized in a width equal to one fifth of the pixel width.
        ########################### ^MAIN TAB^ ###########################

    def delete_temp_dir(self):
        path = Path.cwd() / "tmp"
        if path.exists():
            shutil.rmtree(path.as_posix())

    def input_change_callback(self):
        self.initialize_parameter_fields(force=True)
        t = Thread(target=self.delete_temp_dir)
        t.start()
        for key in st.session_state:
            if key == "imagePathInput" or key == "imagePath":
                continue
            del st.session_state[key]
        t.join()
        st.session_state.console_log = []
        st.session_state.console = Queue()
        st.session_state.rillgen2d = None

    def generate_parameters(self):
        """Generate the parameters.txt file using the flags from the second tab"""
        path = Path.cwd() / 'parameters.txt'
        if path.exists():
            Path.unlink(path)
        f = open('parameters.txt', 'w+')
        f.write(str(int(st.session_state.flagForEquationVar)) +
                '\t /* Flag for equation out */ \n')
        f.write(str(int((st.session_state.flagforDynamicModeVar))) +
                '\t /* Flag for dynamicmode out */ \n')
        f.write(str(int(st.session_state.flagForMaskVar)) +
                '\t /* Flag for mask out */ \n')
        f.write(str(int(st.session_state.flagForTaucSoilAndVegVar)) +
                '\t /* Flag for taucsoilandveg out */ \n')
        f.write(str(int(st.session_state.flagFord50Var)) +
                '\t /* Flag for d50 out */ \n')
        f.write(str(int(st.session_state.flagForRockCoverVar)) +
                '\t /* Flag for rockcover out */ \n')
        f.write(str(st.session_state.fillIncrementVar).replace(
            "\n", "") + '\t /* fillIncrement out */ \n')
        f.write(str(st.session_state.minSlopeVar).replace(
            "\n", "") + '\t /* minslope out */ \n')
        f.write(str(st.session_state.expansionVar).replace(
            "\n", "") + '\t /* Expansion out */ \n')
        f.write(str(st.session_state.yellowThresholdVar).replace(
            "\n", "") + '\t /* Yellow threshold out */ \n')
        f.write(str(st.session_state.lattice_size_xVar).replace(
            "\n", "") + '\t /* Lattice Size X out */ \n')
        f.write(str(st.session_state.lattice_size_yVar).replace(
            "\n", "") + '\t /* Lattice Size Y out */ \n')
        f.write(str(st.session_state.deltaXVar).replace(
            "\n", "") + '\t /* Delta X out */ \n')
        f.write(str(st.session_state.noDataVar).replace(
            "\n", "") + '\t /* nodata out */ \n')
        f.write(str(st.session_state.smoothingLengthVar).replace(
            "\n", "") + '\t /* smoothing length out */ \n')
        f.write(str(st.session_state.rainVar).replace(
            "\n", "") + '\t /* Rain out */ \n')
        f.write(str(st.session_state.taucSoilAndVegeVar).replace(
            "\n", "") + '\t /* tauc soil and vege out */ \n')
        f.write(str(st.session_state.d50Var).replace(
            "\n", "") + '\t /* d50 out */ \n')
        f.write(str(st.session_state.rockCoverVar).replace(
            "\n", "") + '\t /* rock cover out */ \n')
        f.write(str(st.session_state.tanAngleOfInternalFrictionVar).replace(
            "\n", "") + '\t /* tangent of the angle of internal friction out*/ \n')
        f.write(str(st.session_state.bVar).replace(
            "\n", "") + '\t /* b out */ \n')
        f.write(str(st.session_state.cVar).replace(
            "\n", "") + '\t /* c out */ \n')
        f.write(str(st.session_state.rillWidthVar).replace(
            "\n", "") + '\t /* rill width out */ \n')
        st.success("Generated parameters.txt\n\n"+'\n'+"Click on Run Model\n")
        f.close()

    def run_callback(self, imagePath, console, flagForDyanmicModeVar):
        rg2d.generate_input_txt_file(
            st.session_state.flagForEquationVar,
            st.session_state.flagforDynamicModeVar,
            st.session_state.flagForMaskVar,
            st.session_state.flagForTaucSoilAndVegVar,
            st.session_state.flagFord50Var,
            st.session_state.flagForRockCoverVar,
            st.session_state.fillIncrementVar,
            st.session_state.minSlopeVar,
            st.session_state.expansionVar,
            st.session_state.yellowThresholdVar,
            st.session_state.lattice_size_xVar,
            st.session_state.lattice_size_yVar,
            st.session_state.deltaXVar,
            st.session_state.noDataVar,
            st.session_state.smoothingLengthVar,
            st.session_state.rainVar,
            st.session_state.taucSoilAndVegeVar,
            st.session_state.d50Var,
            st.session_state.rockCoverVar,
            st.session_state.tanAngleOfInternalFrictionVar,
            st.session_state.bVar,
            st.session_state.cVar,
            st.session_state.rillWidthVar,
            st.session_state.console
        )
        if st.session_state.flagForMaskVar:
            self.getMask()
        if st.session_state.rillgen2d is None or not st.session_state.rillgen2d.is_alive():
            st.session_state.rillgen2d = Thread(
                target=rg2d.main, args=(imagePath, console, flagForDyanmicModeVar))
            st.session_state.rillgen2d.start()


app = App()
st.title("Rillgen2d")


app_tab, readme = st.tabs(["Rillgen2d App", "Readme"])
preview_col, console_col = st.columns([4, 3])
while not st.session_state.console.empty():
    st.session_state.console_log.append(st.session_state.console.get())
with st.sidebar:
    st.header("Parameters")
    st.text_input(
        "Image Path",
        key="imagePathInput",
        value="/Users/elliothagyard/Downloads/output2.tif",
        on_change=app.input_change_callback
    )
    # If I switch to the file upload look at this for rasterio docs on in memoroy files: https://rasterio.readthedocs.io/en/latest/topics/memory-files.html
    generate_parameters_button = st.button(
        "Generate Parameters",
        on_click=app.generate_parameters_button_callback,
        key="genParameter")
    app.populate_parameters_tab()

    #   st.text_input(label, value="",
    #   max_chars=None, key=None, type="default",
    #   help=None, autocomplete=None, on_change=None,
    #   args=None, kwargs=None, *, placeholder=None, disabled=False, label_visibility="visible")
with app_tab:
    with console_col:
        with st.expander("Console", True):
            for line in st.session_state.console_log[-5:-1:1]:
                st.write(line)
    with preview_col:
        with st.expander("Hillshade", True):
            if st.session_state.hillshade_generated:
                st.image(
                    PIL.Image.open(r"./hillshade.png"),
                    caption="Simulated lighting to visualize selected area",
                    width=400
                )
    with st.container():
        if Path("./map.html").exists() and "rillgen2d" in st.session_state and st.session_state.rillgen2d:
            components.html(Path("./map.html").read_text(),
                            height=500, width=700)
            st.button(
                "Save Output", key="saveButton",
                on_click=app.save_callback
            )
    if "rillgen2d" in st.session_state and st.session_state.rillgen2d:
        if st.session_state.rillgen2d.is_alive():
            st.experimental_rerun()
