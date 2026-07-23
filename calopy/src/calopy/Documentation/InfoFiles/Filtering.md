# Filtering

Filtering includes various data filters. In addition to flexible outlier removal, we offer several options for data smoothing and feature extraction.
The plot shows the selected metabolic variable for individual subjects/boxes. Navigate through your subjects/boxes by using the **prev** and **next** buttons.
 

**Filtering** and **outlier removal** can be customized separately for each variable with individual settings. All current settings are summarized in the table below the current metabolic variable plot.

>##### Limitations 
>**The filters provided here involve data approximation and reduction, which may limit the interpretability of the results.**

---

### 1. Variable Selection

- **Select metabolic variable**: Choose the metabolic variable you want to visualize.
- **Navigate Through Animals**: Use the "Prev" and "Next" buttons to navigate between animals/boxes.

---

### 2. Curve Fitting/Filtering
Curve fitting helps manage noisy raw data caused by factors such as measurement inaccuracies. By applying various curve-fitting and spline functions, it's possible to reveal underlying trends and extract important features like **minima**, **maxima**, **amplitude**, and **phase shifts**. Different filters can be applied to different metabolic variables.  

*We recommend testing multiple methods, as no single approach works for all data types. Inappropriate selections may lead to incorrect data interpretations or data distortion.*

#### Available Curve Fitting Methods:

> ##### **1. Generalized Additive Models (GAM)**
[pyGAM Documentation](https://github.com/dswah/pyGAM)  
**Description**: A parameter-free spline fitting method. It can be problematic for data with “spiked behavior,” such as activity data.  


> ##### **2. Rolling Window Smoothing**
[Pandas Rolling Window](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.rolling.html)  
**Description**: A smoothing technique based on a moving average or rolling window method. The window size (which refers to the sample rate) can be adjusted manually.  
Available options include:

> - *Mean*: Calculates the mean over the data subset within the window.
> - *Triangular Weighted Mean*: Weights over the selected data are calculated using a triangular function.
> - *Gaussian Weighted Mean*: Weights over the selected data are calculated using a Gaussian function.  

> ##### **3. Univariate Spline Fitting**
[Scipy UnivariateSpline](https://docs.scipy.org/doc/scipy/reference/generated/scipy.interpolate.UnivariateSpline.html)  
**Description**:  A cubic spline fitting method with a smoothing factor.  
**Caution**: It’s essential to check all samples using this method because a certain smoothing factor that works well for one sample may not work for others.  
**Autofit option**: Automatically determines the optimal smoothing factor for each sample by performing a grid search to minimize the penalized sum of squares of the residuals.

> ##### **4. Savitzky-Golay Filter (Savgol)**
[Savitzky-Golay Filter (Wikipedia)](https://en.wikipedia.org/wiki/Savitzky%E2%80%93Golay_filter)  
**Description**: This method applies a Savitzky-Golay filter with a chosen window length (positive odd number) and polynomial order by convolution.  

> ##### **5. Single-Component Cosinor Analysis**
[CosinorPy GitHub](https://github.com/mmoskon/CosinorPy), [Cosinor Analysis (Research Paper)](https://doi.org/10.1186/s12859-020-03830-w)  
**Description**: A method for rhythmic data analysis, especially useful for periodic data.


---

## 3. Outlier Removal

Select **Remove Outlier** to apply a **standard outlier detection method** that identifies and removes extreme data points. This method detects values that deviate beyond a user-defined threshold of **standard deviations from the mean**. The threshold can be manually adjusted to fine-tune the sensitivity of the outlier detection, ensuring flexibility in data preprocessing.

After outlier detection and removal, linear interpolation is used to estimate the removed outlier values by averaging the nearest surrounding data points, ensuring the dataset remains smooth and accurate.


---
