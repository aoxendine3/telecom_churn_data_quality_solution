"""
Telecom Customer Churn & Data Quality Solution — Automated Data Quality Cleaner
Scans, repairs, deduplicates, and normalizes raw customer profiles and usage logs.
"""

import pandas as pd
import numpy as np
from typing import Tuple

class TelecomDataCleaner:
    def __init__(self):
        pass

    def clean_customer_info(self, cust_df: pd.DataFrame) -> pd.DataFrame:
        """Deduplicates customer records, imputes missing ages, and repairs negative charges."""
        df = cust_df.copy()
        
        # 1. Deduplicate CustomerID
        df = df.drop_duplicates(subset=['CustomerID'], keep='first').copy()
        
        # 2. Repair negative MonthlyCharges anomalies
        df['MonthlyCharges_clean'] = df['MonthlyCharges'].apply(lambda x: abs(x) if x < 0 else x)
        df['MonthlyCharges_is_negative'] = (df['MonthlyCharges'] < 0).astype(int)
        
        # 3. Missing Age Flag & Median Imputation
        df['Age_is_missing'] = df['Age'].isnull().astype(int)
        median_age = df['Age'].median()
        df['Age_clean'] = df['Age'].fillna(median_age)
        
        # 4. Date Feature Extraction
        df['SignupDate'] = pd.to_datetime(df['SignupDate'])
        df['SignupYear'] = df['SignupDate'].dt.year
        df['SignupMonth'] = df['SignupDate'].dt.month
        df['TenureDays'] = (pd.to_datetime('2023-12-31') - df['SignupDate']).dt.days
        
        return df

    def extract_usage_features(self, usage_df: pd.DataFrame) -> pd.DataFrame:
        """Extracts monthly time-series aggregations and trend signals from usage data."""
        df = usage_df.copy()
        df['Month'] = pd.to_datetime(df['Month'])
        df = df.sort_values(['CustomerID', 'Month'])

        # Aggregate full 12 months stats
        agg_df = df.groupby('CustomerID').agg(
            call_mins_mean=('CallMinutes', 'mean'),
            call_mins_std=('CallMinutes', 'std'),
            call_mins_sum=('CallMinutes', 'sum'),
            call_mins_max=('CallMinutes', 'max'),
            
            data_gb_mean=('DataUsageGB', 'mean'),
            data_gb_std=('DataUsageGB', 'std'),
            data_gb_sum=('DataUsageGB', 'sum'),
            data_gb_max=('DataUsageGB', 'max'),
            
            sms_mean=('SMSCount', 'mean'),
            sms_sum=('SMSCount', 'sum'),
            
            complaints_sum=('Complaints', 'sum'),
            complaints_max=('Complaints', 'max'),
            complaints_mean=('Complaints', 'mean')
        ).reset_index()

        # Recent 3-month vs First 3-month trend ratios
        u_first3 = df[df['Month'] <= '2023-03-31'].groupby('CustomerID').agg(
            call_first3=('CallMinutes', 'mean'),
            data_first3=('DataUsageGB', 'mean')
        ).reset_index()

        u_last3 = df[df['Month'] >= '2023-10-31'].groupby('CustomerID').agg(
            call_last3=('CallMinutes', 'mean'),
            data_last3=('DataUsageGB', 'mean')
        ).reset_index()

        trends = pd.merge(u_first3, u_last3, on='CustomerID', how='outer')
        trends['call_trend_ratio'] = trends['call_last3'] / (trends['call_first3'] + 1e-5)
        trends['data_trend_ratio'] = trends['data_last3'] / (trends['data_first3'] + 1e-5)

        return pd.merge(agg_df, trends, on='CustomerID', how='left')
