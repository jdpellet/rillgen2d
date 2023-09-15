import sys
import os
from streamlit.web  import cli as stcli


sys.argv = ["streamlit", "run", "./rillgen2d/frontend.py"]
sys.exit(stcli.main())
