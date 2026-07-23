import markdown
from shiny import reactive, render, ui
from calopy.Documentation.faq_shiny import faq_shiny

def faq_calopy(input, output, session):
    @output
    @render.ui
    @reactive.file_reader("calopy/Documentation/InfoFiles/FAQ.md")
    def faq_calopy_ui():
            return faq_shiny
