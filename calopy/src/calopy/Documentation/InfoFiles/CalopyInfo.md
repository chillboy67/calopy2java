# Data Analysis with Calopy

Calopy is designed to support flexible, exploratory analysis of Indirect Calorimetry (IC) data, enabling you to investigate a variety of relationships within your dataset. The following analysis options are available:


- Between-Group Comparison  
- Temporal Conditions (Within-Group)  
- Time Window Comparison  


---
### Data Types and Format

Calopy supports two main types of data (**see Data Types**):

- **Metabolic Variables** are time-resolved measurements such as oxygen consumption (VO₂), carbon dioxide production (VCO₂), energy expenditure (EE), and respiratory exchange ratio (RER). Standardized units are recommended to ensure consistency in data analysis. Additional variables like food intake, water intake, and activity are also supported.

- **Metadata** includes descriptive data associated with each subject, classified into Phenotypic Variables (PVs) (e.g., body weight, age) and Conditional Variables (CVs) (e.g., genotype, treatment). Metadata can be imported through CSV files or manually added.


In addition, Calopy enables **feature extraction** from **metabolic variables**, allowing the calculation of various statistical metrics such as mean, median, amplitude, and peak values, with options for global analysis or 24-hour split intervals.


Calopy currently supports two data formats (**see Data Format**):

- **Generic CSV Files** (.csv) – Stores metabolic data and metadata in a single or separate file, requiring a Sample ID, Date/Time Column, and Metabolic Variables (e.g., VO₂, VCO₂, EE, RER). Optional additional **metadata files** should match Sample IDs and include attributes like body weight, diet, and genotype. 

- **TSE PhenoMaster Files** (.csv, .tsv, .xlsx) – Must be raw and unmodified for correct parsing. The file structure includes a property section, a blank separator line, and a measurement table with consistent time points to ensure accurate analysis.

- **Columbus Instruments Files (CI)** (.xlsx) – Currently, only basic support is available for **CI-Link software exported files**, requiring a small workaround: all exported CSV files must be merged into a single `.xlsx` file, with each sheet named **Cage1, Cage2, ...**.

---
### Download and Save Calopy Data and Settings

Calopy allows users to download and save working data in three different file formats:  

- **IC Data File** – A CSV file containing all **unprocessed metabolic variables** (raw data) in a simple `.csv` format. Note that **processed and filtered data** can be downloaded directly using the **plot download buttons**.  

- **Metadata File** – A CSV file containing **all metadata** in a structured table.  

- **Settings File** – A text file that includes **preprocessing settings and variables** used for data analysis. *(Due to frequent code updates, this list may sometimes be incomplete.)*

---
### Exploratory Data Analysis

Calopy provides a flexible interface for exploring relationships within your data, making it easy to test different hypotheses and uncover patterns. For instance:

- In **Between-Group Comparisons**, you can select any continuous data as the response or dependent variable. The predictive variable can be chosen from either:  
    - **Categorical variables** (e.g., treatment, genotype) for analyses like ANOVA or ANCOVA.  
    - **Continuous variables** (e.g., body weight, age) for regression analysis.  
<br>

- In **Temporal Conditions (Within-Group)** you can define various temporal conditions and analyze changes in metabolic variables across these conditions by including the animal/box as a within-subject factor. The analysis can be extended by adding categorical data as covariates.


- In **Time Window Comparison**, the analysis of metabolic variables is achieved by segmenting the data into consecutive or overlapping time windows, which allows for groupwise comparisons using ANOVA across these time windows.

This flexibility allows for comprehensive exploration of your data, whether you're comparing groups or examining trends over time.

--- 
