import logging
import os
import re

import numpy as np
import pandas as pd

from calopy.data.CaliDataTse import CaliDataTse
from calopy.maths.dataframe_utils import replaceNaNvaluesInDataFrame
from calopy.maths.series_utils import parse_date_times

class LoaderColumbus:
    logger = logging.getLogger(__name__)

    def __init__(self, filename):
        self.filename = filename
        self.raw_df = None
        print("load file {} on {}".format(filename, os.getcwd()))

    def loadData(self):
        print("loadData Columbus Instruments")

        try:
            ci_excel = pd.ExcelFile(self.filename)
            # Get all cage sheets
            cage_sheets = [sheet for sheet in ci_excel.sheet_names if "Cage" in sheet]
            print(f"Processing cage sheets: {cage_sheets}")
            
            combined_data = []
            for sheet_name in cage_sheets:
                # Extract only the numeric part of the sheet name
                numeric_sample_id = re.findall(r"\d+", sheet_name)  # Extract all numbers
                numeric_sample_id = int(
                    numeric_sample_id[0]) if numeric_sample_id else None  # Take the first number or set to None
                if numeric_sample_id is None:
                    continue  # Skip sheets without numeric identifiers

                # Read the entire sheet first to locate the first occurrence of '==========='
                raw_df = pd.read_excel(ci_excel, sheet_name=sheet_name, header=None)

                # Extract metadata before ":DATA"
                metadata = {}
                metadata_keys = {
                    "Group/Cage": "group_cage",
                    "Subject ID": "subject_id",
                    "Subject Mass (G)": "subject_mass",
                    "Reference Method": "reference_method",
                    "Heat Calculation Method": "heat_calc_method"
                }
                for i, line in enumerate(raw_df.iloc[:, 0]):  # Iterate over first column
                    if isinstance(line, str) and line.startswith(":DATA"):
                        data_start = i + 1
                        break

                    parts = [str(cell).strip() for cell in raw_df.iloc[i, :].dropna()]
                    if len(parts) >= 2:
                        key, value = parts[0], parts[1]
                        if key in metadata_keys:  # Only include relevant metadata fields
                            metadata[metadata_keys[key]] = value

                # Find the index of the first row after '==========='
                separator_row = raw_df[
                    raw_df.apply(lambda row: row.astype(str).str.contains("=========", na=False)).any(axis=1)].index
                if len(separator_row) == 0:
                    continue  # Skip sheet if no separator found
                start_row = separator_row[0] + 1  # The first row after '==========='

                # Read the sheet again, starting from the detected row
                df_headers = pd.read_excel(ci_excel, sheet_name=sheet_name, skiprows=range(start_row), header=None,
                                           nrows=2)
                merged_headers = [f"{col} [{unit}]" if pd.notna(unit) else col for col, unit in
                                  zip(df_headers.iloc[0], df_headers.iloc[1])]

                # Read actual data after the two header rows
                df = pd.read_excel(ci_excel, sheet_name=sheet_name, skiprows=start_row + 2)

                # Assign merged headers
                df.columns = merged_headers
                # Drop rows that contain '===========' in any column
                df = df[~df.astype(str).apply(lambda row: row.str.contains('=========', na=False)).any(axis=1)]

                # Add a "sample_id" column to track data from different sheets
                df.insert(0, "sample_id", numeric_sample_id)

                # Convert metadata dictionary to DataFrame with one row, repeated for all data rows
                metadata_df = pd.DataFrame(metadata, index=df.index)

                # Rename "DATE/TIME" to "date_time" (if present)
                df.rename(columns=lambda x: "date_time" if "DATE/TIME" in x else x, inplace=True)

                # Drop the columns "CHAN" and "INTERVAL [#]" if they exist
                columns_to_remove = ["CHAN", "INTERVAL [#]"]
                df.drop(columns=[col for col in columns_to_remove if col in df.columns], errors="ignore", inplace=True)

                # Ensure metadata is inserted **between** `sample_id` and `date_time`
                df = pd.concat([df.iloc[:, :1], metadata_df, df.iloc[:, 1:]], axis=1)

                # Check if A2 is empty and if so, normalize VO2 and VCO2 and calculate WEIR
                if pd.isna(raw_df.iloc[1, 0]):  # A2 is row 1, column 0 (0-based indexing)
                    df = self.Normalize_VO2_VCO2(df, ci_excel, sheet_name)
                    if df is not None:
                        df = self.ee_weir(df)

                # Append cleaned data to the list
                combined_data.append(df)

            # Merge all sheets into a single DataFrame
            final_df = pd.concat(combined_data, ignore_index=True)
            # Remove the first unnamed column if it exists
            if final_df.columns[0] == "":
                final_df = final_df.iloc[:, 1:]

            return final_df

        except Exception as e:
            error_message = "Error loading csv file: " + str(e)
            print(error_message)
            return None

    def Normalize_VO2_VCO2(self, df, ci_excel, sheet_name):
        try:
            # Get mass from the existing dataframe (B11)
            mass_g = float(df.iloc[10, 1])  # B11 is row 10, column 1 (0-based indexing)
            mass_kg = mass_g / 1000

            # Find VO2 and VCO2 columns
            vo2_column = [col for col in df.columns if "VO2" in col.upper()]
            vco2_column = [col for col in df.columns if "VCO2" in col.upper()]

            # Compute VO2[ml/hr]
            if vo2_column:
                vo2_column = vo2_column[0]
                df["VO2 [ml/hr]"] = df[vo2_column].astype(float) * mass_kg

            # Compute VCO2[ml/hr]
            if vco2_column:
                vco2_column = vco2_column[0]
                df["VCO2 [ml/hr]"] = df[vco2_column].astype(float) * mass_kg
            return df

        except Exception as e:
            print(f"==========================Error in Normalize_VO2_VCO2: {str(e)}==================")
            return df

    def ee_weir(self, df):
        try:
            # Find normalized VO2 and VCO2 columns
            norm_vo2_column = "VO2 [ml/hr]"
            norm_vco2_column = "VCO2 [ml/hr]"
            # Calculate EE (WEIR)
            df["EE (WEIR) [kcal/hr]"] = ((df[norm_vo2_column].astype(float)/1000) * 3.941 + (df[norm_vco2_column].astype(float)/1000) * 1.106)
            return df
        except Exception as e:
            print(f"=============================Error in ee_weir calculation: {str(e)} ================================")
            return df

    def parseData(self):
        return
