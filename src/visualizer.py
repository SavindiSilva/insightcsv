import pandas as pd
import plotly.express as px


def churn_rate_by_column(
    df: pd.DataFrame,
    column: str,
):
    if "Churn Label" not in df.columns:
        return None

    if column not in df.columns:
        return None

    churn_rates = (
        df.groupby(column)["Churn Label"]
        .apply(lambda x: x.eq("Yes").mean() * 100)
        .reset_index(name="Churn Rate")
    )

    churn_rates["Churn Rate"] = churn_rates[
        "Churn Rate"
    ].round(2)

    fig = px.bar(
        churn_rates,
        x=column,
        y="Churn Rate",
        title=f"Churn Rate by {column}",
        labels={
            "Churn Rate": "Churn Rate (%)",
        },
    )

    return fig


def correlation_heatmap(
    correlation_df: pd.DataFrame,
):
    if correlation_df.empty:
        return None

    fig = px.imshow(
        correlation_df,
        text_auto=True,
        aspect="auto",
        title="Correlation Heatmap",
        labels={
            "color": "Correlation",
        },
        zmin=-1,
        zmax=1,
    )

    return fig


def churn_rate_by_tenure(
    df: pd.DataFrame,
):
    if "Churn Label" not in df.columns:
        return None

    if "Tenure Months" not in df.columns:
        return None

    bins = [
        -1,
        12,
        24,
        48,
        60,
        float("inf"),
    ]

    labels = [
        "0–12 months",
        "13–24 months",
        "25–48 months",
        "49–60 months",
        "61+ months",
    ]

    tenure_groups = pd.cut(
        df["Tenure Months"],
        bins=bins,
        labels=labels,
    )

    churn_rates = (
        df.assign(
            **{"Tenure Group": tenure_groups}
        )
        .groupby(
            "Tenure Group",
            observed=False,
        )["Churn Label"]
        .apply(
            lambda x: x.eq("Yes").mean() * 100
        )
        .reset_index(name="Churn Rate")
    )

    churn_rates["Churn Rate"] = (
        churn_rates["Churn Rate"]
        .round(2)
    )

    fig = px.bar(
        churn_rates,
        x="Tenure Group",
        y="Churn Rate",
        title="Churn Rate by Customer Tenure",
        labels={
            "Churn Rate": "Churn Rate (%)",
            "Tenure Group": "Customer Tenure",
        },
    )

    return fig