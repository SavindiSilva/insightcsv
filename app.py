import json

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from src.analyzer import analyze_dataframe
from src.claude import generate_insights
from src.visualizer import (
    churn_rate_by_column,
    correlation_heatmap,
    churn_rate_by_tenure,
)


load_dotenv()


st.set_page_config(
    page_title="InsightCSV",
    page_icon="📊",
    layout="wide",
)


st.title("📊 InsightCSV")
st.subheader("AI-Powered CSV Data Analyst")

st.write(
    "Upload a CSV file and get a statistical overview, "
    "data-quality checks, visual analysis, and "
    "AI-generated business insights."
)


uploaded_file = st.file_uploader(
    "Upload your CSV file",
    type=["csv"],
)


if uploaded_file is not None:
    try:
        # --------------------------------------------------
        # Load dataset
        # --------------------------------------------------

        df = pd.read_csv(uploaded_file)

        st.success(
            f"Successfully loaded {uploaded_file.name}"
        )

        # --------------------------------------------------
        # Run analysis
        # --------------------------------------------------

        analysis = analyze_dataframe(df)

        dataset_type = analysis.get(
            "dataset_type",
            "generic",
        )

        # --------------------------------------------------
        # Dataset Overview
        # --------------------------------------------------

        st.subheader("Dataset Overview")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Rows",
                len(df),
            )

        with col2:
            st.metric(
                "Columns",
                len(df.columns),
            )

        with col3:
            st.metric(
                "Duplicate Rows",
                int(
                    analysis.get(
                        "duplicate_rows",
                        0,
                    )
                ),
            )

        # --------------------------------------------------
        # Preview
        # --------------------------------------------------

        st.subheader("Preview")

        st.dataframe(
            df.head(10),
            width="stretch",
        )

        # --------------------------------------------------
        # Data Types
        # --------------------------------------------------

        st.subheader("Data Types")

        data_types = analysis.get(
            "data_types",
            {},
        )

        dtype_df = pd.DataFrame(
            {
                "Column": list(data_types.keys()),
                "Data Type": list(data_types.values()),
            }
        )

        st.dataframe(
            dtype_df,
            width="stretch",
        )

        # --------------------------------------------------
        # Data Quality Analysis
        # --------------------------------------------------

        st.subheader("🔎 Data Quality Analysis")

        data_quality = analysis.get(
            "data_quality",
            {},
        )

        missing_values = data_quality.get(
            "missing_values",
            {},
        )

        duplicate_rows = data_quality.get(
            "duplicate_rows",
            0,
        )

        low_information_columns = data_quality.get(
            "low_information_columns",
            [],
        )

        potential_numeric_columns = (
            data_quality.get(
                "potential_numeric_columns",
                [],
            )
        )

        quality_col1, quality_col2, quality_col3 = (
            st.columns(3)
        )

        with quality_col1:
            st.metric(
                "Columns with Missing Data",
                len(missing_values),
            )

        with quality_col2:
            st.metric(
                "Duplicate Rows",
                duplicate_rows,
            )

        with quality_col3:
            st.metric(
                "Low-Information Columns",
                len(low_information_columns),
            )

        # --------------------------------------------------
        # Missing Data
        # --------------------------------------------------

        st.markdown("### Missing Data")

        if missing_values:
            missing_quality_rows = []

            for column, details in (
                missing_values.items()
            ):
                missing_quality_rows.append(
                    {
                        "Column": column,
                        "Missing Values": details[
                            "count"
                        ],
                        "Missing %": details[
                            "percentage"
                        ],
                    }
                )

            missing_quality_df = pd.DataFrame(
                missing_quality_rows
            )

            missing_quality_df = (
                missing_quality_df.sort_values(
                    "Missing %",
                    ascending=False,
                )
            )

            st.dataframe(
                missing_quality_df,
                width="stretch",
            )

        else:
            st.success(
                "No missing values found."
            )

        # --------------------------------------------------
        # Duplicate Rows
        # --------------------------------------------------

        st.markdown("### Duplicate Rows")

        if duplicate_rows == 0:
            st.success(
                "No duplicate rows found."
            )
        else:
            st.warning(
                f"{duplicate_rows:,} duplicate "
                "row(s) found."
            )

        # --------------------------------------------------
        # Low-Information Columns
        # --------------------------------------------------

        st.markdown(
            "### Low-Information Columns"
        )

        if low_information_columns:
            st.warning(
                "These columns contain only one "
                "unique value and may provide "
                "limited analytical value:"
            )

            st.write(
                ", ".join(
                    low_information_columns
                )
            )

        else:
            st.success(
                "No low-information columns found."
            )

        # --------------------------------------------------
        # Potential Numeric Columns
        # --------------------------------------------------

        st.markdown(
            "### Potential Numeric Columns"
        )

        if potential_numeric_columns:
            st.warning(
                "These text columns appear to "
                "contain mostly numeric values:"
            )

            st.write(
                ", ".join(
                    potential_numeric_columns
                )
            )

        else:
            st.success(
                "No obvious numeric columns stored "
                "as text were detected."
            )

        # --------------------------------------------------
        # General Dataset Insights
        # --------------------------------------------------

        st.subheader("💡 Key Findings")

        key_findings = analysis.get(
            "key_findings",
            [],
        )

        if key_findings:
            for finding in key_findings:
                st.write(f"• {finding}")
        else:
            st.info(
                "No key findings could be generated."
            )

        st.subheader("📈 Dataset Insights")

        data_types = analysis.get(
            "data_types",
            {},
        )

        numeric_columns = [
            column
            for column, dtype in data_types.items()
            if dtype.startswith(
                ("int", "float")
            )
        ]

        categorical_columns = [
            column
            for column, dtype in data_types.items()
            if dtype in [
                "object",
                "str",
                "category",
                "bool",
            ]
        ]

        identifier_columns = []
        location_columns = []

        identifier_keywords = [
            "id",
            "customerid",
            "orderid",
            "userid",
            "accountid",
        ]

        location_keywords = [
            "latitude",
            "longitude",
            "lat long",
            "zip",
            "postal",
            "postcode",
        ]

        for column in data_types:

            column_lower = column.lower()

            if any(
                keyword in column_lower
                for keyword in identifier_keywords
            ):
                identifier_columns.append(column)

            elif any(
                keyword in column_lower
                for keyword in location_keywords
            ):
                location_columns.append(column)

        excluded_numeric_columns = [
            "Count",
            "Churn Value",
            "Churn Score",
        ]

        analytical_numeric_columns = [
            column
            for column in numeric_columns
            if column not in location_columns
            and column not in identifier_columns
            and column not in excluded_numeric_columns
        ]

        analytical_categorical_columns = [
            column
            for column in categorical_columns
            if column not in identifier_columns
            and column not in location_columns
        ]

        insight_col1, insight_col2 = (
            st.columns(2)
        )

        with insight_col1:
            st.metric(
                "Analytical Numeric Variables",
                len(analytical_numeric_columns),
            )

        with insight_col2:
            st.metric(
                "Analytical Categorical Variables",
                len(analytical_categorical_columns),
            )

        if analytical_numeric_columns:
            st.markdown(
                "### Numeric Variables"
            )

            st.write(
                ", ".join(
                    analytical_numeric_columns
                )
            )

        if analytical_categorical_columns:
            st.markdown(
                "### Categorical Variables"
            )

            st.write(
                ", ".join(
                    analytical_categorical_columns
                )
            )

        if identifier_columns:
            st.markdown(
                "### Identifier Columns"
            )

            st.write(
                ", ".join(
                    identifier_columns
                )
            )

        if location_columns:
            st.markdown(
                "### Location Columns"
            )

            st.write(
                ", ".join(
                    location_columns
                )
            )

        # --------------------------------------------------
        # Correlation Analysis
        # --------------------------------------------------

        st.subheader("🔗 Correlation Analysis")

        correlations = analysis.get(
            "correlations",
            {},
        )

        if correlations:
            correlation_df = pd.DataFrame(
                correlations
            )

            # Create a list of unique variable pairs
            correlation_pairs = []

            columns = (
                correlation_df.columns.tolist()
            )

            for i in range(len(columns)):
                for j in range(
                    i + 1,
                    len(columns),
                ):
                    column_1 = columns[i]
                    column_2 = columns[j]

                    value = correlation_df.loc[
                        column_1,
                        column_2,
                    ]

                    correlation_pairs.append(
                        {
                            "Variable 1": column_1,
                            "Variable 2": column_2,
                            "Correlation": value,
                            "Absolute Correlation": abs(
                                value
                            ),
                        }
                    )

            correlation_pairs_df = pd.DataFrame(
                correlation_pairs
            )

            correlation_pairs_df = (
                correlation_pairs_df
                .sort_values(
                    "Absolute Correlation",
                    ascending=False,
                )
                .reset_index(drop=True)
            )

            # Display heatmap
            heatmap = correlation_heatmap(
                correlation_df
            )

            if heatmap is not None:
                st.plotly_chart(
                    heatmap,
                    width="stretch",
                )

            # Strongest relationships
            st.markdown(
                "### Strongest Relationships"
            )

            top_correlations = (
                correlation_pairs_df
                .head(5)
                .copy()
            )

            top_correlations = (
                top_correlations[
                    [
                        "Variable 1",
                        "Variable 2",
                        "Correlation",
                    ]
                ]
            )

            top_correlations[
                "Correlation"
            ] = (
                top_correlations[
                    "Correlation"
                ].round(2)
            )

            st.dataframe(
                top_correlations,
                width="stretch",
                hide_index=True,
            )

            with st.expander(
                "View all correlation values"
            ):
                st.dataframe(
                    correlation_df,
                    width="stretch",
                )

        else:
            st.info(
                "Not enough numeric columns "
                "for correlation analysis."
            )

        # --------------------------------------------------
        # Specialized Dataset Analysis
        # --------------------------------------------------

        if dataset_type == "churn":

            # --------------------------------------------------
            # Churn Analysis
            # --------------------------------------------------

            st.subheader(
                "📊 Churn Analysis"
            )

            business_metrics = analysis.get(
                "business_metrics",
                {},
            )

            churn_distribution = (
                business_metrics.get(
                    "churn_distribution",
                    {},
                )
            )

            churned = churn_distribution.get(
                "Yes",
                0,
            )

            total_customers = len(df)

            churn_rate = (
                churned / total_customers * 100
                if total_customers > 0
                else 0
            )

            revenue_at_risk = (
                business_metrics.get(
                    "churned_monthly_revenue",
                    0,
                )
            )

            churned_customers = (
                business_metrics.get(
                    "churned_customers",
                    0,
                )
            )

            retained_customers = (
                business_metrics.get(
                    "retained_customers",
                    0,
                )
            )

            metric_col1, metric_col2, metric_col3, metric_col4 = (
                st.columns(4)
            )

            with metric_col1:
                st.metric(
                    "Overall Churn Rate",
                    f"{churn_rate:.1f}%",
                )

            with metric_col2:
                st.metric(
                    "Churned Customers",
                    f"{churned_customers:,}",
                )

            with metric_col3:
                st.metric(
                    "Retained Customers",
                    f"{retained_customers:,}",
                )

            with metric_col4:
                st.metric(
                    "Monthly Revenue at Risk",
                    f"${revenue_at_risk:,.2f}",
                )

            # --------------------------------------------------
            # Churn Rate by Contract
            # --------------------------------------------------

            if "Contract" in df.columns:
                contract_chart = (
                    churn_rate_by_column(
                        df,
                        "Contract",
                    )
                )

                if contract_chart is not None:
                    st.plotly_chart(
                        contract_chart,
                        width="stretch",
                    )

            # --------------------------------------------------
            # Churn Rate by Internet Service
            # --------------------------------------------------

            if "Internet Service" in df.columns:
                internet_chart = (
                    churn_rate_by_column(
                        df,
                        "Internet Service",
                    )
                )

                if internet_chart is not None:
                    st.plotly_chart(
                        internet_chart,
                        width="stretch",
                    )

            # --------------------------------------------------
            # Churn Rate by Payment Method
            # --------------------------------------------------

            if "Payment Method" in df.columns:
                payment_chart = (
                    churn_rate_by_column(
                        df,
                        "Payment Method",
                    )
                )

                if payment_chart is not None:
                    st.plotly_chart(
                        payment_chart,
                        width="stretch",
                    )

            # --------------------------------------------------
            # Churn Rate by Tenure
            # --------------------------------------------------

            if "Tenure Months" in df.columns:
                tenure_chart = (
                    churn_rate_by_tenure(df)
                )

                if tenure_chart is not None:
                    st.plotly_chart(
                        tenure_chart,
                        width="stretch",
                    )

            # --------------------------------------------------
            # Churn Rate by Customer Segment
            # --------------------------------------------------

            st.subheader(
                "📌 Churn Rate by Customer Segment"
            )

            churn_extremes = (
                business_metrics.get(
                    "churn_rate_extremes",
                    {},
                )
            )

            if churn_extremes:

                segment_rows = []

                for column, extremes in (
                    churn_extremes.items()
                ):

                    highest = extremes.get(
                        "highest",
                        {},
                    )

                    lowest = extremes.get(
                        "lowest",
                        {},
                    )

                    segment_rows.append(
                        {
                            "Variable": column,
                            "Highest Churn Group": (
                                highest.get("group")
                            ),
                            "Highest Churn Rate": (
                                highest.get(
                                    "churn_rate"
                                )
                            ),
                            "Lowest Churn Group": (
                                lowest.get("group")
                            ),
                            "Lowest Churn Rate": (
                                lowest.get(
                                    "churn_rate"
                                )
                            ),
                        }
                    )

                segment_df = pd.DataFrame(
                    segment_rows
                )

                segment_df[
                    "Highest Churn Rate"
                ] = (
                    segment_df[
                        "Highest Churn Rate"
                    ].round(2)
                )

                segment_df[
                    "Lowest Churn Rate"
                ] = (
                    segment_df[
                        "Lowest Churn Rate"
                    ].round(2)
                )

                st.dataframe(
                    segment_df,
                    width="stretch",
                    hide_index=True,
                )

            else:
                st.info(
                    "No categorical segment "
                    "comparisons are available."
                )

            # --------------------------------------------------
            # Churned vs Retained
            # --------------------------------------------------

            st.subheader(
                "👥 Churned vs Retained"
            )

            churn_group_means = (
                business_metrics.get(
                    "churn_group_means",
                    {},
                )
            )

            if churn_group_means:
                profile_df = pd.DataFrame(
                    churn_group_means
                )

                useful_columns = [
                    column
                    for column in [
                        "Tenure Months",
                        "Monthly Charges",
                        "Total Charges",
                        "CLTV",
                        "Churn Score",
                    ]
                    if column in profile_df.index
                ]

                if useful_columns:
                    st.dataframe(
                        profile_df
                        .loc[useful_columns]
                        .round(2),
                        width="stretch",
                    )

        # --------------------------------------------------
        # Dataset Type
        # --------------------------------------------------

        st.subheader("🧭 Dataset Type")

        if dataset_type == "churn":
            st.info(
                "Detected dataset type: Customer Churn"
            )
        else:
            st.info(
                "No specialized dataset type detected. "
                "Showing general statistical analysis."
            )

        # --------------------------------------------------
        # Download Analysis
        # --------------------------------------------------

        st.subheader(
            "📥 Download Analysis"
        )

        analysis_json = json.dumps(
            analysis,
            indent=2,
            default=str,
        )

        st.download_button(
            label="Download Analysis (JSON)",
            data=analysis_json,
            file_name="insightcsv_analysis.json",
            mime="application/json",
        )

        # --------------------------------------------------
        # AI Analysis
        # --------------------------------------------------

        if st.button(
            "🤖 Generate AI Analysis"
        ):
            with st.spinner(
                "Analyzing your dataset with Claude..."
            ):
                insights = generate_insights(
                    analysis
                )

            st.subheader(
                "🤖 AI Analysis"
            )

            st.markdown(
                insights
            )

    except Exception as e:
        st.error(
            f"Something went wrong: {str(e)}"
        )