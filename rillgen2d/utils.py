import os
import tarfile
import requests
import streamlit as st
from pathlib import Path


def get_image_from_url(url):
    """Given the url of an image when a raster is generated or located online,
    extract the geotiff image from the url and display it on the canvas"""
    r = requests.get(url, allow_redirects=True)
    if not r.ok:
        raise Exception(
            "Invalid URL, request responded with status code: "
            + str(r.status_code)
            + " "
            + r.reason
        )
    path = Path.cwd()
    if not path.as_posix().endswith("tmp"):
        path = path / "tmp"
    downloaded = os.path.basename(url)
    img = downloaded
    if not any([downloaded.endswith(ext) for ext in [".tif", ".tiff", ".gz"]]):
        raise Exception(
            "Invalid URL, file must be a geotiff or gzipped geotiff. Downloadeded file: "
            + downloaded
        )

    open((path / downloaded), "wb").write(r.content)
    if downloaded.endswith(".gz"):
        tarpath = path / downloaded
        imagefile = extract_geotiff_from_tarfile(tarpath, path)
        os.remove(path / downloaded)
    else:
        imagefile = path / img
    return imagefile


def extract_geotiff_from_tarfile(tarpath, outputpath):
    img = tarpath
    tar = tarfile.open(tarpath)
    for filename in tar.getnames():
        if filename.endswith(".tif"):
            tar.extract(filename, path=str(outputpath))
            img = filename
            break
    desiredfile = outputpath / img
    return desiredfile


def reset_session_state():
    """
    Clear the session state, and delete the tmp directory.
    Only called when handling exceptions
    """
    for key in st.session_state:
        if key == "imagePathInput1" or key == "imagePathInput2":
            continue
        del st.session_state[key]


def exception_wrapper(callback):
    """
    Broad error handling for callbacks. This is probably a terrible way to do this
    """

    def wrapper(*args, **kwargs):
        # try:
            callback(*args, **kwargs)   
        # #TODO Add more specific exceptions. This seems like obviously practice
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
        #     reset_session_state()
    return wrapper
