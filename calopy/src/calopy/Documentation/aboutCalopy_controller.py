from shiny import render
from calopy.Documentation.aboutCalopy_shiny import aboutCalopy_Info


def about_calopy(output, session):
    @output
    @render.ui
    def about_calopy_ui():
        print("documentation_ui")
        return aboutCalopy_Info

    @render.download()
    def download_howto():
        path = "./calopy/assets/AdditionalFiles/Calopy_HOWTO.pdf"
        return path
