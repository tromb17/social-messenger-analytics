# A/B Test Analysis

This repository contains a Jupyter Notebook analyzing the results of an A/B test conducted on a social media platform's post recommendation algorithm.

## Overview

The A/B test was conducted from March 28, 2025 to April 3, 2025, comparing two groups:
- **Group 1**: Control group (existing recommendation algorithm)
- **Group 2**: Test group (new recommendation algorithm)

The primary hypothesis was that the new algorithm in Group 2 would lead to an increase in CTR (Click-Through Rate).

## Notebook Contents

The analysis includes:

1. **Data Loading**: Connection to ClickHouse database and data extraction
2. **Exploratory Analysis**: 
   - Basic statistics and group sizes
   - CTR distribution visualization
3. **Statistical Testing**:
   - T-test comparison of CTR between groups
   - Mann-Whitney U test (non-parametric alternative)
4. **Smoothed CTR Calculation**: Adjusted CTR metric to handle variability
5. **Key Findings**: Interpretation of test results

## Key Findings

- The CTR distribution differs between groups (Group 1 appears normal while Group 2 is bimodal)
- The t-test showed no significant difference (p=0.685)
- The Mann-Whitney test indicated statistically significant differences (p=4.63e-45)
- Recommendation: The non-parametric test may be more appropriate given the non-normal distribution in Group 2

## Technical Details

**Libraries Used**:
- Pandas (via pandahouse for ClickHouse connection)
- Seaborn/Matplotlib for visualization
- SciPy for statistical tests
- NumPy for numerical operations

**Database Connection**:  
Configured to connect to ClickHouse using provided credentials.
