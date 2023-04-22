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
    from parameters import Parameters
except ModuleNotFoundError:
    os.chdir("..")
    import rillgen2d as rg2d
    from parameters import Parameters
import streamlit.components.v1 as components

def callback_exception_wrapper(callback):
    def wrapper(*args, **kwargs):
        try:
            callback(*args, **kwargs)
        except Exception as e:
            st.error(e)
            st.error(
                str(type(e).__name__)
            )       
            # TypeError
            st.error( str(__file__)) 
            if os.curdir.endswith("tmp"):
                os.chdir("..")
    return wrapper


class Frontend:
    def __init__(self):
    
        if "parameters" not in st.session_state:
            st.session_state.parameters = Parameters()
            st.session_state.console_log = []
            st.session_state.console = Queue()
            st.session_state.rillgen2d = None
        # Alias for session state Parameters object, to make it easier to access
        self.params = st.session_state.parameters
    """
        Broad error handling for callbacks
    """

    def get_image_from_url(self, url):
        """Given the url of an image when a raster is generated or located online,
        extract the geotiff image from the url and display it on the canvas """
        r = requests.get(url, allow_redirects=True)
        if not r.ok:
            raise Exception(
                "Invalid URL, request responded with status code: " +
                str(r.status_code) + " " + r.reason
            )
        path = Path.cwd()
        if path.as_posix().endswith('tmp'):
            path = path.parent
        downloaded = os.path.basename(url)
        img = downloaded
        if not any([downloaded.endswith(ext) for ext in [".tif", ".tiff", ".gz"]]):
            raise Exception("Invalid URL, file must be a geotiff or gzipped geotiff. Downloadeded file: " + downloaded)
        
        open((path / downloaded), 'wb').write(r.content)
        if downloaded.endswith(".gz"):
            tarpath = path / downloaded
            imagefile = self.extract_geotiff_from_tarfile(tarpath, path)
            os.remove(path / downloaded)
        else:
            imagefile = (path / img)
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
    
    @callback_exception_wrapper
    def generate_parameters_callback(self):
        imagePath = st.session_state.imagePathInput
        if imagePath.startswith("http"):
            imagePath = str(self.get_image_from_url(imagePath))
            
        if imagePath.endswith("gz"):
            tarpath = imagePath
            imagePath = self.extract_geotiff_from_tarfile(tarpath, Path(imagePath))
        else:
            imagePath = Path(imagePath)
        self.params.getParametersFromFile("input.txt")

        filename, lattice_size_xVar, lattice_size_yVar = rg2d.save_image_as_txt(imagePath, st.session_state.console)
        self.params.update_value("lattice_size_x", lattice_size_xVar)
        self.params.update_value("lattice_size_y", lattice_size_yVar)
        if filename is None:
            raise Exception("Invalid image file")
        
        rg2d.hillshade_and_color_relief(filename, st.session_state.console)
        st.session_state.hillshade_generated = True
        st.session_state.imagePath = imagePath
        self.params.display_parameters = True

    def save_callback(self):
        rg2d.save_output()

    def getMask(self, filepath):
        # TODO Figure out input for filepath
        if self.params.get_value("mask_flag"):
            try:
                maskfile = Path(filepath)
                if maskfile.suffix == '.tar' or maskfile.suffix == '.gz':
                    maskfile = self.extract_geotiff_from_tarfile(
                        maskfile, Path.cwd())

                shutil.copyfile(maskfile, Path.cwd() / "mask.tif")
                st.session_state.console.put("maskfile: is: " + str(maskfile))
            except Exception:
                raise Exception("Invalid mask.tif file")

    def update_value_from_input(self, attribute):
        self.params.update_value(attribute, st.session_state[attribute])
    
    def create_check_box(self, input):
        return st.checkbox(
            input["display_name"],
            value=input["value"],
            disabled=not self.params.display_parameters,
            help=input["help"],
            key=input["name"],
            args=(self, input["name"]),
            on_change=lambda self, attr : self.update_value_from_input(attr)
        )
    
    def create_conditional_text_input(self, input):
        condition = self.create_check_box(input)
        if condition:
            text = st.text_input(
                input["file_input"]["display_name"],
                disabled=not self.params.display_parameters,
                help=input["help"],
                key=input["file_input"]["name"],
            )
            return [condition, text]
        return condition
    
    def create_number_input(self, input):
            return st.number_input(
                input["display_name"],
                value=input["value"],
                disabled=not self.params.display_parameters,
                help=input["help"],
                args=(self, input["name"]),
                on_change=lambda self, attr: self.update_value_from_input(attr),
                key=input["name"]
            )

    def create_dropdown(self, input, options):
        # Want to use dropdowns for inputs with specific options for user clarity, but Rillgen2d expects integers
        def callback(self, attribute, dropdown_options):
            option = st.session_state[attribute]
            value = dropdown_options.index(option)
            self.params.update_value(attribute, value)
        return st.selectbox(
            input["display_name"],
            options=options,
            disabled=not self.params.display_parameters,
            help=input["help"],
            args=(self, input["name"], options),
            on_change=callback,
            key=input["name"]
        )
    
    def populate_parameters_tab(self):
        """
            Populate the second tab in the application with tkinter widgets. This tab holds editable parameters
            that will be used to run the rillgen2dwitherode.c script. lattice_size_x and lattice_size_y are read in from the
            geometry of the geotiff file
        """
        st.header("Parameters")
        self.view_output = st.checkbox("View Output Directory")
        if self.view_output:
            st.text_input("Output Directory Path",
                          value=Path.cwd(), key="output_path")
            st.button(
                "View Output Directory",
                key="view_output"
            )
            return

        st.text_input(
            "Image Path",
            key="imagePathInput",
            value="https://data.cyverse.org/dav-anon/iplant/home/elliothagyard/geoSpatialTiffFiles/2mb.tif",
            help="URL or filepath",
            on_change=self.input_change_callback
        )
        # If I switch to the file upload look at this for rasterio docs on in memoroy files: https://rasterio.readthedocs.io/en/latest/topics/memory-files.html
        st.button(
            "Generate Parameters",
            on_click=self.generate_parameters_callback,
            key="genParameter"
        )
        # TODO If we switch to python 3.10 we can use match statement
        # Using the dictionary to call the correct function based on the input_field_type so we don't need 3 branches
        if self.params.display_parameters:
            st.table({"Lattice Size X:": self.params.get_value("lattice_size_x"), "Lattice Size Y:": self.params.get_value("lattice_size_y")})
        #TODO this feels awkward and requires a lot of metadata to be stored in params object, maybe figure out a better way for this
        create_st_element = {
            "number": lambda input_dict: self.create_number_input(input_dict),
            "select": lambda input_dict: self.create_dropdown(input_dict, input_dict["options"]),
            "flag": lambda input_dict: self.create_check_box(input_dict),
            "file": lambda input_dict: self.create_conditional_text_input(input_dict)
        }
        for field in self.params.mutable_input_fields():
            parameter = self.params.get_attribute_object(field)
            create_st_element[parameter["input_field_type"]](parameter)
        st.button("Run Rillgen2d", on_click=self.run_callback, args=(self.params, st.session_state.console))
        st.caption(
            'NOTE: The hydrologic correction step can take a long time if there are lots of depressions in the input DEM and/or if the' + 
            ' landscape is very steep. RILLGEN2D can be sped up by increasing the value of "fillIncrement" or by performing the hydrologic correction step in a'+
            ' different program (e.g., ArcGIS or TauDEM) prior to input into RILLGEN2D.'
        )
        # The width of rills (in m) as they begin to form. This value is used to localize water flow to a width less than the width of a pixel.
        # For example, if deltax = 1 m and rillwidth = 20 cm then the flow entering each pixel is assumed, for the purposes of rill development, to be localized in a width equal to one fifth of the pixel width.
        ########################### ^MAIN TAB^ ###########################

    def validate_file_paths(self):
        
        invalid_files = []
        for path in self.params.getEnabledFilePaths():
            if not Path(path).exists():
                invalid_files.append(path)
        if invalid_files:
            raise FileNotFoundError(f"The following filepaths are invalid: {invalid_files}")

    def delete_temp_dir(self):
        path = Path.cwd() / "tmp"
        if path.exists():
            shutil.rmtree(path.as_posix())
    
    @callback_exception_wrapper
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
    
    @callback_exception_wrapper
    def run_callback(self, params, console):
        """Run Rillgen2d"""
        invalid_paths = []
        for path in self.params.getEnabledFilePaths():
            if not Path(path).exists():
                invalid_paths.append(path)
        if invalid_paths:
            raise FileNotFoundError(f"The following filepaths are invalid: {invalid_paths}")
        if params.get_value("mask_flag") == 1:
            self.getMask(params.get_associated_filepath("mask_flag"))
        
        rg2d.generate_input_txt_file(
            st.session_state.console,
            *self.params.parametersAsArray()
        )

        if st.session_state.rillgen2d is None or not st.session_state.rillgen2d.is_alive():
            st.session_state.rillgen2d = Thread(
                target=rg2d.main, args=(imagePath, console, params))
            st.session_state.rillgen2d.start()

    def display_console(self):
        """Update the console with the latest 4 messages from Rillgen2d"""
        if "console" in st.session_state:
            while not st.session_state.console.empty():
                message = st.session_state.console.get()
                if message:
                    st.session_state.console_log.append(message)
            with st.expander("Console", True):
                for line in st.session_state.console_log[-5:-1:1]:
                    st.write(line)

    def display_preview(self):
        """Display the preview of the Geotiff as a hillshade."""
        if "hillshade_generated" not in st.session_state:
            return
        imagePath = "hillshade.png"
        imagePath = r"./" + "tmp/" * \
            int(not Path(imagePath).is_file()) + imagePath
        with st.expander("Hillshade", True):
            if st.session_state.hillshade_generated:
                st.image(
                    PIL.Image.open(imagePath),
                    caption="Simulated lighting to visualize selected area")

    def display_map(self):
        """Display the raster map """
        with st.container():
            components.html(Path("./map.html").read_text(),
                            height=500, width=700)
            st.button(
                "Save Output", key="saveButton",
                on_click=self.save_callback
            )

    def view_output(self, output_path):
        if not (Path(output_path) / "map.html").exists():
            st.warning("Output file not found at " + output_path)
        else:
            with st.container():
                components.html((Path(output_path) / "map.html").read_text())

    def app_is_running(self):
        return \
            "rillgen2d" in st.session_state \
            and st.session_state.rillgen2d\
            and st.session_state.rillgen2d.is_alive()

    def main_page(self):
        """Main page of the app."""
        st.title("Rillgen2d")
        #TODO ADD README
        app_tab, readme = st.tabs(["Rillgen2d App", "Readme"])
        with st.sidebar:
            self.populate_parameters_tab()
        with app_tab:
            if self.view_output and Path.is_file(st.session_state.view_output):
                self.view_output(st.session_state.output_path)
            else:
                self.display_console()
                self.display_preview()
                if Path("./map.html").exists() and "rillgen2d" in st.session_state and st.session_state.rillgen2d:
                    self.display_map()
        if self.app_is_running():
            st.experimental_rerun()

app = Frontend()
app.main_page()
