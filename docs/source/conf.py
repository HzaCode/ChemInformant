import os
import sys
from datetime import datetime

# -- Path setup ---------------------------------------------------------------
sys.path.insert(0, os.path.abspath('../..'))

# -- Project information ------------------------------------------------------
project   = "ChemInformant"
author    = "Ang"
release   = "2.4.0"
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
    "sphinx_copybutton",
]

templates_path   = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
source_suffix    = ".rst"
pygments_style   = "default"

# -- Syntax highlighting configuration ----------------------------------------
# Ensure consistent syntax highlighting across all code blocks
highlight_language = "python"
highlight_options = {
    'default': {'stripall': False},
    'python': {'stripall': False},
    'bash': {'stripall': False},
    'text': {'stripall': False},
}

# -- Copy button configuration -----------------------------------------------
# Configure sphinx-copybutton to skip prompts and output
copybutton_prompt_text = r">>> |\.\.\. |\$ |In \[\d*\]: | {2,5}\.\.\.: | {5,8}: "
copybutton_prompt_is_regexp = True
copybutton_only_copy_prompt_lines = False
copybutton_remove_prompts = True

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
