# Analytics

The Analytics module delivers a structured, end-to-end data science workflow on the Titanic passenger dataset. Starting from raw data profiling and progressing through cleaning, exploratory analysis, visual storytelling, classification modeling, imbalance handling, hyperparameter tuning, regression analysis, and model persistence, this module demonstrates the core competencies expected in a production-oriented analytics pipeline. Every result documented here is derived directly from the executed notebooks.

---

## Overview

The Analytics module is a component of the **Zepto Data & AI Platform**. It operates downstream of the Data Pipeline module, consuming the Titanic dataset and applying a complete analyst-to-data-scientist workflow. The module is implemented across two sequential Jupyter notebooks: the first performs data profiling, cleaning, and exploratory data analysis; the second builds, evaluates, and persists predictive models. Together, they form a reproducible analytical pipeline that transforms raw data into actionable predictions.

---

## Problem Statement

Given the Titanic passenger manifest, the objective is to profile and clean the dataset, extract meaningful patterns through exploratory analysis, and build classification models that predict passenger survival. A secondary regression task predicts passenger fare. The workflow evaluates multiple modeling strategies, addresses class imbalance, tunes hyperparameters, and persists the best-performing pipeline for downstream consumption.

---

## Workflow

| Stage | Description | Output |
|---|---|---|
| Dataset Loading | Load the Titanic dataset from Seaborn and persist as CSV | `titanic.csv` (raw) |
| Profiling | Examine shape, data types, summary statistics, and missing values | Profiling report in notebook |
| Cleaning | Apply threshold-based missing value strategy; drop, impute, or remove columns | Cleaned DataFrame |
| EDA — Univariate | Histogram, boxplot, IQR outlier detection for `age` and `fare` | Distribution insights, outlier counts |
| EDA — Bivariate | Survival rates by sex, class, sex × class; correlation matrix | Survival rate tables, correlation rankings |
| Storytelling | Five visualizations with written interpretations | Multivariate data narrative |
| Exploratory Standardization | Z-score validation on `age` and `fare` | Standardized mean ≈ 0, std ≈ 1 |
| Dataset Export | Save cleaned dataset for modeling notebook | `titanic.csv` (cleaned) |
| Preprocessing | Imputation, encoding, scaling via `ColumnTransformer` + `Pipeline` | Transformed feature matrices |
| Classification | Train Logistic Regression, Decision Tree, Random Forest | Three fitted pipelines |
| Evaluation | Accuracy, Precision, Recall, F1, AUC, confusion matrices, ROC curves | Comparison table |
| Imbalance Handling | Baseline vs. `class_weight='balanced'` vs. SMOTE | Imbalance comparison table |
| Hyperparameter Tuning | GridSearchCV on Random Forest (n_estimators, max_depth, max_features) | Best parameters, CV score, OOB score |
| Regression | Linear Regression predicting fare; MAE, RMSE, R², Adjusted R², residual plot | Regression evaluation table |
| Pipeline Saving | Serialize best pipeline with Joblib; reload and verify | `best_model.pkl` |

---

## Folder Structure

```
analytics/
├── 01_eda.ipynb        # Profiling, cleaning, and the data story
├── 02_modeling.ipynb    # Predictive modeling
├── titanic.csv          # Cleaned dataset produced by 01_eda.ipynb
├── best_model.pkl       # Best-performing pipeline
└── README.md
```

| File | Description |
|---|---|
| `01_eda.ipynb` | Loads the Titanic dataset, performs profiling, applies missing value handling, conducts univariate and bivariate analysis, builds a multivariate data story, and exports the cleaned dataset |
| `02_modeling.ipynb` | Consumes the cleaned CSV, builds a preprocessing pipeline, trains three classifiers, evaluates and compares models, handles class imbalance, tunes hyperparameters, runs a regression side-task, and saves the final pipeline |
| `titanic.csv` | The cleaned Titanic dataset (889 records after row removal) used as input by the modeling notebook |
| `best_model.pkl` | The serialized scikit-learn `Pipeline` containing both preprocessing steps and the tuned Random Forest classifier |

---

## Technology Stack

| Library | Purpose |
|---|---|
| `pandas` | Data loading, manipulation, aggregation, and tabular operations |
| `seaborn` | Statistical visualizations (histograms, boxplots, barplots, heatmaps, pairplots, scatterplots) |
| `matplotlib` | Base plotting framework and figure layout control |
| `scikit-learn` | Preprocessing pipelines, classification models, regression, evaluation metrics, hyperparameter tuning |
| `imbalanced-learn` | SMOTE oversampling to address class imbalance in the training set |
| `joblib` | Serialization and deserialization of the trained pipeline |

---

## Installation

```bash
# Clone the repository
git clone https://github.com/pothireddyvishnu/Zepto_Data_AI_Platform.git
cd Zepto_Data_AI_Platform

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate        # macOS / Linux
# .venv\Scripts\activate          # Windows

# Install dependencies
pip3 install -r requirements.txt

# Launch Jupyter
jupyter notebook
```

---

## Running the Module

Execute the notebooks in strict sequential order:

```
01_eda.ipynb  →  02_modeling.ipynb
```

1. **`01_eda.ipynb`** — Run all cells. This notebook loads the raw Titanic dataset from Seaborn, performs profiling and cleaning, conducts exploratory analysis, and saves the cleaned dataset as `titanic.csv`.

2. **`02_modeling.ipynb`** — Run all cells. This notebook reads `titanic.csv` produced by the first notebook, builds preprocessing pipelines, trains and evaluates classifiers, tunes hyperparameters, runs regression analysis, and saves the final model as `best_model.pkl`.

The second notebook depends on the cleaned CSV output of the first. Running them out of order will produce incorrect results.

---

# Exploratory Data Analysis

The EDA notebook (`01_eda.ipynb`) is organized into six analytical stages: dataset profiling, missing value handling, univariate analysis, bivariate analysis, multivariate storytelling, and exploratory standardization.

---

## Profiling

The dataset was loaded using `sns.load_dataset('titanic')` and profiled using standard pandas methods:

- **`df.shape`** — The dataset contains **891 records** and **15 columns**.
- **`df.info()`** — Identified column data types and non-null counts. Revealed that `age`, `embarked`, `deck`, and `embark_town` contain missing values.
- **`df.describe()`** — Generated summary statistics for all numerical columns, providing measures of central tendency, dispersion, and range.
- **Missing values** — Four columns contained missing data, with `deck` having the most severe missingness at 77.22%.

---

## Missing Value Handling

A threshold-based cleaning strategy was applied:

- **Under 5% missing** → Drop affected rows
- **5%–30% missing** → Impute
- **Over 30% missing** → Drop the column

| Column | Missing Count | Missing % | Strategy | Reason |
|---|---|---|---|---|
| `age` | 177 | 19.87% | Median imputation | Missing rate is between 5%–30%; median is robust to outliers in the age distribution |
| `embarked` | 2 | 0.22% | Drop affected rows | Minimal information loss; only 2 records affected |
| `embark_town` | 2 | 0.22% | Drop affected rows | Same records as `embarked`; co-occurring missingness |
| `deck` | 688 | 77.22% | Drop column | Over three-quarters missing; imputation would introduce significant bias |

After cleaning, the dataset retained **889 records** and **14 columns**.

---

## Univariate Analysis

Histograms and boxplots were generated for `age` and `fare`. The IQR method was used to quantify outliers.

### Age

| Metric | Value |
|---|---|
| Q1 | 22.0 |
| Q3 | 35.0 |
| IQR | 13.0 |
| Lower Bound | 2.5 |
| Upper Bound | 54.5 |
| Outliers Detected | **65** |

The age histogram shows a concentration of passengers in the 20–35 range, with the boxplot confirming outliers above 54.5 years. The large spike near the median (28.0) is partially attributable to median imputation of the 177 missing values.

### Fare

| Metric | Value |
|---|---|
| Q1 | 7.8958 |
| Q3 | 31.0 |
| IQR | 23.1042 |
| Lower Bound | −26.7605 |
| Upper Bound | 65.6563 |
| Outliers Detected | **114** |

The fare distribution is heavily right-skewed, with a long tail of high-fare passengers.

### Fare Central Tendency

| Measure | Value |
|---|---|
| Mean | 32.10 |
| Median | 14.45 |
| Mode | 8.05 |
| Skewness | **Right-Skewed** |

Since **Mean (32.10) > Median (14.45) > Mode (8.05)**, the fare distribution is right-skewed. A small number of passengers paid exceptionally high fares, pulling the mean upward while most passengers paid relatively low fares.

---

## Bivariate Analysis

### Survival Rate by Sex

| Sex | Survival Rate |
|---|---|
| Male | 18.89% |
| Female | 74.04% |

Female passengers survived at approximately four times the rate of male passengers, consistent with the historical "women and children first" evacuation protocol.

### Survival Rate by Passenger Class

| Class | Survival Rate |
|---|---|
| 1st | 62.62% |
| 2nd | 47.28% |
| 3rd | 24.24% |

First-class passengers had the highest survival rate, with a steep decline through second and third class. This suggests that socioeconomic status or cabin location influenced access to lifeboats.

### Survival Rate by Sex and Class

| Sex | Class | Survival Rate |
|---|---|---|
| Female | 1st | 96.74% |
| Female | 2nd | 92.11% |
| Female | 3rd | 50.00% |
| Male | 1st | 36.89% |
| Male | 2nd | 15.74% |
| Male | 3rd | 13.54% |

The interaction reveals that sex dominated class effects: first-class females survived at 96.74%, while even first-class males survived at only 36.89%. Third-class females had a 50% survival rate — higher than any male subgroup.

### Correlation Matrix

The correlation matrix was computed on six numerical variables: `survived`, `pclass`, `age`, `sibsp`, `parch`, and `fare`.

**Two strongest correlations:**

| Rank | Feature Pair | Correlation (r) |
|---|---|---|
| 1 | `pclass` & `fare` | −0.5482 |
| 2 | `sibsp` & `parch` | 0.4145 |

The negative correlation between `pclass` and `fare` reflects that higher-class passengers (lower `pclass` number) paid higher fares. The positive correlation between `sibsp` and `parch` indicates that passengers traveling with spouses/siblings also tended to travel with parents/children.

---

## Data Story

### Survival Rate by Sex (Bar Chart)

**Purpose:** Visualize the difference in survival probability between male and female passengers.

The bar chart shows a substantial difference in survival rates between male and female passengers. Female passengers had a significantly higher probability of surviving than male passengers, indicating that sex was one of the strongest factors influencing survival. This supports the historical observation that women were given priority during the evacuation.

### Survival Rate by Passenger Class (Bar Chart)

**Purpose:** Compare survival rates across the three ticket classes.

Survival rates varied considerably across passenger classes, with first-class passengers having the highest survival rate and third-class passengers the lowest. This suggests that socioeconomic status or cabin location may have influenced access to lifeboats and evacuation procedures. Passenger class was therefore another important factor associated with survival.

### Age vs. Fare by Survival (Scatter Plot)

**Purpose:** Examine the joint relationship between age, fare, and survival outcome.

The scatter plot indicates that passengers who paid higher fares were more frequently among the survivors, while those paying lower fares experienced a higher proportion of fatalities. Age alone does not show a clear separation between survivors and non-survivors, suggesting it had a weaker influence than fare. Since higher fares were generally associated with higher passenger classes, this visualization reinforces the relationship between passenger class and survival.

### Correlation Heatmap

**Purpose:** Summarize the linear relationships among the selected numerical variables.

The correlation heatmap summarizes the relationships among the selected numerical variables. Passenger class and fare exhibit the strongest negative correlation, reflecting that higher-class passengers generally paid higher fares. Survival shows a moderate positive relationship with fare and a negative relationship with passenger class, supporting the earlier findings that wealthier, higher-class passengers were more likely to survive.

### Pair Plot (survived, pclass, age, fare)

**Purpose:** Provide a comprehensive multivariate view of pairwise relationships colored by survival status.

The pair plot provides a comprehensive view of the relationships among `survived`, `pclass`, `age`, and `fare`. The visual patterns confirm that survivors are more concentrated among passengers with higher fares and lower passenger class numbers (first class), while age does not show a strong separation between the two groups. Overall, the pair plot reinforces the conclusions drawn from the previous visualizations and presents a cohesive multivariate perspective on the factors influencing survival.

---

## Feature Standardization

As an exploratory validation step, `age` and `fare` were standardized using the z-score formula:

```
z = (x − mean) / std
```

| Feature | Before Mean | Before Std | After Mean | After Std |
|---|---|---|---|---|
| `age` | 29.32 | 12.98 | ≈ 0.00 | 1.00 |
| `fare` | 32.10 | 49.70 | ≈ 0.00 | 1.00 |

This standardization was performed as an EDA sanity check to confirm that z-score transformation produces the expected zero-mean, unit-variance result. It is **not** used in the predictive modeling pipeline, which applies its own `StandardScaler` within the preprocessing `Pipeline`.

---

# Predictive Modeling

The modeling notebook (`02_modeling.ipynb`) builds a complete machine learning pipeline from the cleaned dataset, covering preprocessing, training, evaluation, imbalance handling, tuning, regression, and model persistence.

---

## Train/Test Split

The dataset was split into **80% training (711 samples)** and **20% testing (178 samples)** using `train_test_split` with `stratify=y`.

Stratified sampling was chosen because the target variable is imbalanced:

| Class | Count | Percentage |
|---|---|---|
| Not Survived (0) | 549 | 61.75% |
| Survived (1) | 340 | 38.25% |

Without stratification, the minority class (survivors) could be underrepresented in either split, leading to biased training or unreliable evaluation. Stratification preserves the 61.75%/38.25% ratio in both subsets.

---

## Preprocessing Pipeline

The preprocessing pipeline is constructed using scikit-learn's `ColumnTransformer` and `Pipeline` to ensure all transformations are applied consistently and without data leakage.

**Numerical features** (`pclass`, `age`, `sibsp`, `parch`, `fare`):
1. `SimpleImputer(strategy="median")` — fills remaining missing values with the column median
2. `StandardScaler()` — standardizes features to zero mean and unit variance

**Categorical features** (`sex`, `embarked`):
1. `SimpleImputer(strategy="most_frequent")` — fills missing values with the mode
2. `OneHotEncoder(handle_unknown="ignore")` — converts categories to binary indicator columns

The `ColumnTransformer` combines both sub-pipelines, producing a transformed feature matrix of shape **(711, 10)** for training and **(178, 10)** for testing.

**Why Pipeline prevents data leakage:** The `Pipeline` object ensures that `fit_transform()` is called only on the training data. The test data is transformed using `transform()` with parameters learned exclusively from the training set. This prevents test-set statistics (means, standard deviations, category mappings) from influencing the training process.

---

## Models Trained

| Model | Purpose | Advantages |
|---|---|---|
| Logistic Regression | Linear baseline classifier | Interpretable coefficients; fast training; provides calibrated probability estimates |
| Decision Tree | Non-linear, rule-based classifier | Visually interpretable; captures non-linear boundaries; no feature scaling required |
| Random Forest | Ensemble of decision trees | Reduces overfitting through bagging; robust to noise; provides out-of-bag estimation |

These three models represent a deliberate progression from a simple linear baseline to an ensemble method, enabling a meaningful comparison of model complexity versus predictive performance.

---

## Decision Tree Visualization

The decision tree was visualized using `plot_tree()` with feature names extracted from the preprocessing pipeline and class labels `["Not Survived", "Survived"]`. The tree displays the learned splitting rules at each node, showing the feature, threshold, Gini impurity, sample count, and class distribution. This visualization makes the model fully interpretable and reveals which features (e.g., sex, class, fare) the tree prioritized for partitioning.

---

## Model Evaluation

### Logistic Regression

- **Confusion Matrix:** Correctly classified the majority of non-survivors, with moderate recall on the survivor class.
- **Accuracy: 0.8090** — Correctly classified 80.90% of test passengers.
- **Precision: 0.7833** — Of predicted survivors, 78.33% actually survived.
- **Recall: 0.6912** — Identified 69.12% of actual survivors.
- **F1 Score: 0.7344** — Harmonic mean reflects the trade-off between precision and recall.
- **AUC: 0.8610** — Strong discriminatory ability; the model ranks survivors above non-survivors 86.10% of the time.

### Decision Tree

- **Confusion Matrix:** Higher recall than Logistic Regression but more false positives.
- **Accuracy: 0.7697** — Lowest accuracy among the three classifiers.
- **Precision: 0.6901** — More false positives compared to the other models.
- **Recall: 0.7206** — Captured a larger share of actual survivors than Logistic Regression.
- **F1 Score: 0.7050** — Balanced metric reflects the precision drop.
- **AUC: 0.7541** — Weakest ranking performance, indicating limited generalization.

### Random Forest

- **Confusion Matrix:** Best overall balance between true positives and false positives.
- **Accuracy: 0.8202** — Highest accuracy among all classifiers.
- **Precision: 0.7812** — Comparable to Logistic Regression; few false positives.
- **Recall: 0.7353** — Better than Logistic Regression at identifying actual survivors.
- **F1 Score: 0.7576** — Best F1 among the three models.
- **AUC: 0.8184** — Strong ranking performance, though slightly below Logistic Regression's AUC.

---

## Classification Model Comparison

| Model | Accuracy | Precision | Recall | F1 Score | ROC-AUC |
|---|---|---|---|---|---|
| Logistic Regression | 0.8090 | 0.7833 | 0.6912 | 0.7344 | 0.8610 |
| Decision Tree | 0.7697 | 0.6901 | 0.7206 | 0.7050 | 0.7541 |
| Random Forest | **0.8202** | **0.7812** | **0.7353** | **0.7576** | 0.8184 |

Random Forest achieved the highest Accuracy, F1 Score, and Recall while maintaining precision comparable to Logistic Regression. Although Logistic Regression had the highest AUC (0.8610 vs. 0.8184), Random Forest provided a better balance across all classification metrics and was selected as the strongest baseline model for further optimization.

---

## Imbalance Handling

Three strategies were compared using Logistic Regression as the base classifier:

| Strategy | Precision | Recall | F1 Score |
|---|---|---|---|
| Baseline | 0.7833 | 0.6912 | 0.7344 |
| `class_weight='balanced'` | 0.7183 | 0.7500 | 0.7338 |
| SMOTE | 0.7353 | 0.7353 | 0.7353 |

**Observations:**

- **Class weighting** improved recall from 0.6912 to 0.7500 by penalizing misclassification of the minority class, but at the cost of reduced precision (0.7833 → 0.7183). The F1 score remained nearly identical (0.7338 vs. 0.7344).
- **SMOTE** produced balanced precision and recall (both 0.7353), with a marginal F1 improvement over the baseline (0.7353 vs. 0.7344).
- Neither technique produced a meaningful improvement in F1 over the baseline, suggesting that the 61.75%/38.25% class distribution is not severely imbalanced enough to warrant resampling for this dataset.

---

## Hyperparameter Tuning

The Random Forest classifier was optimized using **GridSearchCV** with 5-fold cross-validation, scored on F1.

**Parameter Grid:**

| Parameter | Values Searched |
|---|---|
| `n_estimators` | 100, 200, 300 |
| `max_depth` | None, 5, 10, 20 |
| `max_features` | `sqrt`, `log2` |

**Results:**

| Metric | Value |
|---|---|
| Best `n_estimators` | 200 |
| Best `max_depth` | None |
| Best `max_features` | `sqrt` |
| Best Cross-Validation F1 | 0.7434 |
| OOB Score | 0.8073 |

**Tuned Random Forest Test Metrics:**

| Metric | Value |
|---|---|
| Accuracy | 0.8090 |
| Precision | 0.7656 |
| Recall | 0.7206 |
| F1 Score | 0.7424 |
| AUC | 0.8211 |

The tuned model did not outperform the default Random Forest on the test set (F1: 0.7424 vs. 0.7576). The optimal configuration retained `max_depth=None` (fully grown trees) and used 200 estimators with `sqrt` features per split. The OOB score of 0.8073 provides an independent generalization estimate consistent with test accuracy.

---

## Regression Analysis

A multivariate **Linear Regression** model was developed to predict passenger **fare** using the remaining features.

**Target:** `fare`
**Features:** `pclass`, `age`, `sibsp`, `parch` (numerical); `sex`, `embarked` (categorical)

The regression pipeline applied the same preprocessing pattern: median imputation + standard scaling for numerical features, constant imputation + one-hot encoding for categorical features.

### Residual Plot

The residual plot displays predicted fare values on the x-axis and residuals (actual − predicted) on the y-axis. The residuals exhibit a non-random, fan-shaped spread that widens as predicted values increase. This pattern confirms the presence of **heteroscedasticity** — the variance of prediction errors is not constant across the range of predicted fares. The model underestimates high fares and produces larger errors for expensive tickets.

---

## Regression Model Summary

| Metric | Value |
|---|---|
| MAE | 21.1386 |
| RMSE | 41.7465 |
| R² | 0.3468 |
| Adjusted R² | 0.3118 |

The R² of 0.3468 indicates that the model explains approximately 34.7% of the variance in fare. The Adjusted R² (0.3118) accounts for the number of predictors and shows modest explanatory power. The gap between MAE (21.14) and RMSE (41.75) is large, confirming that a subset of predictions have very large errors — consistent with the heteroscedastic residual pattern observed for high-fare passengers.

---

## Model Persistence

The best-performing pipeline was serialized using `joblib.dump()` and saved as `best_model.pkl`.

```python
joblib.dump(best_model, 'best_model.pkl')
```

The saved pipeline was reloaded and verified:

```python
load_model = joblib.load('best_model.pkl')
predictions = load_model.predict(X_test)
accuracy = accuracy_score(y_test, predictions)
# Accuracy: 0.8090
```

The reloaded model produced an accuracy of **0.8090** on the test set, confirming that the serialized pipeline is intact and functional.

**Why save the entire pipeline:** Saving only the estimator would require manually reproducing the preprocessing steps (imputation, encoding, scaling) at inference time. Saving the complete `Pipeline` object ensures that raw, unprocessed data can be passed directly to `predict()`, with all transformations applied automatically. This eliminates preprocessing mismatches between training and inference and makes the model deployment-ready.

---

## Final Recommendation

The **Random Forest Classifier** is the recommended model for deployment. It achieved the highest test accuracy (0.8202) and F1 score (0.7576) among the three classifiers, demonstrating the best balance between precision (0.7812) and recall (0.7353). While Logistic Regression produced a higher AUC (0.8610 vs. 0.8184), its lower recall (0.6912) means it misses a larger proportion of actual survivors — an operationally significant shortcoming. The hyperparameter-tuned Random Forest did not improve upon the default configuration on the held-out test set (F1: 0.7424 vs. 0.7576), suggesting that the default hyperparameters already provide near-optimal generalization for this dataset. Accordingly, the default Random Forest pipeline is the preferred choice for production deployment.

---

## Learning Outcomes

This module demonstrates the following concepts through hands-on implementation:

- **Data Profiling** — using `shape`, `info()`, `describe()`, and missing value analysis to assess dataset quality
- **Threshold-Based Cleaning** — applying rule-driven strategies (drop rows, impute, drop column) based on missingness severity
- **Univariate Analysis** — using histograms, boxplots, and IQR-based outlier detection to characterize individual feature distributions
- **Bivariate Analysis** — computing group-level survival rates with boolean masking and quantifying linear relationships with correlation matrices
- **Visual Storytelling** — constructing a multivariate narrative through sequenced visualizations with written interpretations
- **Preprocessing Pipelines** — building leakage-free transformation workflows using `ColumnTransformer` and `Pipeline`
- **Classification Modeling** — training and comparing Logistic Regression, Decision Tree, and Random Forest on the same split
- **Model Evaluation** — interpreting confusion matrices, precision–recall trade-offs, F1 scores, and ROC-AUC curves
- **Class Imbalance Handling** — comparing baseline, class weighting, and SMOTE strategies
- **Hyperparameter Tuning** — using GridSearchCV with cross-validation to search parameter spaces systematically
- **Regression Analysis** — building a Linear Regression model, computing MAE/RMSE/R²/Adjusted R², and diagnosing heteroscedasticity from residual plots
- **Model Persistence** — serializing and reloading complete pipelines with Joblib for deployment readiness
