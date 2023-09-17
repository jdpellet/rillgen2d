import sys
import os
from streamlit.web  import cli as stcli
import importlib
modules = ['wand', 'threading', 'pathlib', 'osgeo', 'datetime', 'ctypes', 'branca', 'os', 'subprocess', 'shutil', 'sys', 'time', 'folium', 'PIL']
for module in modules:
    try:
        importlib.import_module(module)
    except ImportError:
        print(f"The '{module}' module is not installed.")


os.chdir(os.path.dirname(__file__))
sys.argv = ["streamlit", "run", "./rillgen2d/frontend.py"]
sys.exit(stcli.main())
