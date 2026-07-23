# Preprocessing 

This section allows initial data trimming, sample removal, and global parameter settings for your data.

---

### 1. Variable Selection
- **Select metabolic variable** and **grouping/aggregation** to be visualized.
- **Add/edit metadata**: View a table of available conditional and phenotypic data. Columns can be added or removed, and all fields can be directly edited. Additionally, a **metadata file** can be uploaded. The first column of the metadata file must contain a unique sample/mouse ID, which should match the ID provided in the additional data file.
- **Add/edit Metabolic Variable**: A number of key standardized metabolic variables can be added here eg: 
    - **Energy Intake** [kcal/h] – requires setting the kcal/g food value using Add/Edit Metadata
    - Recalculate **Heat Production/Energy Expenditure** (non-normalized by mouse body weight) to [kcal/h]

---

### 2. Data Trimming
Data trimming allows to eliminate measurement time from the beginning or end of your data, which can be helpful for acclimatization periods or adjusting measurements for whole days.

- **Set Start and Endpoints**: Define the start and end of the study/data for analysis. A day is considered as a 24-hour period from the start time.
- Set **Dark/Light Phases**.
- **Set All Samples Start the Same Day**: Merge experiments conducted in batches by setting the measurement start time to be the same for all subjects. 

---

### 3. Options
- **Remove samples**  Exclude specific subjects (e.g., boxes/animals) from the analysis.
- **Plot x-labels for days**:  Replace calendar day labels with increasing day numbers (day 1, day 2, etc.).
---

#### Handling Missing Values:
- **Short gaps**: Missing values occurring in short sequences (up to 5 consecutive values) are imputed using linear interpolation, similar to outlier handling. However, excessive missing values in a single region may reduce accuracy, as values are filled sequentially.
- **Feature extraction in 24-hour segments**: For selecting features with the 24-hour split option, a more advanced approach is used. Missing data at the end of a measurement period often prevents capturing a full day. To address this, gaps of up to 3 hours are inferred to maintain complete 24-hour records. This is done using the Generalized Additive Model (GAM), which effectively imputes multiple values while accounting for circadian rhythms.





