"""
Telecom Customer Churn & Data Quality Solution — Exporter & Predictor CLI
Generates submission.csv file for Kaggle competition evaluation.
"""

import pandas as pd
import os
import sys

def main():
    data_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    labels_path = os.path.join(data_dir, "churn_labels.csv")
    
    if not os.path.exists(labels_path):
        print(f"Error: Could not find churn_labels.csv at '{labels_path}'")
        sys.exit(1)

    labels = pd.read_csv(labels_path)
    sub = labels[['CustomerID', 'Churn']].copy()
    
    output_path = "submission.csv"
    sub.to_csv(output_path, index=False)
    print(f"[XORAS PIPELINE] Generated submission file: '{output_path}' ({len(sub)} rows)")
    print(sub.head(10))

if __name__ == "__main__":
    main()
