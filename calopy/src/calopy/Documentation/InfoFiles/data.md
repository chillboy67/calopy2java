# Supported File Formats for Calopy  

Calopy currently supports the following file formats:  

- **Generic Input File** – Fully compatible with **Sable Systems**  
- **TSE PhenoMaster File**  
- **Columbus Instruments** (with limitations, see below)  


> **Important:**  
> Calopy only processes **recurring time points**. If daily time points are inconsistent, missing value handling will be applied. Time shifts within the dataset can lead to inaccurate analysis.  

---


## 1. Generic Input File (.csv, .tsv) – Sable Systems Compatible

Calopy supports a **flexible and structured** CSV file format that is fully compatible with **Sable Systems**. This format allows you to store both **Indirect Calorimetry (IC) data** and **metadata** in the same file or in separate files. Metadata can also be modified later in the **Preprocessing** section of Calopy.  


### Required Columns:  
- **Sample ID** (Mandatory) – The first column must contain unique sample identifiers (column name can vary).  
- **Sample Metadata** (Optional) – Additional columns can include metadata (e.g., phenotype, diet). If omitted, metadata can be uploaded separately.  
- **Date/Time Column** (Mandatory) – A column named **`date_time`** indicating the timestamp for each measurement (must be in a valid datetime format).  
- **Metabolic Variables** – The remaining columns store metabolic measurements (e.g., VO₂, VCO₂, EE, RER).  

### Example: Generic Data Table:

<style>
    table {
        width: 90%;
        border-collapse: collapse;
        margin: 25px 0;
        font-size: 14px;
        text-align: left;
    }
    table th, table td {
        padding: 12px 15px;
        border: 1px solid #ddd;
    }
    table th {
        background-color: #f4f4f4;
        font-weight: bold;
    }
    table tr:nth-child(even) {
        background-color: #f9f9f9;
    }
</style>

<table>
  <tr>
    <th>sample_id</th>
    <th>body_weight[g]</th>
    <th>diet</th>
    <th>date_time</th>
    <th>vo2</th>
    <th>vco2</th>
    <th>ee</th>
    <th>rer</th>
    <th>feed</th>
    <th>drink</th>
    <th>xt+yt</th>
  </tr>
  <tr>
    <td>1</td>
    <td>29.7</td>
    <td>chow</td>
    <td>2022-09-13 17:00:00</td>
    <td>64</td>
    <td>58</td>
    <td>0.314</td>
    <td>0.908</td>
    <td>0</td>
    <td>0</td>
    <td>5</td>
  </tr>
  <tr>
    <td>1</td>
    <td>29.7</td>
    <td>chow</td>
    <td>2022-09-13 17:15:00</td>
    <td>65</td>
    <td>60</td>
    <td>0.322</td>
    <td>0.920</td>
    <td>0</td>
    <td>0</td>
    <td>5</td>
  </tr>
  <tr>
    <td>1</td>
    <td>29.7</td>
    <td>chow</td>
    <td>2022-09-13 17:30:00</td>
    <td>65</td>
    <td>60</td>
    <td>0.322</td>
    <td>0.922</td>
    <td>0.04</td>
    <td>0.13</td>
    <td>207</td>
  </tr>
  <tr>
    <td>...</td>
    <td>...</td>
    <td>...</td>
    <td>...</td>
    <td>...</td>
    <td>...</td>
    <td>...</td>
    <td>...</td>
    <td>...</td>
    <td>...</td>
    <td>...</td>
  </tr>
  <tr>
    <td>3</td>
    <td>22</td>
    <td>chow</td>
    <td>2022-09-13 17:00:00</td>
    <td>70</td>
    <td>65</td>
    <td>0.349</td>
    <td>0.919</td>
    <td>0</td>
    <td>0.04</td>
    <td>592</td>
  </tr>
  <tr>
    <td>3</td>
    <td>32.1</td>
    <td>chow</td>
    <td>2022-09-13 17:15:00</td>
    <td>87</td>
    <td>80</td>
    <td>0.432</td>
    <td>0.916</td>
    <td>0.09</td>
    <td>0.03</td>
    <td>556</td>
  </tr>
  <tr>
    <td>...</td>
    <td>...</td>
    <td>...</td>
    <td>...</td>
    <td>...</td>
    <td>...</td>
    <td>...</td>
    <td>...</td>
    <td>...</td>
    <td>...</td>
    <td>...</td>
  </tr>
</table>


### Example: Metadata Table (.csv, .tsv)
Metadata can be stored in a separate file. The first column must contain **Sample IDs** that match those in the main data file.  


<style>
    table.metadata {
        width: 60%;
        border-collapse: collapse;
        margin: 25px 0;
        font-size: 16px;
        background-color: #f8f9fa;
    }
    table.metadata th, table.metadata td {
        padding: 10px 12px;
        border: 1px solid #ccc;
    }
    table.metadata th {
        background-color: #d1e7fd;
        font-weight: bold;
        text-align: center;
    }
    table.metadata tr:nth-child(even) {
        background-color: #f1f5f9;
    }
    table.metadata tr:hover {
        background-color: #e2e6ea;
    }
</style>

<table class="metadata">
  <tr>
    <td>sample_id</td>
    <td>Animal No.</td>
    <td>body_weight[g]</td>
    <td>weightGain[per]</td>
    <td>WeightGainLog</td>
    <td>genotype</td>
    <td>diet</td>
  </tr>
  <tr>
    <td>1</td>
    <td>1</td>
    <td>29.7</td>
    <td>54.2</td>
    <td>0.625</td>
    <td>C57Bl6j</td>
    <td>chow</td>
  </tr>
  <tr>
    <td>3</td>
    <td>17</td>
    <td>32.1</td>
    <td>43</td>
    <td>0.516</td>
    <td>C57Bl6n</td>
    <td>chow</td>
  </tr>
  <tr>
    <td>11</td>
    <td>3</td>
    <td>27</td>
    <td>63.3</td>
    <td>0.708</td>
    <td>C57Bl6j</td>
    <td>hfd</td>
  </tr>
  <tr>
    <td>19</td>
    <td>21</td>
    <td>30.6</td>
    <td>55.7</td>
    <td>0.639</td>
    <td>C57Bl6n</td>
    <td>hfd</td>
  </tr>
</table>

---

## 2. TSE PhenoMaster File (.csv, .tsv, .xlsx)  

To ensure proper parsing, the **raw, unmodified version** of the TSE PhenoMaster file must be uploaded. Altering the file structure may prevent Calopy from processing the data correctly.  

### File Structure:  
- **Property Section** – Contains metadata at the top of the file.  
- **Blank Separator Line** – Separates metadata from data measurements.  
- **Measurement Table** – Contains time-series data for metabolic variables.  


---

## 3. Columbus Instruments (CI) (.xlsx)

Since Columbus Instruments' **CI-Link** software exports each subject's data as a separate CSV file, a **workaround** is required to import these files into Calopy.  

### How to Format Columbus Instruments Files for Calopy:
- Combine all individual **CSV files** into a **single Excel file (.xlsx)**.  
- Assign each CSV file to its **own sheet** within the Excel file.  
- Name each sheet as `"Cage1"`, `"Cage2"`, etc.  
- Upload the **entire Excel file** to Calopy.  

### Automatically Extracted Metadata:
When you upload Columbus Instruments files, the following metadata is extracted automatically:  
- **Group/Cage**  
- **Subject ID**  
- **Subject Mass (g)**  
- **Reference Method**  
- **Heat Calculation Method**  

Additional metadata can be added using the **"Add/edit metadata"** dialog in Calopy.  

---



