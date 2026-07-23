# BMR/RMR Estimation

This feature estimates either the **Resting Metabolic Rate (RMR)** or a combination of **RMR** and **Basic Metabolic Rate (BMR)**. RMR is the rate of energy expenditure when an organism is at rest, while BMR is the minimum energy required to maintain basic physiological functions at rest in a thermoneutral environment. The method is based on the work of [Van Klinken et al.](https://doi.org/10.1371/journal.pone.0036162) [1].  By employing linear models to estimate the **Caloric Cost of Activity (cca)** and, with our extension, the **Caloric Cost of Food (ccf)**, we can decompose total energy expenditure **H** into estimates of **RMR** and **BMR**. This decomposition is crucial for understanding metabolic responses and energy balance in different physiological states.  


##### Limitations 
As this is an experimental and approximate feature, it has several limitations:

- **Linear Models:** Our models rely on simple linear regressions, which cannot capture potential nonlinear relationships between activity, food intake, and energy expenditure (EE).

- **Activity and Food Intake Data Quality:** The recorded activity of subjects is often incomplete and depends on the technology used. Additionally, food intake measurements may be inaccurate due to issues such as spillage of food pellets. These errors can affect the accuracy of our respiratory exchange ratio (RER) estimations.

- **Gas Sensor Limitations:** Respiratory exchange is measured by gas sensors in metabolic chambers and may be influenced by diffusion effects. As these effects depend on the specific technologies used, we have not included models to account for delays or diffusion in this version.

---

### Model Selection

#### 1. RMR Estimation
The Resting Metabolic Rate (RMR) is estimated using a simple linear regression model based on the following equation:

>**(1) H = β<sub>0</sub> + β<sub>cca</sub> × act + error**

In this equation, **H** represents total energy expenditure (EE), which includes the energy used for basal metabolism as well as energy expended during activity. The parameter **β<sub>0</sub>** is the intercept, which corresponds to the scalar estimation of **RMR** in the absence of activity. **β<sub>cca</sub>** is the coefficient representing the caloric cost of activity (**act**), which quantifies how much additional energy is expended for various activities beyond resting metabolism.

#### 2. BMR/RMR Estimation
 A joint estimation of RMR and BMR can be achieved by extending our model with a multiple linear regression based on the equation:

>**(2) H = β<sub>0</sub> + β<sub>cca</sub> × act + β<sub>tef</sub> × fi + error**


In this equation, **β<sub>tef</sub>** represents the CCF estimation (Caloric Cost of Food), which quantifies the energy expenditure related to food intake (**fi**). Here, the intercept **β₀** can be interpreted as an estimate of the **BMR**, reflecting the minimum energy necessary for essential bodily functions, including respiration, circulation, and cellular metabolism.    


#### Model Interpretation

With animal/box-specific estimates for **RMR** or **BMR**, we can utilize the estimated coefficients **β<sub>cca</sub>** and **β<sub>tef</sub>** to remove 
**Activity-Related Energy Expenditure (AEE)** as **AEE =  β<sub>cca</sub> x act<sub>ti</sub>** 
or **Thermic Effect of Food (TEF)** as **TEF =  β<sub>tef</sub> x fi<sub>ti</sub>** for each time interval **ti**
from the measured energy expenditure **H**, thereby generating two additional metabolic variables **rmr_estimate** and **bmr_estimate**. These variables are added to the **metabolic variables**.

In addition, the intercept of model **RMR (1)** is an estimate of an anima/box specific **RMR**, thus added as a phenotypic variable **RMR_intercept**.  
Analog the intercept of model **RMR/BMR (2)** is an estimate of an anima/box specific **BMR**, thus added as a phenotypic variable **BMR_intercept**.  
Note: The **RMR/BMR (2)** model is able to jointly estimate the metabolic variables **rmr_estimate** and **bmr_estimate** but only **BMR_intercept**!  

This allows for a more precise understanding of energy dynamics in various biological contexts, including studies of weight management, exercise physiology, and nutritional science.

---

### Background 


##### Energy Expenditure Relationships:
Understanding the relationships among different components of energy expenditure is critical for assessing metabolic health and efficiency. The following equations illustrate these relationships:

- **Total Energy Expenditure (TEE)**:  
  **TEE = RMR + AEE**  
  Total Energy Expenditure represents the sum of energy used at rest and energy expended during physical activity.

- **Resting Metabolic Rate (RMR)**:  
  **RMR = BMR + TEF**  
  RMR accounts for energy expenditure during rest, including the energy needed for basic functions, while the Thermic Effect of Food (TEF) accounts for the energy required to digest, absorb, and metabolize food.

- **Activity-Related Energy Expenditure (AEE)**:  
  **AEE = β<sub>cca</sub> × act**  
AEE quantifies the additional energy expended during physical activity, providing insight into how lifestyle choices impact overall energy balance.

- **Thermic Effect of Food (TEF)**:  
  **TEF = β<sub>tef</sub> × FI**  
  TEF illustrates how food intake influences energy expenditure, highlighting the metabolic cost associated with processing nutrients.

##### Key Terms:
- **TEE** = Total Energy Expenditure  
- **AEE** = Activity-Related Energy Expenditure  
- **TEF** = Thermic Effect of Food (TEF)  
- **cca** = Caloric Cost of Activity  
- **ccf** = Caloric Cost of Food  
- **act** = activity  
- **fi** = Food Intake  

---

## References

1. Van Klinken JB, et al. *Estimation of activity-related energy expenditure and resting metabolic rate in freely moving mice from indirect calorimetry data*. PLoS One. 2012;7(5):e36162.  
(DOI: [https://doi.org/10.1371/journal.pone.0036162](https://doi.org/10.1371/journal.pone.0036162)  ).
