import pandas as pd

from src.analyzer import analyze_dataframe


df = pd.read_csv("data/sample.csv")

print("Numeric columns:")
print(df.select_dtypes(include="number").columns.tolist())

analysis = analyze_dataframe(df)

print("\nDataset type:")
print(analysis.get("dataset_type"))

print("\nAnalysis keys:")
print(analysis.keys())

print("\nCorrelations:")
print(analysis.get("correlations"))

print("\nChurn Rate Extremes:")
print(
    analysis.get("business_metrics", {}).get(
        "churn_rate_extremes",
        {}
    )
)

print("\nKey Findings:")
for finding in analysis.get("key_findings", []):
    print(f"- {finding}")