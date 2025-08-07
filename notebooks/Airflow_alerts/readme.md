# Real-time Alerting System Using Airflow

## Overview

This directory houses an automated system designed to continuously monitor user activity metrics in real-time. By leveraging Apache Airflow, the system extracts data from a ClickHouse database every 15 minutes and compares current values with those from the same interval exactly 24 hours prior. If there is a significant deviation exceeding a predefined threshold, alerts are automatically dispatched to a designated Telegram channel.

## Key Functionalities

### Monitoring Metrics

- **Feed Actions**: Number of unique users interacting with feeds, total likes, total views, and CTR (Click-Through Rate).
- **Messaging Actions**: Total messages sent and unique users sending messages.

### Threshold-Based Alerting

When the percentage change exceeds ±50%, the system triggers an alert:
- A Telegram message detailing the specific metric, its current and previous-day values, and the percent change.
- An accompanying graph highlighting the variation in the metric over the two compared intervals.

## Technical Stack

- **Python**: Main programming language for logic implementation.
- **Pandas**: For efficient data manipulation and calculations.
- **Matplotlib & Seaborn**: To render comparative visualizations.
- **Apache Airflow**: Orchestrates periodic executions and manages dependencies.
- **Telegram Bot API**: Sends notifications and attachments to the Telegram channel.

## How It Works

1. **Data Extraction**: Queries are executed against the ClickHouse database using pre-defined SQL statements to pull the latest metrics.
2. **Comparison Logic**: Current values are contrasted with historic ones from precisely 24 hours earlier.
3. **Alert Generation**: When thresholds are breached, alerts are triggered and dispatched.

## Customization Options

- Adjust the frequency of checks by modifying the cron expression (`schedule_interval`).
- Modify the acceptable deviation threshold (`threshold_pct`) depending on business requirements.
- Enhance security by storing sensitive tokens (e.g., Telegram bot token) externally rather than hardcoding them.

## Getting Started

To deploy this solution locally:

1. Install required packages (Pandas, Requests, Telegram, Matplotlib, Seaborn, PyTZ, Airflow).
2. Set up appropriate configurations (database access details, Telegram bot credentials).
3. Execute the DAG through the Airflow UI or CLI.

## Conclusion

This system offers a flexible framework for tracking key application metrics in real-time, ensuring swift responses to abnormal fluctuations. It enhances operational efficiency by automating otherwise manual oversight tasks.

## Example Outputs

Alerts delivered to the Telegram channel look something like this:

![Alert](/notebooks/Airflow_alerts/Example_alert.jpg)
