import markdown
import matplotlib
from shiny import reactive, render, ui

matplotlib.use("agg")

from calopy.Documentation.documentation_shiny import Documentation_shiny

def Documentation(input, output, session):
    documentation_update_toggle = reactive.Value(True)

    # def between_groups_update():
    #     print("between_groups_update_ui")
    #     documentation_update_toggle.set(not documentation_update_toggle())

    @output
    @render.ui
    def documentation_ui():
        print("documentation_ui")
        return Documentation_shiny

    ####################
    @reactive.file_reader("calopy/Documentation/InfoFiles/CalopyInfo.md")
    def read_info():
        with open("calopy/Documentation/InfoFiles/CalopyInfo.md", "r", encoding="utf-8") as f:
            content = f.read()
            return markdown.markdown(content)  # Convert markdown content to HTML

    @output
    @render.ui
    def introduction():
        return ui.HTML(read_info())

    ####################

    @reactive.file_reader("calopy/Documentation/InfoFiles/CalopyDataTypes.md")
    def read_datatypes():
        with open("calopy/Documentation/InfoFiles/CalopyDataTypes.md", "r", encoding="utf-8") as f:
            content = f.read()
            return markdown.markdown(content)  # Convert markdown content to HTML

    @output
    @render.ui
    def datatypes():
        return ui.HTML(read_datatypes())

    ####################
    @reactive.file_reader("calopy/Documentation/InfoFiles/data.md")
    def read_dataformat():
        with open("calopy/Documentation/InfoFiles/data.md", "r", encoding="utf-8") as f:
            content = f.read()
            return markdown.markdown(content)  # Convert markdown content to HTML

    @output
    @render.ui
    def dataformat():
        return ui.HTML(read_dataformat())

    ####################
    @reactive.file_reader("calopy/Documentation/InfoFiles/Preprocessing.md")
    def read_preprocessing():
        with open("calopy/Documentation/InfoFiles/Preprocessing.md", "r", encoding="utf-8") as f:
            content = f.read()
            return markdown.markdown(content)  # Convert markdown content to HTML

    @output
    @render.ui
    def preprocessing():
        return ui.HTML(read_preprocessing())

    ####################
    @reactive.file_reader("calopy/Documentation/InfoFiles/Filtering.md")
    def read_filtering():
        with open("calopy/Documentation/InfoFiles/Filtering.md", "r", encoding="utf-8") as f:
            content = f.read()
            return markdown.markdown(content)  # Convert markdown content to HTML

    @output
    @render.ui
    def filtering():
        return ui.HTML(read_filtering())

    ####################
    @reactive.file_reader("calopy/Documentation/InfoFiles/BMRRMR.md")
    def read_bmr():
        with open("calopy/Documentation/InfoFiles/BMRRMR.md", "r", encoding="utf-8") as f:
            content = f.read()
            return markdown.markdown(content)  # Convert markdown content to HTML

    @output
    @render.ui
    def BMR_RMR():
        return ui.HTML(read_bmr())

    ####################
    @reactive.file_reader("calopy/Documentation/InfoFiles/DataAnalysis.md")
    def read_analysis():
        with open("calopy/Documentation/InfoFiles/DataAnalysis.md", "r", encoding="utf-8") as f:
            content = f.read()
            return markdown.markdown(content)  # Convert markdown content to HTML

    @output
    @render.ui
    def dataanalysis():
        return ui.HTML(read_analysis())
