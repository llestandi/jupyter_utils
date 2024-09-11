"""
Module for translating Markdown content.

This module supports two translation methods:

1. **LibreTranslate** (API-based):
   - Ideal for lightweight and simple translation tasks.
   - Easy to set up with a local or remote API.
   - Requires manual handling of Markdown, LaTeX, and code formatting.
   - **Warning**: The local LibreTranslate server must be running to use this method.
     Ensure the server is running at `http://localhost:5000` if self-hosted.
   - Best suited for general-purpose translations where speed and simplicity are key.

2. **Hugging Face Transformers** (model-based):
   - **Not implemented completely, escape characters are not handled properly**
   - Offers higher translation quality and customizable models.
   - Allows for fine-tuning and domain-specific translations.
   - Can handle complex formatting like Markdown and LaTeX with custom preprocessing.
   - Resource-intensive and slower, but highly adaptable to advanced use cases.
   - **requires pytorch and transformers**

Use LibreTranslate for now
"""
import sys
from pathlib import Path
import json
import re
import argparse
import requests

import nbformat

def translate_CLI():
    """
    Command line parser for the translate_notebook function function.

    Example usage:
    $ python auto_translate.py path/to/your_notebook.ipynb --input_language fr --output_language en
    or if you have installed the package with pip:
    $ translate_notebook path/to/your_notebook.ipynb --input_language fr --output_language en
    """
    parser = argparse.ArgumentParser(
        description="Translate Markdown content in a Jupyter notebook while preserving formatting."
    )
    
    parser.add_argument(
        'notebook_path',
        type=str,
        help='Path to the Jupyter notebook file (.ipynb).'
    )
    
    parser.add_argument(
        '--input_language',
        type=str,
        default='fr',
        help='The source language for translation. Default is "fr".'
    )
    
    parser.add_argument(
        '--output_language',
        type=str,
        default='en',
        help='The target language for translation. Default is "en".'
    )
    
    args = parser.parse_args()
    
    notebook_path = args.notebook_path
    input_language = args.input_language
    output_language = args.output_language
    
    # Validate the notebook path
    notebook_path = Path(notebook_path)
    if not notebook_path.is_file():
        print(f"Error: The file '{notebook_path}' does not exist.")
        sys.exit(1)
    
    # Call the translate_notebook function
    try:
        translate_notebook(notebook_path, input_language, output_language)
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)


def translate_notebook(notebook_path,
                       input_language="fr",
                       output_language="en") -> None: 
    """
    Translates Markdown content in a Jupyter notebook while preserving code cells.
    
    Adds a warning message to the first cell and translates Markdown cells using LibreTranslate.
    
    Parameters
    ----------
    notebook_path : str
        Path to the Jupyter notebook file (.ipynb).
    
    output_language : str, optional
        The target language for translation. Default is 'en' (English).
    
    Returns
    -------
    None
    """

    translator=lambda text : libretranslate(text, input_language=input_language,  output_language=output_language)
    # Load the notebook
    with open(notebook_path, 'r', encoding='utf-8') as f:
        nb = nbformat.read(f, as_version=4)

    #Add warning in first cell
    warning=f'<div class="alert alert-danger"> <p> <b>This notebook has been translated automatically from{input_language}</b> You can access the original text of each cell in metadata.</p>'
    warning_cell = nbformat.v4.new_markdown_cell(warning)
    nb.cells.insert(0, warning_cell)
    
    # Translate Markdown cells
    for cell in nb.cells:
        if cell.cell_type == 'markdown':
            if 'original_content' not in cell.metadata:
                cell.metadata['original_content'] = cell.source # Store the original content in metadata
            original_text = cell.source
            translated_text = translate_md(original_text,translator)
            cell.source = translated_text
    
    # Save the translated notebook
    output_path = notebook_path.with_name(notebook_path.stem + f"_auto_{output_language}.ipynb")
    with open(output_path, 'w', encoding='utf-8') as f:
        nbformat.write(nb, f)
    
    print(f"Translated notebook saved to {output_path}")

def translate_md(source, translator):
    """Translates Markdown content while preserving formatting.

    This function translates a Markdown document, ensuring that special formatting 
    such as code blocks, LaTeX equations, and other non-translatable elements 
    are preserved using placeholders during the translation process.

    Parameters
    ----------
    source : str
        The source Markdown text to be translated.
    
    translator : function
        A function that takes the preprocessed text and performs the translation.
        The translator function should follow the signature: 
        `translator(text, input_language, output_language)`.
    
    Returns
    -------
    str
        The translated Markdown content with formatting and special elements 
        (e.g., LaTeX, code blocks) preserved.
    
    Workflow
    --------
    1. **Preprocessing**:
        The `preprocess_text` function identifies and replaces non-translatable elements, 
        such as LaTeX, code blocks, and other Markdown-specific formatting, with 
        placeholders to ensure they are not altered during the translation process.
    
    2. **Translation**:
        The preprocessed text is passed to the `translator` function, which handles 
        the translation of the remaining translatable segments between the input 
        and output languages.
    
    3. **Postprocessing**:
        After translation, `postprocess_text` restores the original non-translatable 
        elements by replacing the placeholders, ensuring the final output maintains 
        the correct Markdown structure and formatting.
    
    Notes
    -----
    - Ensure that the `translator` function provided correctly implements the 
      translation process for the input and output languages.
    - The placeholders are used to preserve Markdown-specific elements that should 
      not be translated (e.g., LaTeX equations, code blocks).
    
    Examples
    --------
    Translate a Markdown document from French to English using a custom translator:

    >>> translated_md = translate_md(source_md, my_translator)
    """

    placeholders = {}
    text = preprocess_text(source, placeholders)
    text= translator(text)
    return postprocess_text(text, placeholders)

def preprocess_text(text, placeholders):
    """function to extract and replace text that we do not want translated (specifically anything between ``` and ``` code blocks)
    """
    # placeholder pattern (you can customize this)
    pattern = r'```(.*?)```'
    matches = re.findall(pattern, text, re.DOTALL)
    for i, match in enumerate(matches):
        placeholder = f'__PLACEHOLDER_{i}__'
        placeholders[placeholder] = match
        text = text.replace(f'```{match}```', placeholder)
    return text

# function to reinsert the original segments back into the text
def postprocess_text(translated_text, placeholders):
    for placeholder, original_text in placeholders.items():
        translated_text = translated_text.replace(placeholder, f'```{original_text}```')
        #translated_text = translated_text.replace(placeholder, '[NO_TRANSLATE]' + original_text + '[/NO_TRANSLATE]')
    return translated_text

# function to translate text using LibreTranslate API
def libretranslate(text, 
                   url = 'http://localhost:5000/translate',
                   input_language="fr", 
                   output_language="en"):
    """Translates text using the LibreTranslate API.

    Sends the provided text to a LibreTranslate instance (default is local server),
    translating it from the specified input language to the target language.
    
    Parameters
    ----------
    text : str
        The text to be translated.
    
    url : str, optional
        The endpoint URL for the LibreTranslate API. Default is 'http://localhost:5000/translate'.
    
    input_language : str, optional
        The language code of the input text. Default is 'fr' (French).
    
    output_language : str, optional
        The language code for the translated output text. Default is 'en' (English).
    
    Returns
    -------
    str
        The translated text returned by the LibreTranslate API.
    
    Raises
    ------
    Exception
        If the LibreTranslate server is not running, or an error occurs during the API request.
    
    Notes
    -----
    - Ensure the LibreTranslate server is running at the specified URL (default: localhost).
    - The translation format is set to "html" to handle any embedded formatting in the text (e.g., Markdown or LaTeX).

    Examples
    --------
    Translate a French sentence to English:
    
    >>> libretranslate("Bonjour le monde")
    'Hello, world'
    """
    
    # Test if the LibreTranslate server is running
    try:
        response = requests.get(url.replace("/translate", "/languages"))
        if response.status_code != 200:
            raise Exception("LibreTranslate server is not responding.")
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to connect to LibreTranslate server: {e}"
                        "Ensure that the LibreTranslate Docker server is running. "
                        "Start the server with: `docker run -d -p 5000:5000 libretranslate/libretranslate` and try again.")

    # build Json payload to send to LibreTranslate API
    payload = {
        "q": text,
        "source": input_language,
        "target": output_language,
        "format": "html",
        "api_key": ""
    }
    headers = {"Content-Type": "application/json"}

    # send payload to LibreTranslate API
    response = requests.post(url, data=json.dumps(payload), headers=headers)

    return response.json()['translatedText']

# def load_Marian_translator():
#     """Loading MarianMT model as a translator (microsoft owned)"""
#     from transformers import MarianMTModel, MarianTokenizer
#     model_name = 'Helsinki-NLP/opus-mt-fr-en'
#     model = MarianMTModel.from_pretrained(model_name)
#     tokenizer = MarianTokenizer.from_pretrained(model_name)
#     def translate(text, model=model, tokenizer=tokenizer):
#         # Tokenize the input text
#         inputs = tokenizer(text, return_tensors="pt", padding=True)

#         # Generate the translated output using the model
#         translated = model.generate(**inputs)

#         # Decode the translated text back to a readable format
#         return tokenizer.decode(translated[0], skip_special_tokens=True)
#     return translate

if __name__=='__main__':
    source_md = """
    # Bonjour le monde

    Ceci est un exemple de document Markdown contenant du texte, des `code blocks`,
    ainsi que des formules LaTeX : $E = mc^2$.

    > *Les variables simples vue jusqu'ici sont dites **non-mutable** (immuable en bon français) i.e.*
    > 1. on ne modifie jamais le contenu d'une case mémoire
    > 1. on affecte la variable à une nouvelle case
    """
    # Use LibreTranslate as the translator
    translated_md = translate_md(source_md, libretranslate)
    print("Translated Markdown with LibreTranslate:\n", translated_md)
    
    # Use MarianMT as the translator
    # translated_md = translate_md(source_md, load_Marian_translator())
    # print("Translated Markdown with MarianMT:\n", translated_md)
    
