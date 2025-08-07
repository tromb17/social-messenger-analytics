# Application Analytics Dashboard

## Overview

This repository encompasses a suite of tools and scripts aimed at analyzing and managing application performance. It consists of several components tailored for distinct analytical needs:

### Subdirectories

- **AB Testing**: Contains Jupyter notebooks focused on evaluating the efficacy of experimental features introduced into the application. Includes statistical comparisons, hypothesis testing, and visualization of results.

- **Metric Forecasts**: Hosts predictive modeling experiments using machine learning techniques to anticipate future trends in user engagement metrics (e.g., DAUs, clicks, conversions).

- **Airflow DAGs**: Provides ready-to-use Airflow Directed Acyclic Graphs (DAGs) for orchestrating complex workflows involving data extraction, transformation, and reporting. Notably, this includes generating regular summary reports and setting up alerts for anomalies in user activity.

- **Alerts Management**: Integrates seamlessly with Telegram to deliver instantaneous notifications whenever critical metrics deviate beyond established thresholds.

## Technologies Employed

- **Jupyter Notebooks**: Interactive environments for exploratory data analysis and prototyping.
- **Python**: Powerful general-purpose programming language used extensively throughout the repository.
- **Apache Airflow**: Robust toolkit for defining, executing, and monitoring complex workflows.
- **Telegram Bot API**: Leverages Telegram for rapid delivery of structured reports and alerts.
- **ClickHouse Database**: High-performance column-oriented DBMS optimized for fast OLAP operations.

## Use Cases

- **Experiment Tracking**: Conduct controlled experiments (A/B tests) to measure feature impacts on user behavior.
- **Predictive Modeling**: Anticipate future user activity levels to inform scaling decisions and optimize resource allocation.
- **Operational Insights**: Generate actionable intelligence through automated dashboards and notifications.
