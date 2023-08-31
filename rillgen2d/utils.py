import os
import tarfile
import requests

from pathlib import Path

def get_image_from_url(url):
    """Given the url of an image when a raster is generated or located online,
    extract the geotiff image from the url and display it on the canvas """
    r = requests.get(url, allow_redirects=True)
    if not r.ok:
        raise Exception(
            "Invalid URL, request responded with status code: " +
            str(r.status_code) + " " + r.reason
        )
    path = Path.cwd()
    if not path.as_posix().endswith('tmp'):
        path = path / "tmp"
    downloaded = os.path.basename(url)
    img = downloaded
    if not any([downloaded.endswith(ext) for ext in [".tif", ".tiff", ".gz"]]):
        raise Exception("Invalid URL, file must be a geotiff or gzipped geotiff. Downloadeded file: " + downloaded)
    
    open((path / downloaded), 'wb').write(r.content)
    if downloaded.endswith(".gz"):
        tarpath = path / downloaded
        imagefile = extract_geotiff_from_tarfile(tarpath, path)
        os.remove(path / downloaded)
    else:
        imagefile = (path / img)
    return imagefile

def extract_geotiff_from_tarfile(tarpath, outputpath):
    img = tarpath
    tar = tarfile.open(tarpath)
    for filename in tar.getnames():
        if filename.endswith('.tif'):
            tar.extract(filename, path=str(outputpath))
            img = filename
            break
    desiredfile = (outputpath / img)
    return desiredfile