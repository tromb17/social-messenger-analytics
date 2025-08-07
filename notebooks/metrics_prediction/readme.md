# User Activity Prediction

## Task Description

As user activity grows, so does the burden on our servers. Recently, we've been getting many complaints about application lags. While this seems like a task for DevOps engineers, your contribution is equally important—we need you to predict how user activity will evolve over the coming month.

## Metric Selection and Temporal Granularity

The primary metric selected for prediction is **Number of Views**. This choice reflects direct user interactions with content, thus influencing server loads. The temporal resolution is set to **daily**, offering adequate detail without introducing unnecessary noise.

Additional regressor variables are excluded from the model for simplicity and clarity.

## Dataset Overview

Historical data spans from early March 2025 through mid-July. There are 136 rows of daily observations covering user activity metrics including DAU (Daily Active Users), likes, views, and CTR (Click-Through Rate).

| Date       | DAU      | Likes | Views | CTR      |
|------------|----------|-------|-------|----------|
| 2025-03-01 | 878      | 1560  | 7603  | 0.205182 |
| 2025-03-02 | 2238     | 12816 | 62770 | 0.204174 |
| ...        | ...      | ...   | ...   | ...      |
| 2025-07-14 | 19017    | 131578| 633584| 0.207673 |

Variable Types:
- `date`: datetime64[ns]
- `DAU`, `likes`, `views`: uint64
- `ctr`: float64

Correlations reveal moderate positive relationships among all core metrics.

## Models

Two Dynamic Linear Trend (DLT) models were utilized:
1. **Linear Trend Model**
2. **Log-Linear Trend Model**

Training involves Markov Chain Monte Carlo (MCMC) simulations to stabilize estimates across multiple iterations.

## Quality Assessment

Models undergo rigorous evaluation via backtesting methodologies:
- Rolling Window
- Expanding Window

Evaluation metrics include:
- Mean Absolute Error (MAE)
- Mean Squared Error (MSE)
- Symmetric Mean Absolute Percentage Error (SMAPE)
- Weighted Mean Absolute Percent Error (WMAPE)

The second model (**Log-Linear Trend**) demonstrated superior performance across all key metrics.

## Interpretation of Results

The preferred model accurately predicts a gradual rise in user activity over the upcoming weeks. However, limitations should be noted:
- No seasonal adjustments incorporated
- External influences (marketing campaigns, holidays, etc.) unaccounted for

Therefore, ongoing server capacity planning and proactive monitoring remain essential.
