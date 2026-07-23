import datetime
import io
import os
from datetime import date
import tempfile
import pandas as pd

from shiny import reactive, render, ui
from shiny.types import FileInfo

from calopy.between_groups.between_groups_controller import between_groups
from calopy.calopy_store import addCaliDataToStore, caliData, caliState, downloadCaliStoreObject, loadCaliStoreObject
from calopy.calopy_ui import PREPROCESSING
from calopy.conditions.conditions_controller import conditions
from calopy.conditions.DialogConditions import dialogConditions
from calopy.data import CaliDataTse
from calopy.data.DataMerger import DataMerger
from calopy.Documentation.documentation_controller import Documentation
from calopy.Documentation.aboutCalopy_controller import about_calopy
from calopy.Documentation.faq_controller import faq_calopy
from calopy.energy_balance.energy_balance_controller import energy_balance

from calopy.loader.LoaderCsv import LoaderCsv
from calopy.loader.LoaderTse import LoaderTse
from calopy.loader.LoaderColumbus import LoaderColumbus
from calopy.preprocessed.DialogEditAdditionalData import dialogEditAdditionalData
from calopy.preprocessed.preprocessed_controller import preprocessed, preprocessed_load_state
from calopy.rmr.rmr_controller import rmr
#from calopy.scatter.scatter_controller import scatter
from calopy.smoothing.smoothing_controller import smoothing
from calopy.window.window_controller import window_analysis
from calopy.writer.TseWriter import TseWriter
from calopy.writer.CalopyWriter import CalopyWriter


### set the max request size to 500 MB (0.5 * 1024 * 1024 * 1024 bytes)
MAX_REQUEST_SIZE = 536870912 # 0.5 * 1024 * 1024 * 1024
SHOW_ANNOUNCEMENT = False   # <-- flip to True when you want the popup

def calopy_server(input, output, session):
    preprocessed(input, output, session)
    smoothing(input, output, session)
    rmr(input, output, session)
    dialogEditAdditionalData(input, output, session)
    # scatter(input, output, session)
    conditions(input, output, session)
    dialogConditions(input, output, session)
    window_analysis(input, output, session)
    between_groups(input, output, session)
    energy_balance(input, output, session)
    Documentation(input, output, session)
    about_calopy(output, session)
    faq_calopy(input, output, session)


    if SHOW_ANNOUNCEMENT:
        @reactive.effect
        def _():
            ui.modal_show(
                ui.modal(
                    ui.HTML("""
                         <p><strong>Dear Calopy users,</strong></p>
                        <p>Due to a complete migration of our institution’s server infrastructure, 
                        Calopy will be offline from <strong>September 15 to September 19</strong>.</p>
                        <p>Stay tuned,<br><em>Your Calopy Dev Team</em></p>
                    """),
                    title="Service Announcement",
                    easy_close=True,
                    footer=ui.modal_button("Got it!")
                )
            )


    @render.image
    def logo_image_calopy():
        img = {
            "src": "./calopy/assets/AdditionalFiles/calopy_logo.png",
            "height": "70px",
        }
        return img

    @render.image
    def logo_image_helmholtz():
        img = {
            "src": "./calopy/assets/AdditionalFiles/logo_helmholtz.png",
            "height": "70px",
        }
        return img

    @render.text
    def help_show_input_format_text():
        with open("./calopy/assets/AdditionalFiles/help_example_csv.txt", "r") as file:
            txt_lines = file.read()

        return txt_lines

    @reactive.Effect
    @reactive.event(input.tse_file_loader)
    def loadDataTse():
        print("loadDataTse")
        f: list[FileInfo] = input.tse_file_loader()
        if passed_filesize_uploaded(f):
            data, state = LoaderTse(f[0]["datapath"]).loadData()
            if state != "failed_reading":
                addCaliDataToStore(session, data, state)
                update_ui()

    @reactive.Effect
    @reactive.event(input.csv_file_loader)
    def loadDataCsv():
        print("loadDataCsv")
        f: list[FileInfo] = input.csv_file_loader()
        if passed_filesize_uploaded(f):
            data, state = LoaderCsv(filename=f[0]["datapath"]).loadData()
            if data is None:
                print(state)
                # return state
            addCaliDataToStore(session, data, state)
            update_ui()

    @reactive.Effect
    @reactive.event(input.columbus_file_loader)
    def loadDataColumbus():
        print("loadDataColumbus")
        f: list[FileInfo] = input.columbus_file_loader()
        if passed_filesize_uploaded(f):
            loader = LoaderColumbus(f[0]["datapath"])
            CIdataframe = loader.loadData()
            print(f[0])
            if CIdataframe is None:
                print("========Error loading CIdataframe======")
            else:
                data, state = LoaderCsv(dataframe=CIdataframe).loadData()
                addCaliDataToStore(session, data, state)
                update_ui()


    @reactive.Effect
    @reactive.event(input.calistore_file_loader)
    def loadDataCaliStore():
        print("loadDataCaliStore")
        f: list[FileInfo] = input.calistore_file_loader()
        if passed_filesize_uploaded(f):
            loadCaliStoreObject(session, f[0]["datapath"])
            update_ui()




    @reactive.Effect
    @reactive.event(input.tse_file_merge)
    def mergeData():
        print("mergeData")
        f: list[FileInfo] = input.tse_file_merge()
        mergeData, state = LoaderTse(f[0]["datapath"]).loadDataTse()
        addCaliDataToStore(session, DataMerger(caliData(session), mergeData).mergedData(), None)
        update_ui()

    def update_ui():
        ui.update_navs("selected_feature", selected=PREPROCESSING)
        preprocessed_load_state()

    @reactive.Effect
    @reactive.event(input.load_test_data)
    def loadTestData():
        print("loadTestData")
        data, state = LoaderTse("./calopy/assets/AdditionalFiles/example_tse.tsv").loadData()
        addCaliDataToStore(session, data, state)
        update_ui()

    @render.download()
    def download_example_data():
        path = "./calopy/assets/AdditionalFiles/example_csv.csv"
        return path

    @render.download(
        filename=lambda: f"calidata-download-{datetime.datetime.now().isoformat()}.tse"
    )
    def tse_file_downloader():
        print("downloadData")
        with io.BytesIO() as buf:
            TseWriter(caliData(session), caliState(session)).writeToFile(buf)
            yield buf.getvalue()

    @render.download(
        filename=lambda: f"calopy-metabolic-variables-{datetime.datetime.now().isoformat()}.csv"
    )
    def calopy_metabolic_variables_downloader():
        print("downloadData")
        with io.BytesIO() as buf:
            CalopyWriter(caliData(session), caliState(session)).writeMetabolicVarsToFile(buf)
            yield buf.getvalue()

    @render.download(
        filename=lambda: f"calopy-metadata-{datetime.datetime.now().isoformat()}.csv"
    )
    def calopy_metadata_downloader():
        print("downloadData")
        with io.BytesIO() as buf:
            CalopyWriter(caliData(session), caliState(session)).writeMetadataToFile(buf)
            yield buf.getvalue()

    @render.download(
        filename=lambda: f"calopy-settings-{datetime.datetime.now().isoformat()}.csv"
    )
    def calopy_settings_downloader():
        print("downloadData")
        with io.BytesIO() as buf:
            CalopyWriter(caliData(session), caliState(session)).writeSettingsToFile(buf)
            yield buf.getvalue()


    @render.download(
        filename=lambda: f"calidata-download-{datetime.datetime.now().isoformat()}.pkl"
    )
    def tse_calistore_downloader():
        print("downloadCaliStoreData")
        with io.BytesIO() as buf:
            downloadCaliStoreObject(session, buf)
            yield buf.getvalue()


    def passed_filesize_uploaded(f):
        if f[0]["size"] > MAX_REQUEST_SIZE:
            print(f"File size exceeds the limit of {MAX_REQUEST_SIZE / (1024 * 1024):.2f} MB. Uploaded file size: {f[0]['size'] / (1024 * 1024):.2f} MB")
            return False
        else:
            return True

    @render.download()
    def download_howto_top():
        path = "./calopy/assets/AdditionalFiles/Calopy_HOWTO.pdf"
        return path
