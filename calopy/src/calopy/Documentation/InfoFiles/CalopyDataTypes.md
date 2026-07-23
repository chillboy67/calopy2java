# Calopy Data Types

Calopy distinguishes between two primary types of data:

- **Metabolic Variables (MVs)**
- **Metadata** 

---

### Metabolic Variables:  
**Metabolic variables** refer to time-resolved measurements recorded for each subject (e.g., VO<sub>2</sub>, VCO<sub>2</sub>, activity, etc.). Although Calopy allows for any type of time-resolved data, we strongly recommend using standardized units for consistency and comparability. To prevent statistical artifacts in IC data analysis, we advise using the following units for commonly measured metabolic parameters:  


<style>
    table {
        width: 30%;
        border-collapse: collapse;
        margin: 15px 0;
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
    <th>Metabolic Variable</th>
    <th>Abbrevation</th>
    <th>Units</th>
  </tr>
  <tr>
    <td>Oxygen Consumption</td>
    <td>VO<sub>2</sub></td>
    <td>mL/h</td>
  </tr>
  <tr>
    <td>Carbon Dioxide Production</td>
    <td>VCO<sub>2</sub></td>
    <td>mL/h</td>
  </tr>
  <tr>
    <td>Energy Expenditure</td>
    <td>EE</td>
    <td>kcal/h</td>
  </tr>
  <tr>
    <td>Respiratory Exchange Ratio </td>
    <td>RER</td>
    <td>dimensionless</td>
  </tr>
</table>

Further metabolic variables depend on the experimental setup and system used. Below are additional recommended units:

- **Food intake (FI): g/h**.  
Most systems export food intake as grams per sample rate **[g]**. Since **g/h** is the preferred standardized unit, future versions of Calopy will include automatic unit conversion. Currently, only **cumulative food intake** conversion is supported.  
- **Water intake (WI): mL/h**.   
Similarly, mL/h is recommended as the standard unit. Calopy will be updated accordingly.
- **Energy intake (EI): kcal/h**.   
EI depends on the caloric content of the provided food. Automated **EI** calculation is not yet implemented but will be introduced soon. We recommend using **kcal/h** for direct comparability with **EE**.
- **Activity: m**.   
Activity is commonly measured as distance (in **meters [m]**) or **beam break counts**. While [SI units](https://en.wikipedia.org/wiki/International_System_of_Units) are recommended, conversion depends on the system used. Additionally, **activity is generally a noisy measure and should be interpreted with caution.**

---

### Features: 
Calopy allows the estimation of various continuous **features** from metabolic variables, such as mean values, maxima, or amplitude.  
**Note:** Feature values are highly dependent on the selected filters, which can impact your analysis and potentially lead to erroneous results or misinterpretations. Use with caution.

Features available:

- **raw data**: each value is considered individually
- **cumulative total**: the sum of all values over time
- **AUC** (Area Under Curve): computed using the composite Simpson’s rule and normalized per hour
- **mean**
- **median**
- **minimum**
- **maximum**
- **amplitude**: the difference between the minimum and maximum value
- **maximum peak**: identified using a peak detection method [Scipy.signal](https://docs.scipy.org/doc/scipy/reference/signal.html). detects the peak over a time series (not necessarily the absolute maximum). The algorithmn uses 2× standard devation as prominence, a minimum height of the mean value, und a minimum distance of 18 hours between peaks.
- **minimum peak**: similar to maximum peak, only for minimum
    
Features can be selected as:

- **global**  - use metabolic variable unrestricted
- **24h split**  - split data into days/24h intervals*, use all daily features
- **24h split and median** - split data into days/24h intervals\*, use median of feature

\* a day is defined as the 24h interval from measurement start

---

### Metadata:
**Metadata** refers to the descriptive data associated with each subject (e.g., mouse or cage) in an IC experiment. Calopy automatically differentiates between two basic types of **Metadata**:

- **Phenotypic variables (PVs):** These are continuous or numerical attributes that describe individual characteristics, such as body weight, age, or body temperature.  
- **Conditional Variables (CVs):** These are categorical or discrete variables used for grouping or categorization. They typically represent experimental conditions, such as Genotype, Treatment, or Diet.

Metadata can be included either in a generic data file (\*.csv file) or TSE data format or may be added using an additional metadata table (\*.csv) within **preprocessing** tab (see **Data Format**).  

For standardized and artifact-free data analysis we strongly recommend to include at least body weight [g] as metadata.


---


