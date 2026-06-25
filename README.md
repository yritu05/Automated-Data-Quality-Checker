# Automated-Data-Quality-Checker

This project provides an automated web-based tool to check and clean data quality in uploaded files using Python and Streamlit. It performs various checks such as missing values, duplicates, schema validation, and outlier detection, and offers cleaning options.

Features
File Upload: Upload CSV or Excel files for analysis.
Data Preview: View uploaded data in a table format.
Missing Values Check: Identifies columns with missing data.
Duplicates Check: Finds duplicate rows in the dataset.
Schema Validation: Compares actual columns against expected columns.
Outlier Detection: Detects outliers in numeric columns using IQR method.
Data Cleaning: Remove duplicates, fill missing values, remove outliers.
Download Cleaned Data: Export cleaned data as CSV.
Prerequisites
Python 3.x
Installation
Clone or download the project.
Install dependencies:
pip install -r requirements.txt
Usage
Run the Streamlit app:

streamlit run app.py
This will start the web application on http://localhost:8501

Upload a CSV or Excel file using the file uploader.

View data preview and quality analysis.

Use cleaning options to improve data quality.

Download the cleaned data.

Deployment
This app can be deployed on Streamlit Cloud or other platforms supporting Streamlit apps.

Configuration
The app automatically detects file types (CSV/Excel).
Schema validation allows custom expected columns.
Outlier detection works on selected numeric columns.
Cleaning options include various fill methods for missing values.
Dependencies
streamlit
pandas
sqlalchemy
psycopg2-binary
