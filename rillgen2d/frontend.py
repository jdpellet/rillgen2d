from __future__ import annotations
import multiprocessing as mp
import os
import shutil
import time
from pathlib import Path

import PIL
import streamlit as st
import streamlit.components.v1 as components
import subprocess

import tarfile
MAIN_DIRECTORY = Path(__file__).parent.parent
os.chdir(MAIN_DIRECTORY)

# import rillgen2d class
from rillgen2d import Rillgen2d

from utils import (extract_geotiff_from_tarfile, get_image_from_url,
                   open_file_dialog, reset_session_state)
from parameters.Parameters import Parameters
from pathlib import Path
from utils import extract_geotiff_from_tarfile
import shutil


# todo switch to prefixing with utils to improve traceability


class Frontend:
    def __init__(self):
        if "parameters" not in st.session_state:
            st.session_state.parameters = Parameters()
        self.params = st.session_state.parameters  # Update the alias
        
        if "console" not in st.session_state:
            st.session_state.console_log = []
            st.session_state.console = mp.Queue()
        
        if "rillgen2d" not in st.session_state:
            st.session_state.rillgen2d = Rillgen2d(
                params=st.session_state.parameters,
                message_queue=st.session_state.console,
            )
        # set output path to None for previous model runs    
        self.existing_output = None
        # Alias for session state Parameters object, to make it easier to access

        self.rillgen2d = st.session_state.rillgen2d

    def generate_parameters_callback(self):
        path1 = st.session_state.imagePathInput1
        path2 = st.session_state.imagePathInput2
        if path1 and path2:
            st.warning("Both image paths are filled, please only fill one")
            return
        elif not path1 and not path2:
            st.warning("No input DEM file or URL provided, please provide one")
            return 
        path = path1 or path2

        tmp_path = MAIN_DIRECTORY / "tmp"
        # path2 already clears the tmp dir
        if path == path1:
            self.clear_tmp_dir()
            os.mkdir(tmp_path)

        if path.startswith("http"):
            path = str(get_image_from_url(path))

        if path.endswith("gz"):
            tarpath = path
            path = extract_geotiff_from_tarfile(tarpath, Path(path))
        else:
            path = Path(path)
            self.params.getParametersFromFile(MAIN_DIRECTORY / "input.txt")

            (
                filename,
                lattice_size_xVar,
                lattice_size_yVar,
                pixel_size_x,
                pixel_size_y,
            ) = self.rillgen2d.save_image_as_txt(Path(path))
            
            self.params.lattice_size_x.value = lattice_size_xVar
            self.params.lattice_size_y.value = lattice_size_yVar
            st.session_state.pixel_size_x = pixel_size_x
            st.session_state.pixel_size_y = pixel_size_y
            self.params.delta_x.value = pixel_size_x
            if filename is None:
                raise Exception("Invalid image file")
            self.rillgen2d.filename = filename
            st.session_state.hillshade = self.rillgen2d.hillshade_and_color_relief()
            st.session_state.hillshade_generated = True
            self.params.image_path = path
        self.params.display_parameters = True

    def save_callback(self):  
        save_dir = self.rillgen2d.save_output()  # Use default behavior 
        if save_dir:
            # Create tar.gz archive
            tar_filename = f"{save_dir.stem}.tar.gz"
            with tarfile.open(save_dir.parent / tar_filename, "w:gz") as tar:
                tar.add(save_dir, arcname=save_dir.name)
            
            st.success(f"Successfully saved output to {save_dir}")
            
            # Reset environment
            self.reset_environment()
            
            # Download button
            with open(save_dir.parent / tar_filename, "rb") as f:
                st.download_button(
                    label="Download Results as tar.gz",
                    data=f,
                    file_name=tar_filename,
                    mime="application/gzip",
            )
        else:
            st.warning("Failed to save output")

    def reset_environment(self):
        # Stop rillgen2d process if running
        if self.app_is_running():
            self.stop_callback()

        # Reset console and rillgen2d
        self.clear_tmp_dir()
        self.clear_session_state()
        

    def stop_callback(self):
        self.rillgen2d.terminate()
        del st.session_state.rillgen2d
        del st.session_state.parameters
        st.session_state.display_parameters = False

    def getMask(self, filepath: str):
        try:
            maskfile = Path(filepath)
            if maskfile.suffix == ".tar" or maskfile.suffix == ".gz":
                maskfile = extract_geotiff_from_tarfile(maskfile, Path.cwd())
            # Use the temporary file path as the source
            shutil.copyfile(maskfile, MAIN_DIRECTORY / "tmp/mask.tif")
            st.session_state.console.put("maskfile: is: " + str(maskfile))
        except Exception as e:
            raise Exception(f"{filepath} is an invalid mask.tif file")

    def select_file_callback(self):
        file =  st.session_state.inputTifButton
        if not file:
            return
        self.clear_tmp_dir()

        save_location = MAIN_DIRECTORY / "tmp" / file.name
        print(save_location)
        with open(save_location, "wb") as f:
            f.write(file.read())
        st.session_state.imagePathInput2 = str(save_location)


    def clear_tmp_dir(self):
        tmp_path = MAIN_DIRECTORY / "tmp"
        if tmp_path.exists()and tmp_path.is_dir():
            shutil.rmtree(tmp_path)
        os.mkdir(tmp_path)  # Recreate the directory

    def populate_parameters_tab(self):
        """
        Populate the second tab in the application with Streamlit widgets. This tab holds editable parameters
        that will be used to run the rillgen2dwitherode.c script. lattice_size_x and lattice_size_y are read in from the
        geometry of the geotiff file
        """
        # NA st.header("Parameters")
        # self.existing_output = st.checkbox("Load Previous Model Run")
        # if self.existing_output:
        #     uploaded_file = st.file_uploader("Choose an output model directory")
        #     if uploaded_file is not None:
        #         # Get the directory of the uploaded file
        #         st.session_state.output_path = os.path.dirname(uploaded_file.name)
        #         st.write(f'Selected directory: {st.session_state.output_path}')

        st.subheader("Input DEM (required)")
        st.text_input(
            "**Remote DEM from URL (`https://`)**",
            key="imagePathInput1",
            value="",
            help="Load valid raster (`.tif`, `.asc`, or `.tar.gz`) from a website URL (`https://`)",
            on_change=reset_session_state,
        )

        if "imagePathInput2" not in st.session_state:
            st.session_state.imagePathInput2 = ""
        upload = st.file_uploader(
            "**Local DEM file**",
            key="inputTifButton",
            help="Load valid DEM raster (`.tif`, `.asc`, `.tar.gz`) in the same directory as `rillgen2d.py` or use a full path (e.g., `C:/yourname/Downloads/rasters/dem.tif`, or `/Users/yourname/Downloads/rasters/dem.tif`)",
            on_change=self.select_file_callback,
        )
        if  upload:
            st.text(upload.name)
        # If I switch to the file upload look at this for rasterio docs on in memoroy files: https://rasterio.readthedocs.io/en/latest/topics/memory-files.html
        st.button(
            "Load DEM",
            on_click=self.generate_parameters_callback,
            key="genParameter",
            disabled=self.app_is_running() is True,
        )
        
        # if not self.app_is_running():
        #     st.button(
        #         "Run Rillgen2d",
        #         on_click=self.run_callback,
        #         disabled=self.params.display_parameters is False,
        #     )
        # else:
        #     st.button(
        #         "Stop Rillgen2d",
        #         key="stopRillgen",
        #         on_click=self.stop_callback,
        #     )
        # TODO this feels awkward and requires a lot of metadata to be stored in params object, maybe figure out a better way for this
        #with app_tab:
        #    if self.params.display_parameters:
        #        self.params.draw_fields(disabled=self.app_is_running())

        # The width of rills (in m) as they begin to form. This value is used to localize water flow to a width less than the width of a pixel.
        # For example, if deltax = 1 m and rillwidth = 20 cm then the flow entering each pixel is assumed, for the purposes of rill development, to be localized in a width equal to one fifth of the pixel width.


        ########################### ^MAIN TAB^ ###########################

    def clear_tmp_dir(self):
        tmp_path = MAIN_DIRECTORY / "tmp"
        if tmp_path.exists() and tmp_path.is_dir():
            shutil.rmtree(tmp_path)
            os.mkdir(tmp_path)  # Recreate the directory
    
    def clear_session_state(self):
        keep_keys = ["imagePathInput1", "imagePathInput2"]  # Add other keys to keep
        for key in list(st.session_state.keys()):
            if key not in keep_keys:
                del st.session_state[key]    
                
    def run_callback(self):
        """Run Rillgen2d"""
        errors: list[str] = self.params.validate()
        if errors:
            for error in errors:
                st.error(error)
            return
        self.params.copy_files_to_dir(MAIN_DIRECTORY / "tmp")
        if self.params.get_value("mask_flag") == 1:
            self.getMask(
            self.params.get_parameter("mask_flag").get_inner_value())
            self.rillgen2d.convert_geotiff_to_txt("mask")
        self.params.writeParametersToFile(MAIN_DIRECTORY / "tmp" / "input.txt")

        # Handle edge cases where an old rillgen object is still is in the "Run" slot
        # NOTE might be good to change Rillgen2d away from inhereting process and just create a process with a function that calls the correct stuff
        if self.rillgen2d.has_run:
            reset_console()
            reset_rillgen()
            st.session_state.rillgen2d.filename = self.rillgen2d.filename
            del self.rillgen2d
            self.rillgen2d = st.session_state.rillgen2d
            self.clear_tmp_dir()
            self.clear_session_state() 

            # Re-initialize rillgen2d
            st.session_state.rillgen2d = Rillgen2d(
                params=st.session_state.parameters,  # This line might be causing the error
                message_queue=st.session_state.console,
            )
            self.rillgen2d = st.session_state.rillgen2d  # Update the alias as well

        st.session_state.rillgen2d.start()
        self.rillgen2d.has_run = True

    def display_console(self):
        """Update the console with the latest 6 messages"""
        while not st.session_state.console.empty():
            message = st.session_state.console.get()
            if message:
                st.session_state.console_log.append(message)
        with st.expander("**Console Output**", True):
            for line in st.session_state.console_log[-7:-1:1]:
                st.write(line)

    def display_preview(self):
        """Preview of the landscape."""
        imagePath = "hillshade.png"
        imagePath = "./" + "tmp/" * \
            int(not Path(imagePath).is_file()) + imagePath
        with st.expander("**Preview DEM Hillshade** (validate)", True):
            if (
                "hillshade_generated" in st.session_state
                and st.session_state.hillshade_generated
            ):
                st.image(
                    PIL.Image.open(MAIN_DIRECTORY / "tmp/hillshade.png"),
                    caption="Hillshade generated from expected DEM raster",
                )

    def display_outputs(self):
        self.display_preview()
        map = MAIN_DIRECTORY / "tmp/map.html"
        if map.exists() and self.rillgen2d.has_run:
            st.subheader("Leaflet Map")
            self.display_map(MAIN_DIRECTORY / "tmp/map.html")
            st.subheader("Tau C (Pa)")
            self.display_tau(MAIN_DIRECTORY / "tmp/tau.png")
            st.subheader("F")
            self.display_f(MAIN_DIRECTORY / "tmp/f1.png")
            
            
                              

    # display the Leaflet Folium Map
    def display_map(self, path):
        """Display the raster map"""
        with st.container():
            components.html(
                (path).read_text(), height=500, width=700
                )

    # Add the Legend below the Leaflet Map for Tau and F

    def display_tau(self, path):
        """Display the legends"""
        if not Path(path).exists():
            return
        with st.expander("Check Tau Results", True):
            st.image(PIL.Image.open(path), caption="Tau C (Pa)")
            
    def display_f(self, path):
        """Display the legends"""
        if not Path(path).exists():
            return
        with st.expander("Check F Results", True):
            st.image(PIL.Image.open(path), caption="F Results")

    def view_output(self, output_path):
        if not (Path(output_path) / "map.html").exists():
            st.warning("Output file not found in " + output_path)
        else:
            self.display_map(Path(output_path) / "map.html")
            self.display_tau(Path(output_path) / "tau.png")
            self.display_f(Path(output_path) / "f1.png")

    def app_is_running(self):
        return (
            "rillgen2d" in st.session_state
            and st.session_state.rillgen2d
            and st.session_state.rillgen2d.is_alive()
        )

    def main_page(self):
        """Main page of the app."""
        st.title("rillgen2d")
        if not self.app_is_running():
            st.button(
                "Run Rillgen2d",
                on_click=self.run_callback,
                disabled=self.params.display_parameters is False,
            )
        else:
            st.button(
                "Stop Rillgen2d",
                key="stopRillgen",
                on_click=self.stop_callback,
            )
        input_layers,model_params,results,readme = st.tabs(["Input Layers","Model Parameters","View Results","User Manual"])

        with input_layers:#NA st.sidebar:
            self.populate_parameters_tab()
#            if self.existing_output and "output_path" in st.session_state:
#                self.view_output(st.session_state.output_path)
            self.display_preview()
            #else:
                #self.display_outputs()
            #     self.display_console()
        
# Results Tab
        with results:
            st.button(
                "Save Output", 
                key="saveButton",
                disabled=self.params.display_parameters is False,
                on_click=self.save_callback)
            # create running app screen
            if self.app_is_running():
                st.warning("Rillgen2d is currently running. Please wait for it to finish.")
            else:
                self.display_outputs()
                # ask the user if they want to open the temporary outputs directory
                if st.button("View temporary files (local only)"):
                    st.session_state.output_path = MAIN_DIRECTORY / "tmp"
                    st.write(f'Selected directory: {st.session_state.output_path}')
                    st.session_state.output_path = st.session_state.output_path.as_posix()
                    subprocess.call(['open', st.session_state.output_path]) 
                
                # ask the user if they want to open the saved output directory that starts with the word "output" and then the date and time
                if st.button("View saved output directory (local only)"):
                    st.session_state.output_path = MAIN_DIRECTORY / "."
                    st.write(f'Selected directory: {st.session_state.output_path}')
                    st.session_state.output_path = st.session_state.output_path.as_posix()
                    subprocess.call(['open', st.session_state.output_path])                                     
        
# User Manual Tab    
        with readme:
            components.iframe(
                "https://tyson-swetnam.github.io/rillgen2d/", scrolling=True, height=1000)
        
# Model Parameters Tab
        with model_params:
            if self.params.display_parameters:
                self.params.draw_fields(disabled=self.app_is_running())
        if self.app_is_running():
            time.sleep(0.5)
            st.rerun()

# Console Outputs 
        self.display_console()
        
def reset_console():
    st.session_state.console_log = []
    st.session_state.console = mp.Queue()

def reset_rillgen():
    st.session_state.rillgen2d = Rillgen2d(
        params=st.session_state.parameters,
        message_queue=st.session_state.console,
    )


if __name__ == "__main__":
    st.set_page_config(
        page_title="RillGen2D",
        page_icon=None,
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items=None,
    )
    app = Frontend()
    app.main_page()
