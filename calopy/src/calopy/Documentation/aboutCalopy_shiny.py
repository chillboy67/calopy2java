from shiny import ui
from calopy.shared_ui.get_git_version import get_calopy_gitlab_version, get_git_version_tag


aboutCalopy_Info = ui.column(5,
    ui.h3("About Calopy"),
    ui.markdown("This application provides advanced statistical analysis for indirect calorimetry data."),
    ui.markdown("Please read our **Documentation** for background information, data and format descriptions, Calopy features and statistical methods."),
    ui.markdown("A detailed **User HowTo** including additional information's and use-case examples can be downloaded here:"),
    ui.row(ui.column(4,ui.download_button("download_howto", "Download User HowTo", class_="btn-primary"))),
    ui.hr(),
    ui.h5("Contact"),
    ui.markdown("Calopy is a development of the Computational Discovery Research group [CDR](https://www.helmholtz-munich.de/en/templates/institute-page/research-groups-1-63/metabolism/computational-discovery-research) at Helmholtz Munich. "
                "Contact us for support and contributions at: "),
    ui.a("calopy(at)helmholtz-munich.de", href="mailto:calopy@helmholtz-munich.de"),
    ui.hr(),
    ui.h5("Development"),
    ui.markdown("Calopy source code is available at our gitlab repository at: [Calopy Gitlab](https://gitlab.com/computational-discovery-research/calopy) "),
    ui.markdown("We gratefully thank our contributors for their fabulous help in designing and and developing Calopy: Stefan Loipfinger, Matthias Grosholz, Santhosh Kumar, Stefan Haffner and Helin Erbilir."),
    ui.markdown("Helmholtz Munich 2025"),
    ui.hr(),
    ui.h5("Version"),
    ui.markdown(f"Running Calopy version: `{get_git_version_tag()}`"),
    ui.markdown(f"Latest Calopy release: `{get_calopy_gitlab_version()}`"),
    ui.hr(),
    ui.h5("Publications"),
    ui.markdown("- Loipfinger et al.; Calopy – An Advanced Framework for the Integration and Analysis of Indirect Calorimetry Data; *Nature Metabolism*, 2025. <br /> "
                "DOI: [https://doi.org/10.1038/s42255-025-01316-8](https://doi.org/10.1038/s42255-025-01316-8)"),
    ui.hr(),
    ui.h5("Legal Notice"),
    ui.p("This application is provided as-is without any warranties."),
)
