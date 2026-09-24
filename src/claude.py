import json
import os

from dotenv import load_dotenv
from anthropic import Anthropic


load_dotenv()


client = Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY")
)


SYSTEM_PROMPT = """
You are a careful business data analyst.

Analyze the statistical profile provided by the application.

Rules:
- Use only facts supported by the provided data.
- Do not invent numbers or relationships.
- Use business metrics calculated by the application when they are relevant.
- Do not perform important calculations yourself when the required metric is already provided.
- Do not claim causation unless the data supports it.
- Clearly distinguish correlation from causation.
- Clearly mention important data-quality issues.
- Keep the analysis concise and useful for a business user.

Return exactly these sections:

## Executive Summary
Give 3-4 concise bullet points with the most important findings.

## Key Findings
Give 5 concise findings.
Include relevant numbers when available.

## Data Quality
Mention only the most important data-quality issues.

## Suggested Visualizations
Suggest 3 useful charts and explain what each would help investigate.

## Business Questions
Give 3 useful questions that could be investigated next.

Do not write a long report.
Do not repeat the dataset description unnecessarily.
"""


def build_compact_profile(analysis: dict) -> dict:
    """
    Select the most useful analytical results before
    sending them to the language model.
    """

    profile = {
        "dataset_overview": {
            "rows": analysis.get("rows"),
            "columns": analysis.get("columns"),
            "duplicate_rows": analysis.get(
                "duplicate_rows"
            ),
        },
        "data_quality": {
            "missing_values": analysis.get(
                "missing_values",
                {}
            ),
            "data_types": analysis.get(
                "data_types",
                {}
            ),
        },
        "numeric_summary": analysis.get(
            "numeric_summary",
            {}
        ),
        "correlations": analysis.get(
            "correlations",
            {}
        ),
        "business_metrics": analysis.get(
            "business_metrics",
            {}
        ),
    }

    return profile


def generate_insights(analysis: dict) -> str:
    compact_profile = build_compact_profile(
        analysis
    )

    prompt = f"""
Here is the statistical profile of a dataset:

{json.dumps(
    compact_profile,
    indent=2,
    default=str
)}

Analyze this dataset according to your instructions.
"""

    message = client.messages.create(
        model="claude-opus-5",
        max_tokens=1800,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )

    text_blocks = [
        block.text
        for block in message.content
        if block.type == "text"
    ]

    return "\n".join(text_blocks)