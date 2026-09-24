import json
import pandas as pd

from src.analyzer import analyze_dataframe
from src.claude import build_compact_profile


df = pd.read_csv("data/sample.csv")

analysis = analyze_dataframe(df)

profile = build_compact_profile(analysis)

prompt = json.dumps(
    profile,
    indent=2,
    default=str,
)

print("Prompt characters:", len(prompt))
print("Approximate tokens:", len(prompt) // 4)