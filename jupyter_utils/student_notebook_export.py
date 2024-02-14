import nbformat
import argparse
import os
from nbconvert import HTMLExporter

def export_CLI():
    """
    Command line parser for the notebook_student_export function.

    Example usage:
    $ python student_notebook_export.py notebook_with_solutions.ipynb --keep_output --export_HTML
    or if you have installed the package with pip:
    $ student_notebook_export notebook_with_solutions.ipynb --keep_output --export_HTML
    """
    parser = argparse.ArgumentParser(description="Create a student version of a Jupyter Notebook without solution cells.")
    parser.add_argument("input", help="Path to the notebook with solutions")
    parser.add_argument("--keep_output", help="Keep the output for solution code cells", action="store_true")
    parser.add_argument("--export_HTML", help="Export the notebook to HTML to the same directory with the same name as the output notebook", action="store_true")
    args = parser.parse_args()

    output_path = "student_"+args.input

    notebook_student_export(args.input, output_path, args.export_HTML, args.keep_output)
    

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

def notebook_student_export(notebook_path, output_path, export_HTML=True, keep_output=False):
    """
    Create a student version of a Jupyter Notebook without solution cells. You can also choose to keep the output of the solution cells. and export the notebook to HTML.
    
    Args:
    notebook_path (str): Path to the notebook with solutions
    output_path (str): Path to the output notebook
    export_HTML (bool): Export the notebook to HTML to the same directory with the same name as the output notebook
    keep_output (bool): Keep the output for solution code cells
    """
    # this code was generated with the help of LLMs on 14/02/2024
    with open(notebook_path, 'r') as f:
        notebook = nbformat.read(f, as_version=4)

    cleaned_cells = []
    for cell in notebook.cells:
        if cell.cell_type == 'code':
            if "solution" not in cell.get("metadata", {}).get("tags", []):
                cleaned_cells.append(cell)
            elif keep_output:
                # Keep the output for solution code cells
                cell.source = ""
                cleaned_cells.append(cell)
        else:
            # Keep non-code cells
            cleaned_cells.append(cell)

    notebook.cells = cleaned_cells

    with open(output_path, 'w') as f:
        nbformat.write(notebook, f)

    if export_HTML:
        # Convert notebook to HTML
        html_exporter = HTMLExporter()
        (html_body, _) = html_exporter.from_notebook_node(notebook)
        html_output_path = os.path.splitext(output_path)[0] + ".html"
        # Save HTML output
        with open(html_output_path, 'w') as f:
            f.write(html_body)    
