from __future__ import annotations
from rillgen2d import Rillgen2d
import shutil
import PIL
import os
import time

import streamlit.components.v1 as components
from pathlib import Path
import multiprocessing as mp
import streamlit as st

# Change directory to the root of the project before doing relative imports
MAIN_DIRECTORY = Path(__file__).parent.parent
os.chdir(MAIN_DIRECTORY)
from parameters.Parameters import Parameters
from utils import (
    get_image_from_url, extract_geotiff_from_tarfile, reset_session_state, open_file_dialog)

# TODO switch to prefixing with utils. to improve traceability


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
                message_queue=st.session_state.console,
            )
        # Alias for session state Parameters object, to make it easier to access
        self.params = st.session_state.parameters
        self.rillgen2d = st.session_state.rillgen2d

    def generate_parameters_callback(self):
        path1 = st.session_state.imagePathInput1
        path2 = st.session_state.imagePathInput2
        if path1 and path2:
            st.warning("Both image paths are filled, please only fill one")
            return
        elif not path1 and not path2:
            st.warning("Please fill in an image path")
            return
        path = path1 or path2

        tmp_path = MAIN_DIRECTORY / "tmp"
        if tmp_path.exists():
            shutil.rmtree(tmp_path.as_posix())
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
        ) = self.rillgen2d.save_image_as_txt(path)
        self.params.lattice_size_x.value = lattice_size_xVar
        self.params.lattice_size_y.value = lattice_size_yVar
        if filename is None:
            raise Exception("Invalid image file")
        self.rillgen2d.filename = filename
        st.session_state.hillshade = self.rillgen2d.hillshade_and_color_relief()
        st.session_state.hillshade_generated = True
        self.params.image_path = path
        self.params.display_parameters = True

    def save_callback(self):
        outDir = self.rillgen2d.save_output()
        if outDir:
            st.success("Successfully saved output to " + str(outDir))
        else:
            st.warning("Failed to save output")

    def stop_callback(self):
        # TODO check if queue can become corrupted
        self.rillgen2d.terminate()
        del st.session_state.rillgen2d
        del st.session_state.parameters
        st.session_state.display_parameters = False

    def getMask(self, filepath: str):
        try:
            maskfile = Path(filepath)
            if maskfile.suffix == ".tar" or maskfile.suffix == ".gz":
                maskfile = extract_geotiff_from_tarfile(maskfile, Path.cwd())
            shutil.copyfile(maskfile, MAIN_DIRECTORY / "tmp/mask.txt")
            st.session_state.console.put("maskfile: is: " + str(maskfile))
        except Exception as e:
            print(e)
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
            if st.button('Select Output Directory'):
                st.session_state.output_path = open_file_dialog()
            return

        st.header("Input DEM")
        st.text_input(
            "Load DEM (`.tif`) from Web URL (`https://`)",
            key="imagePathInput1",
            value="",
            help="Load valid raster (`.tif`) from a URL (`https://`), the file will be downloaded",
            on_change=reset_session_state,
        )

        st.text_input(
            "Locally saved DEM file (`.tif`)",
            key="imagePathInput2",
            value="",
            help="Load valid DEM raster (`.tif`) in the same directory as `rillgen2d.py` or use a full path (e.g., `C:/yourname/Downloads/rasters/dem.tif`, or `/Users/yourname/Downloads/rasters/dem.tif`)",
            on_change=reset_session_state,
        )

        # If I switch to the file upload look at this for rasterio docs on in memoroy files: https://rasterio.readthedocs.io/en/latest/topics/memory-files.html
        st.button(
            "Generate Parameters",
            on_click=self.generate_parameters_callback,
            key="genParameter",
            disabled=self.app_is_running() is True,
        )
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
        st.caption(
            "NOTE: The hydrologic correction step can take a long time if there are lots of depressions in the input DEM and/or if the"
            + ' landscape is very steep. RILLGEN2D can be sped up by increasing the value of "fillIncrement" or by performing the hydrologic correction step in a'
            + " different program (e.g., ArcGIS or TauDEM) prior to input into RILLGEN2D."
        )
        # TODO this feels awkward and requires a lot of metadata to be stored in params object, maybe figure out a better way for this
        if self.params.display_parameters:
            self.params.draw_fields(disabled=self.app_is_running())

        # The width of rills (in m) as they begin to form. This value is used to localize water flow to a width less than the width of a pixel.
        # For example, if deltax = 1 m and rillwidth = 20 cm then the flow entering each pixel is assumed, for the purposes of rill development, to be localized in a width equal to one fifth of the pixel width.
        ########################### ^MAIN TAB^ ###########################

    def run_callback(self):
        """Run Rillgen2d"""
        errors: list[str] = self.params.validate()
        if errors:
            for error in errors:
                st.error(error)
            return
        self.params.copy_files_to_dir(MAIN_DIRECTORY / "tmp")
        if self.params.get_value("mask_flag") == 1:
            self.getMask(self.params.get_parameter("mask_flag").get_inner_value())
        self.params.writeParametersToFile(MAIN_DIRECTORY / "tmp" / "input.txt")

        # Handle edge cases where an old rillgen object still is in the run slot
        # NOTE might be good to change Rillgen2d away from inhereting process and just create a process with a function that calls the correct stuff
        if self.rillgen2d.has_run:
            reset_console()
            reset_rillgen()
            st.session_state.rillgen2d.filename = self.rillgen2d.filename
            del self.rillgen2d
            self.rillgen2d = st.session_state.rillgen2d
        
        st.session_state.rillgen2d.start()
        self.rillgen2d.has_run = True

    def display_console(self):
        """Update the console with the latest 6 messages"""
        while not st.session_state.console.empty():
            message = st.session_state.console.get()
            if message:
                st.session_state.console_log.append(message)
        with st.expander("Terminal", True):
            for line in st.session_state.console_log[-7:-1:1]:
                st.write(line)

    def display_preview(self):
        """Preview of the landscape."""
        imagePath = "hillshade.png"
        imagePath = "./" + "tmp/" * int(not Path(imagePath).is_file()) + imagePath
        with st.expander("Check DEM landscape", True):
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
            self.display_map(MAIN_DIRECTORY / "tmp/map.html")
            self.display_tau(MAIN_DIRECTORY / "tmp/tau.png")
            st.button("Save Output", key="saveButton", on_click=self.save_callback)

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

    def view_output(self, output_path):
        if not (Path(output_path) / "map.html").exists():
            st.warning("Output file not found at " + output_path)
        else:
            self.display_map(Path(output_path) / "map.html")
            self.display_tau(Path(output_path) / "tau.png")

    def app_is_running(self):
        return (
            "rillgen2d" in st.session_state
            and st.session_state.rillgen2d
            and st.session_state.rillgen2d.is_alive()
        )

    def main_page(self):
        """Main page of the app."""
        st.title("rillgen2d")
        app_tab, readme = st.tabs(["Parameters", "User Manual"])
        with st.sidebar:
            self.populate_parameters_tab()
        with app_tab:
            if self.existing_output and "output_path" in st.session_state:
                self.view_output(st.session_state.output_path)
            else:
                self.display_console()
                self.display_outputs()
        with readme:
            components.iframe("https://tyson-swetnam.github.io/rillgen2d/", scrolling=True, height=1000)
        if self.app_is_running():
            time.sleep(0.5)
            st.rerun()


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
        page_title="Rillgen2d",
        page_icon=None,
        layout="wide",
        initial_sidebar_state="auto",
        menu_items=None,
    )
    app = Frontend()
    app.main_page()
