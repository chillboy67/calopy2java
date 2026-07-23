from shiny import ui

with open("calopy/Documentation/InfoFiles/FAQ.md", "r", encoding="utf-8") as f:
    faq_md = f.read()

faq_shiny = ui.column(5,
            ui.h2("FAQ"),
            ui.markdown(faq_md)
            )
