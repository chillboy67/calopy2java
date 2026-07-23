import markdown
import os
from shiny import reactive, render, ui

@reactive.file_reader("src/calopy/Documentation/InfoFiles/FAQ.md")
def read_faq():
    print("Reading FAQ.md file...")
    file_path = "src/calopy/Documentation/InfoFiles/FAQ.md"
    print(f"Attempting to read file at: {os.path.abspath(file_path)}")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            print(f"Successfully read FAQ.md. Content length: {len(content)} characters")
            html_content = markdown.markdown(content)
            print(f"Successfully converted markdown to HTML. HTML length: {len(html_content)} characters")
            return html_content
    except Exception as e:
        print(f"Error reading FAQ.md: {str(e)}")
        return f"Error loading FAQ: {str(e)}"

@render.ui
def faq_calopy_ui():
    print("Rendering FAQ UI...")
    content = read_faq()
    print(f"FAQ content type: {type(content)}")
    return ui.HTML(content) 