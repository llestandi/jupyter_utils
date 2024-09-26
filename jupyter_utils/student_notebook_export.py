"""
Notebook Student Export Module

This module provides functionality to create a student-friendly version of a Jupyter notebook 
by removing solution cells and optionally keeping their output. The processed notebook can be 
exported to different formats like HTML, PDF (via HTML or LaTeX), and YAML configuration files.

Main Features
-------------
- Remove solution cells from a Jupyter notebook, keeping or discarding their output.
- Export the cleaned notebook to HTML format, PDF (via HTML or LaTeX), or YAML for styling metadata.
- Command-line interface (CLI) for easy use, allowing users to pass various export options.

Functions
---------
- export_CLI(): 
    Command-line interface parser to handle the notebook export process.
    
- remove_solution_cells(notebook_path, output_path):
    Removes cells tagged with "solution" from the notebook, creating a cleaned version for students.

- notebook_student_export(notebook_path, output_path, keep_output=False, export_HTML=False, export_YAML=False, export_PDF=False, export_PDF_latex=False):
    Main function that processes the notebook to create a student version and exports it to various formats.

- YAML_update(cell, to_pdf=False):
    Updates YAML metadata in the first cell of the notebook, which can be used for styling or LaTeX formatting.

CLI Usage
---------
The module can be run from the command line with arguments to customize the export options. 
For example:
    $ python student_notebook_export.py notebook_with_solutions.ipynb --keep_output --export_HTML
or after installing the package:
    $ student_notebook_export notebook_with_solutions.ipynb --keep_output --export_HTML

Dependencies
------------
- nbconvert
- nbformat
- argparse
- subprocess
- yaml
"""

import os
import subprocess
import argparse

from datetime import datetime
from nbconvert import HTMLExporter, PDFExporter
import yaml

import nbformat



def export_CLI():
    """
    Command line parser for the notebook_student_export function.

    Example usage:
    $ python student_notebook_export.py notebook_with_solutions.ipynb --keep_output --export_HTML
    or if you have installed the package with pip:
    $ student_notebook_export notebook_with_solutions.ipynb --keep_output --export_HTML
    """
    parser = argparse.ArgumentParser(description="Create a student version of a Jupyter Notebook without solution cells.")
    parser.add_argument("input",
                        help="Path to the notebook with solutions")
    parser.add_argument("--keep_output",
                        help="Keep the output for solution code cells", action="store_true")
    parser.add_argument("--export_HTML",
                        help="Export the notebook to HTML to the same directory with the same name as the output notebook",
                        action=argparse.BooleanOptionalAction)
    parser.add_argument("--export_YAML",
                        help="updates_yaml for styling PDF and/or HTML", 
                        action="store_true")
    parser.add_argument("--export_PDF", 
                        help="Export the notebook to PDF via HTML using wkhtmltopdf in the same directory with the same name as the output notebook", 
                        action="store_true")
    
    parser.add_argument("--export_PDF_latex", 
                        help="Export the notebook directly to PDF using LaTeX. Base64 images will not come through", 
                        action="store_true")

    args = parser.parse_args()
    output_path = "student_"+args.input

    notebook_student_export(args.input, output_path,
                            keep_output=args.keep_output,
                            export_HTML=args.export_HTML, 
                            export_YAML=args.export_YAML, 
                            export_PDF=args.export_PDF,
                            export_PDF_latex=args.export_PDF_latex)

# first version
def remove_solution_cells(notebook_path, output_path):
    with open(notebook_path, 'r') as f:
        notebook = nbformat.read(f, as_version=4)

    cleaned_cells = []
    for cell in notebook.cells:
        if "solution" not in cell.get("metadata", {}).get("tags", []):
            cleaned_cells.append(cell)

    notebook.cells = cleaned_cells

    with open(output_path, 'w') as f:
        nbformat.write(notebook, f)

def notebook_student_export(notebook_path, output_path, 
                            keep_output=False,
                            export_HTML=False,
                            export_YAML=False, 
                            export_PDF=False,
                            export_PDF_latex=False):
    """
    Create a student version of a Jupyter Notebook without solution cells. You can also choose to keep the output of the solution cells. and export the notebook to HTML.
    
    notebook_path (str): Path to the original notebook with solutions.
        output_path (str): Path to the output notebook (without solutions).
        keep_output (bool): If True, retains the output of solution code cells in the student version.
        export_HTML (bool): If True, exports the notebook to HTML format in the same directory as the output notebook.
        export_YAML (bool): If True, exports the notebook's metadata or configuration to a YAML file.
        export_PDF (bool): If True, converts the notebook to a PDF using wkhtmltopdf after exporting to HTML.
        export_PDF_latex (bool): If True, converts the notebook directly to a PDF using LaTeX.

    Returns:
        None
    """
    # this code was generated with the help of LLMs on 14/02/2024
    with open(notebook_path, 'r') as f:
        notebook = nbformat.read(f, as_version=4)

    cleaned_cells = []
    for i, cell in enumerate(notebook.cells):
        if export_YAML and i==0:
            YAML_update(cell)

        if "solution" in cell.get("metadata", {}).get("tags", []): 
            if keep_output: # remove cell source but display output
                cell.source = "" 
            else:
                continue # skip saving i.e. discard all the cell
                 
        cleaned_cells.append(cell)

    notebook.cells = cleaned_cells

    with open(output_path, 'w') as f:
        nbformat.write(notebook, f)
    html_body = None

    if export_HTML or export_PDF:
        # Convert notebook to HTML (if needed for HTML or PDF export)
        html_exporter = HTMLExporter()
        html_body, _ = html_exporter.from_notebook_node(notebook)
        html_output_path = os.path.splitext(output_path)[0] + ".html"

        # Save HTML output
        with open(html_output_path, 'w') as f:
            f.write(html_body)

    pdf_output_path = os.path.splitext(output_path)[0] + ".pdf"
    if export_PDF:      
        # Convert HTML to PDF using wkhtmltopdf
        
        subprocess.run(['wkhtmltopdf', html_output_path, pdf_output_path])
        if not export_HTML:  # cleaning up temp HTML if not wanted
            os.remove(html_output_path)

    if export_PDF_latex :
        # Convert notebook to PDF
        pdf_exporter = PDFExporter()
        # making sure yaml formatting is stripped off
        YAML_update(notebook.cells[0],True) 
        pdf_data, _ = pdf_exporter.from_notebook_node(notebook)
        # Write the PDF data to a file
        print("Using latex : base 64 images will not come through", pdf_output_path)
        with open(pdf_output_path, 'wb') as f:
            f.write(pdf_data)


def YAML_update(cell,to_pdf=False):
    if cell.cell_type=="raw": 
        #reading existing data only if raw format
        metadata=yaml.safe_load(cell.source)
    else:
        metadata={"author": "Lucas Lestandi",
                "email": "lucas.lestandi@ec-nantes.fr",
                "date": "",
                "version": "V1.0",
                    }

    current_year = datetime.now().year
    next_year = current_year + 1
    academic_year = f"{current_year}-{next_year}"

    metadata["date"]=academic_year
    if to_pdf:
        cell.source=f"---\n{yaml.dump(metadata, sort_keys=False)}---"
    else:
        cell.source=f"```yaml\n---\n{yaml.dump(metadata, sort_keys=False)}---\n```"