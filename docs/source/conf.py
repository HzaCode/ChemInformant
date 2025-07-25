import os
import sys
from datetime import datetime

# -- Path setup ---------------------------------------------------------------
sys.path.insert(0, os.path.abspath('../../src'))

# -- Project information ------------------------------------------------------
project   = "ChemInformant"
author    = "Ang"
release   = "2.3.0"
copyright = f"{datetime.now().year}, {author}"

# -- General configuration ----------------------------------------------------
root_doc   = "index"
language   = "en"
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "sphinx.ext.todo",
]

templates_path   = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
source_suffix    = ".rst"
pygments_style   = "sphinx"

# -- HTML output --------------------------------------------------------------
html_theme       = "sphinx_rtd_theme"
html_static_path = ["_static"]


html_theme_options = {
    "collapse_navigation": True,   
    "navigation_depth"  : 2,       
    "style_external_links": True,  
}


# -- Intersphinx --------------------------------------------------------------
intersphinx_mapping = {
    "python"  : ("https://docs.python.org/3", None),
    "pandas"  : ("https://pandas.pydata.org/pandas-docs/stable/", None),
    "requests": ("https://docs.python-requests.org/en/latest/", None),
}
