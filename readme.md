# Jupyter utils 

jupyter_utils is a Python package designed to enhance the functionality of Jupyter Notebooks, particularly for managing and visualizing academic schedules, converting images to HTMLbase64, and exporting student version of lab notebooks.

## Installation

You can install jupyter_utils using pip:

```bash
pip install jupyter_utils
```

Or you can clone the repository and install it locally:

```bash
git clone https://github.com/llestandi/jupyter_utils.git
cd jupyter_utils
pip install .
```
## Usage
### Agenda ECN
The agenda_ecn.py module is designed to parse and extract course schedules from Excel files used at ECN (École Centrale de Nantes).

A complete notebook example is provided at [`agenda.ipynb`](agenda.ipynb)

### Converting media to HTML base64 for explicit embedding
The img2html.py module converts images and videos to HTML format for easy embedding in Jupyter Notebooks. It is wrapped into a CLI for ease of use.

#### media2html_base64
This function reads the media file name from command-line arguments,
converts the media to a base64-encoded HTML media tag using the media2html_base64 function,
and prints the resulting tag to the console.

```bash
media2html_base64 path/to/media.file
```

### Student notebook export
Similarly, a CLI has been implemented to export a curated version Labs Jupyter Notebook for students. In other words, the cells tagged with `"solution"` are removed from the processed nb.
Example usage:

```bash
    $ python student_notebook_export.py notebook_with_solutions.ipynb --keep_output --export_HTML
    # or if you have installed the package with pip:
    $ student_notebook_export notebook_with_solutions.ipynb --keep_output --export_HTML
```
# License
This project is licensed under the MIT License. See the LICENSE file for details.