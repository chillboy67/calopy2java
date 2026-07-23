# Data Analysis

Calopy is designed to facilitate exploratory analysis of Indirect Calorimetry (IC) data, offering a wide range of flexible options for investigating your dataset. The following analysis options are currently available:  
  
  - Between-Group Comparison   
  - Temporal Conditions (Within group)  
  - Time Window analysis  

---

### 1. Between-Group Comparison

The **between-group analysis** tests various dependent variables across different conditions or treatments (i.e., conditional variables). Calopy's key strength lies in its flexibility to select and combine predictive and dependent variables:  

- **Dependent Variables**:  
  These can include metabolic variables, derived data features, or phenotypic variables.  

- **Flexibility in Predictive Variable Selection**:  
    - Perform one-way ANOVA comparisons using grouping or aggregation variables selected from available conditional variables.  
    - Add a **second grouping variable** for two-way ANOVA.  
    - Split raw metabolic data into **light (day) and dark (night) phases**.  
    - Use a **continuous covariate** (e.g., body weight) for ANCOVA analysis, which is essential for comparing energy expenditure [1]*.  
    - Apply **linear regression** by excluding grouping/aggregation as a predictive factor. Continuous phenotypic variables and features extracted from metabolic data can serve as predictive variables.  

*For large differences in the body weight of the groups compared we do not recommend the use of an ANCOVA here since interpretability is limited.  

---


### 2. Temporal Conditions (Within Groups)

The **temporal conditions analysis** compares changes in a specific observed metabolic variable across multiple temporal conditions within the same group:  

- **Temporal Conditions**:  
  You can define an unlimited number of temporal conditions.  

- **Dependent Variable Selection**:  
  Select features from any metabolic variable. It is advisable to avoid using day-specific features, as they might interfere with the chosen temporal conditions.  

- **Add Grouping/Aggregation Variable**:  
  You can include an additional grouping or aggregation covariate from conditional variables to perform repeated measures ANOVA.  


---

### 3. Time Window Comparison

**Time window analysis** focuses on pairwise comparisons of metabolic variables segmented into consecutive or overlapping time windows. Group comparisons using ANOVA are performed based on a selected categorical variable. This method divides data curves into multiple small windows and calculates the mean for each time segment, enabling group comparisons over the measurement period.

- **Adjustable Window Sizes**:  
  Window sizes can be customized according to the temporal sampling rate.  

- **Allow for overlapping windows**:  
  Overlapping windows can be configured as needed.  

---

### 4. Energy Balance

**Energy Balance** compares Energy Intake (EI) with Energy Expenditure (EE).
EI can be calculated using user-defined values for the energy content of the given food in [kcal/g], when food intake is provided in grams [g].

---

#### References

1. Müller TD, Klingenspor M, Tschöp MH. Revisiting energy expenditure: how to correct mouse metabolic rate for body mass. Nat Metab. 2021 Sep;3(9):1134-1136. doi: 10.1038/s42255-021-00451-2. Erratum in: Nat Metab. 2021 Oct;3(10):1433. PMID: 34489606. [https://doi.org/10.1038/s42255-021-00451-2](https://doi.org/10.1038/s42255-021-00451-2)
