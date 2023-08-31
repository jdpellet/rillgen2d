import shutil
import PIL
import os
# Change the shell to the expected directory
import streamlit.components.v1 as components


from pathlib import Path
# Threading makes sense here, since C code doesn't have global interpreter lock?
import multiprocessing as mp
import streamlit as st
import time
MAIN_DIRECTORY = Path(__file__).parent.parent
os.chdir(MAIN_DIRECTORY)

from rillgen2d import Rillgen2d
from parameters.Parameters import Parameters
from utils import get_image_from_url, extract_geotiff_from_tarfile


def reset_session_state():
    """
    Clear the session state, and delete the tmp directory.
    Only called when handling exceptions
    """
    # path = MAIN_DIRECTORY / "tmp"
    # if path.exists():
    #     shutil.rmtree(path.as_posix())
    for key in st.session_state:
        if key == "imagePathInput":
            continue
        del st.session_state[key]


def exception_wrapper(callback):
    """
    Broad error handling for callbacks. This is probably a terrible way to do this
    """
    def wrapper(*args, **kwargs):
 
        # try:
            callback(*args, **kwargs)
        #TODO Add more specific exceptions. This seems like obviously practice
        # except Exception as e:
        #     print(e)
        #     st.error(e)
        #     st.error(
        #         str(type(e).__name__)
        #     )       
        #     # TypeError
        #     st.error( str(__file__)) 

        #     if st.session_state.rillgen2d is not None and st.session_state.rillgen2d.is_alive():
        #         st.session_state.rillgen2d.join()
            # reset_session_state()
    return wrapper



class Frontend:
    def __init__(self):
        if "parameters" not in st.session_state:
            st.session_state.parameters = Parameters()
        if "console" not in st.session_state:
            st.session_state.console_log = []
            st.session_state.console = mp.Queue()
        if "rillgen2d" not in st.session_state:
            st.session_state.rillgen2d = Rillgen2d(
                params=st.session_state.parameters,
                message_queue=st.session_state.console
            )
        # Alias for session state Parameters object, to make it easier to access
        self.params = st.session_state.parameters
        self.rillgen2d = st.session_state.rillgen2d

    
    @exception_wrapper
    def generate_parameters_callback(self):
        path = MAIN_DIRECTORY / "tmp"
        if path.exists():
            shutil.rmtree(path.as_posix())
        os.mkdir(MAIN_DIRECTORY / "tmp")
        path = st.session_state.imagePathInput
        if path.startswith("http"):
            path = str(get_image_from_url(path))
            
        if path.endswith("gz"):
            tarpath = path
            path = extract_geotiff_from_tarfile(tarpath, Path(path))
        else: 
            path = Path(path)
        
        self.params.getParametersFromFile(Path.cwd() / "input.txt")

        filename, lattice_size_xVar, lattice_size_yVar = self.rillgen2d.save_image_as_txt(path)
        self.params.lattice_size_x.value = lattice_size_xVar
        self.params.lattice_size_y.value = lattice_size_yVar
        if filename is None:
            raise Exception("Invalid image file")
        self.rillgen2d.filename = filename
        st.session_state.hillshade =  self.rillgen2d.hillshade_and_color_relief()
        st.session_state.hillshade_generated = True
        self.params.image_path = path
        self.params.display_parameters = True

    def save_callback(self):
        self.rillgen2d.save_output()

    def getMask(self, filepath):
        # TODO Figure out input for filepath
        if self.params.get_value("mask_flag"):
            try:
                maskfile = Path(filepath)
                if maskfile.suffix == '.tar' or maskfile.suffix == '.gz':
                    maskfile = extract_geotiff_from_tarfile(
                        maskfile, Path.cwd()
                    )

                shutil.copyfile(maskfile, Path.cwd() / "mask.tif")
                st.session_state.console.put("maskfile: is: " + str(maskfile))
            except Exception:
                raise Exception("Invalid mask.tif file")


    def populate_parameters_tab(self):
        """
            Populate the second tab in the application with tkinter widgets. This tab holds editable parameters
            that will be used to run the rillgen2dwitherode.c script. lattice_size_x and lattice_size_y are read in from the
            geometry of the geotiff file
        """
        st.header("Parameters")
        self.existing_output = st.checkbox("View Output Directory")
        if self.existing_output:
            st.text_input("Output Directory Path",
                          value=Path.cwd(), key="output_path")
            st.button(
                "View Output Directory",
                key="view_output_button"
            )
            return
        st.text_input(
            "Image Path",
            key="imagePathInput",
            value="https://data.cyverse.org/dav-anon/iplant/home/elliothagyard/geoSpatialTiffFiles/2mb.tif",
            help="URL or filepath",
            on_change=reset_session_state
        )
        # If I switch to the file upload look at this for rasterio docs on in memoroy files: https://rasterio.readthedocs.io/en/latest/topics/memory-files.html
        st.button(
            "Generate Parameters",
            on_click=self.generate_parameters_callback,
            key="genParameter"
        )
        #TODO this feels awkward and requires a lot of metadata to be stored in params object, maybe figure out a better way for this
        if self.params.display_parameters:

            self.params.draw_fields()
        
        st.button("Run Rillgen2d", on_click=self.run_callback, args=(self.params,))
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
    
    @exception_wrapper
    def run_callback(self, params):
        """Run Rillgen2d"""
        invalid_paths = []
        for path in self.params.getEnabledFilePaths():
            if not Path(path).exists():
                invalid_paths.append(path)
        if invalid_paths:
            raise FileNotFoundError(f"The following filepaths are invalid: {invalid_paths}")
        if params.get_value("mask_flag") == 1:
            self.getMask(params.get_associated_filepath("mask_flag"))
        params.writeParametersToFile(MAIN_DIRECTORY / "tmp" / "input.txt")
        # if self.rillgen2d.ident: 
        #     st.session_state.rillgen2d = Rillgen2d(self.param, st.session_state.console)
        self.rillgen2d.start()


    @exception_wrapper
    def display_console(self):
        """Update the console with the latest 4 messages from Rillgen2d"""
        while not st.session_state.console.empty():
            message = st.session_state.console.get()
            if type(message) is Exception:
                raise message
            elif message:
                st.session_state.console_log.append(message)
        with st.expander("Console", True):
            for line in st.session_state.console_log[-5:-1:1]:
                st.write(line)
                
    @exception_wrapper
    def display_preview(self):
        """Display the preview of the Geotiff as a hillshade."""
        if "hillshade" not in st.session_state:
            return
        imagePath = st.session_state.hillshade
        with st.expander("Hillshade", True):
            if st.session_state.hillshade_generated:
                st.image(
                    PIL.Image.open(imagePath),
                    caption="Simulated lighting to visualize selected area")

    def display_map(self):
        """Display the raster map """
        with st.container():
            components.html(Path(MAIN_DIRECTORY / "tmp/map.html").read_text(),
                            height=600)
            st.button(
                "Save Output", key="saveButton",
                on_click=self.save_callback
            )

    def view_output(self, output_path):
        if not (Path(output_path) / "map.html").exists():
            st.warning("Output file not found at " + output_path)
        else:
            with st.container():
                components.html((Path(output_path) / "map.html").read_text(), height=600)

    def app_is_running(self):
        return self.rillgen2d and self.rillgen2d.is_alive()

    def main_page(self):
        """Main page of the app."""
        st.title("Rillgen2d")
        #TODO ADD README
        app_tab, readme = st.tabs(["Rillgen2d App", "Readme"])
        with st.sidebar:
            self.populate_parameters_tab()
        with app_tab:
            if self.existing_output:
                self.view_output(st.session_state.output_path)
            else:
                self.display_console()
                self.display_preview()
                if Path(MAIN_DIRECTORY / "tmp/map.html").exists() and "rillgen2d" in st.session_state and st.session_state.rillgen2d:
                    self.display_map()
        if self.app_is_running():
            time.sleep(.5)
            st.experimental_rerun()


if __name__ == "__main__":
    st.set_page_config(page_title="Rillgen2d", page_icon=None, layout="wide", initial_sidebar_state="auto", menu_items=None)
    app = Frontend()
    app.main_page()
