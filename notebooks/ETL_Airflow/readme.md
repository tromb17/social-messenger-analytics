# Automated App Analytics Pipeline Using Airflow

## Project Overview

This repository contains an automated analytics pipeline built using Apache Airflow to retrieve, process, and visualize key metrics related to user activity in an application. The goal is to monitor critical KPIs (Key Performance Indicators) and deliver timely updates to stakeholders via Telegram notifications.

## Key Features

- **Automated ETL**: Scheduled extraction of data from a ClickHouse database.
- **Metrics Calculation**: Computation of crucial indicators such as DAU (Daily Active Users), average likes per user, CTR (Click-Through Rate), and more.
- **Visual Representation**: Creation of interactive graphs depicting weekly trends in user activity.
- **Notification System**: Delivery of daily reports to a Telegram channel using a dedicated bot.

## Architecture Breakdown

### Tasks

1. **Extract Feed Data**:
   - Retrieves relevant metrics (DAU, likes, views, etc.) from the `simulator_20250620.feed_actions` table for the past 31 days.

2. **Extract Message Data**:
   - Fetches analogous metrics specifically tied to messenger activities (DAU, sent messages, etc.).

3. **Send Report**:
   - Combines the above datasets to calculate relative changes over time and generates informative reports complete with visual aids.

### Core Libraries

- **Pandas**: For data manipulation and aggregation.
- **Matplotlib & Seaborn**: For creating high-quality graphical representations.
- **Telethon**: Enables communication with Telegram channels/bots.
- **Airflow**: Coordinates the entire workflow and ensures scheduled executions.

## Configuration Details

- **Connection Parameters**: Credentials for accessing the ClickHouse database are stored securely in environment variables.
- **Scheduling**: Reports are generated daily at 11 AM UTC.

## Usage Guide

To run this pipeline locally:

1. Install dependencies (Pandas, Matplotlib, Seaborn, Telethon, Airflow).
2. Configure credentials (bot token, chat IDs) appropriately.
3. Launch the Airflow scheduler and worker services.

## Example Outputs

Daily reports delivered to the Telegram channel look something like this:

![Report](/notebooks/ETL_Airflow/Report.jpg)
