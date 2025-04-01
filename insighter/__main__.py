import os
import streamlit.web.cli as stcli
import sys
from pathlib import Path

if __name__ == "__main__":
    
    root_dir = Path(__file__).resolve().parent.parent
    
    app_path = os.path.join(root_dir, "app.py")
    
    sys.argv = ["streamlit", "run", app_path]
    sys.exit(stcli.main()) 