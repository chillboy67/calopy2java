##### **Calopy – Frequently Asked Questions**

***What is Calopy?***  
Calopy is an open-source web application for analyzing indirect calorimetry (IC) data. Built with Shiny for Python, it runs in any web browser and can be used both online or locally.

***Is there a user guide or additional help available?***  
Yes. A comprehensive User How-To, including detailed instructions and use cases, is available in the **Help** or **Info & Contact** sections of the app.

***How often is Calopy updated?***  
We actively maintain and improve Calopy. New features and fixes are released regularly, and update logs are available on the project’s website or Git repository.

***I found a bug. What should I do?***  
Great — you can help us improve! Please contact us directly so we can fix it.  
Even better: if you're a Python developer (or want to become one), feel free to clone the code, implement a fix, and get in touch — we’ll help you integrate it into the main repository.

***I’ve developed a great method for analyzing IC data — can you include it in Calopy?***  
Awesome! Please reach out to us, and we’ll gladly explore ways to integrate your method into Calopy together.

***I'm missing feature XYZ — why isn't it included?***  
We built Calopy to deliver both basic and extended IC data analysis, including tools like filtering, feature extraction, and RMR/BMR estimation. Our goal was to first release a robust and functional version. A list of additional planned features and methods is already in the pipeline. If you need a specific feature, contact us — we’re happy to help where we can.

***How should I cite Calopy?***  
Please cite:  
Loipfinger S, Grosholz M, Kumar S, Erbilir H, Dyar KA, Müller TD, Grein S, Rozman J, Klingenspor M, Meyer C, Lutter D. Calopy — An Advanced Framework for the Integration and Analysis of Indirect Calorimetry Data. *Nature Metabolism*, 2025. <br />
DOI: [https://doi.org/10.1038/s42255-025-01316-8](https://doi.org/10.1038/s42255-025-01316-8)

---

##### **Data Upload & File Handling**

***What file formats does Calopy support?***  
- **TSE PhenoMaster** raw `.csv` files  
- **Sable Systems** `.csv` export files (via generic format)  
- Basic support for **Columbus Instruments** `.xlsx`  
- A **generic format** widely compatible with **Sable Systems** 

***What is the maximum upload file size?***  
Up to **500 MB** per file.

***Why is my TSE PhenoMaster file not working?***  
This usually occurs if the file has been edited. Calopy requires the original, unmodified TSE export file for accurate processing.

***How do I upload Columbus Instruments data?***  
Columbus Instruments exports each cage’s data as a separate `.csv` file. To use these with Calopy:  
1. Combine the individual `.csv` files into a single `.xlsx` file.  
2. Assign each cage its own sheet (e.g., *Cage1*, *Cage2*, etc.).  
3. Upload the resulting `.xlsx` file to Calopy.

***Can I compare multiple experimental runs or datasets?***  
Yes, but it requires a small workaround.
Calopy lets you merge and align datasets from different runs using this approach:

1. Upload your files one by one.
2. Use Download Data → Download IC data file for each run.
3. Merge these files into a single dataset and upload it again.
4. Ensure that each animal has a unique ID (sample_id).
5. Finally, use the “Make all samples start at the same day” checkbox.

This should do the trick.

Our original merging function was unreliable and difficult to maintain across multiple formats, but we plan to provide a more robust solution in future versions.


---

##### **Preprocessing, Analysis & Output**

***Can I save my session or analysis settings?***  
Yes. Calopy allows you to download a settings file that includes all preprocessing steps and selected variables. This helps with documentation, reproducibility, and continuing analyses later.  
We previously included support for downloading/uploading full Python session objects, but had to deactivate this feature due to security concerns. If you’re running Calopy locally and want to reactivate this, feel free to contact us.

***Can I reload saved data into Calopy?***  
See above. While automatic session reloading is not currently supported, you can manually re-upload your data and reapply the saved settings.

***Does Calopy support feature extraction from filtered data?***  
Yes. Calopy enables you to extract features such as daily maxima, minima, amplitude, and area under the curve (AUC) — both from raw and filtered data.

***Can I export my plots and results?***  
Yes. You can download plots, statistical results, and processed datasets for use in publications or presentations.

---

##### **Statistical Methods**

***Can I run custom statistical tests?***  
Calopy supports standard methods like ANOVA, ANCOVA, and regression. While user-defined statistical formulas are not yet supported, we plan to add more flexibility in future versions.

***Why is normalizing metabolic variables by body mass discouraged?***  
Although commonly done, normalizing energy expenditure by body or lean mass can introduce bias and obscure meaningful results. Regression-based approaches such as **ANCOVA** are preferred, as they statistically separate mass-dependent from mass-independent effects, providing more accurate and interpretable insights.

***What’s the difference between ANOVA and ANCOVA?***  
- **ANOVA** tests for differences in numeric outcomes across groups:  
  - *One-way ANOVA*: one categorical grouping variable  
  - *Two-way ANOVA*: two categorical variables and their interaction  
- **ANCOVA** compares group means while adjusting for numeric or categorical covariates.

***Where can I learn more about IC-specific statistical methods?***  
We recommend the following resources:  
* Tschöp, M.H. et al. *Nat. Methods* 9, 57–63 (2012). https://doi.org/10.1038/nmeth.1806  
* Speakman, J.R. & Krol, E. *J. Comp. Physiol. B* 175, 475–482 (2005). https://doi.org/10.1007/s00360-005-0017-1  
* Harris, J.E. et al. *J. Acad. Nutr. Diet.* 112, 90–98 (2012).
