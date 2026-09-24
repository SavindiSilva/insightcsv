import pandas as pd

def detect_dataset_type(df: pd.DataFrame) -> str:
    """
    Detect whether the dataset matches a known
    specialized analysis type.
    """

    columns = set(df.columns)

    # Churn dataset detection
    churn_indicators = {
        "Churn Label",
        "Churn Value",
        "Churn Score",
    }

    if len(columns.intersection(churn_indicators)) >= 1:
        return "churn"

    return "generic"

def analyze_dataframe(df: pd.DataFrame) -> dict:
    df = df.copy()

    # --------------------------------------------------
    # Clean known numeric columns
    # --------------------------------------------------

    if "Total Charges" in df.columns:
        df["Total Charges"] = pd.to_numeric(
            df["Total Charges"],
            errors="coerce"
        )

    # --------------------------------------------------
    # Data quality analysis
    # --------------------------------------------------

    data_quality = {}

    # Missing values
    missing_counts = df.isnull().sum()

    missing_percentages = (
        missing_counts / len(df) * 100
    ).round(2)

    data_quality["missing_values"] = {
        column: {
            "count": int(missing_counts[column]),
            "percentage": float(
                missing_percentages[column]
            ),
        }
        for column in df.columns
        if missing_counts[column] > 0
    }

    # Duplicate rows
    data_quality["duplicate_rows"] = int(
        df.duplicated().sum()
    )

    # Low-information columns
    low_information_columns = [
        column
        for column in df.columns
        if df[column].nunique(dropna=False) <= 1
    ]

    data_quality["low_information_columns"] = (
        low_information_columns
    )

    # Potential numeric columns stored as text
    potential_numeric_columns = []

    for column in df.select_dtypes(
        include="object"
    ).columns:

        converted = pd.to_numeric(
            df[column],
            errors="coerce"
        )

        non_missing = df[column].notna()

        if (
            non_missing.sum() > 0
            and converted[non_missing].notna().mean()
            >= 0.9
        ):
            potential_numeric_columns.append(
                column
            )

    data_quality["potential_numeric_columns"] = (
        potential_numeric_columns
    )

    # --------------------------------------------------
    # Main analysis information
    # --------------------------------------------------

    analysis = {
        "dataset_type": detect_dataset_type(df),
        "rows": len(df),
        "columns": len(df.columns),
        "column_names": df.columns.tolist(),

        # These reflect the cleaned dataframe
        "data_types": (
            df.dtypes.astype(str).to_dict()
        ),

        "missing_values": (
            df.isnull().sum().to_dict()
        ),

        "duplicate_rows": int(
            df.duplicated().sum()
        ),

        "data_quality": data_quality,
    }

    # --------------------------------------------------
    # Numeric analysis
    # --------------------------------------------------

    numeric_columns = df.select_dtypes(
        include="number"
    ).columns

    if len(numeric_columns) > 0:
        analysis["numeric_summary"] = (
            df[numeric_columns]
            .describe()
            .round(2)
            .to_dict()
        )
    else:
        analysis["numeric_summary"] = {}

    # --------------------------------------------------
    # Categorical analysis
    # --------------------------------------------------

    categorical_columns = df.select_dtypes(
        include=[
            "object",
            "category",
            "bool",
        ]
    ).columns

    groupable_columns = [
        column
        for column in categorical_columns
        if df[column].nunique(dropna=True) <= 10
        and df[column].nunique(dropna=True)
        < len(df) * 0.5
    ]

    categorical_summary = {}

    for column in categorical_columns:
        counts = (
            df[column]
            .value_counts(dropna=False)
            .head(10)
        )

        categorical_summary[column] = (
            counts.to_dict()
        )

    analysis["categorical_summary"] = (
        categorical_summary
    )

    # --------------------------------------------------
    # Group-level analysis
    # --------------------------------------------------

    group_analysis = {}

    for categorical_column in groupable_columns:
        unique_values = (
            df[categorical_column]
            .dropna()
            .unique()
        )

        # Avoid creating huge prompts for
        # high-cardinality columns
        if len(unique_values) <= 10:
            group_analysis[categorical_column] = {}

            for value in unique_values:
                group = df[
                    df[categorical_column] == value
                ]

                if len(numeric_columns) > 0:
                    group_stats = (
                        group[numeric_columns]
                        .describe()
                        .round(2)
                        .to_dict()
                    )

                    group_analysis[
                        categorical_column
                    ][str(value)] = {
                        "rows": len(group),
                        "numeric_summary": group_stats,
                    }

    analysis["group_analysis"] = (
        group_analysis
    )

    # --------------------------------------------------
    # Correlation analysis
    # --------------------------------------------------

    excluded_correlation_columns = {
        "Count",
        "Zip Code",
        "Latitude",
        "Longitude",
        "Churn Value",
        "Churn Score",
    }

    correlation_columns = [
        column
        for column in numeric_columns
        if column not in excluded_correlation_columns
    ]

    if len(correlation_columns) > 1:
        correlation_matrix = (
            df[correlation_columns]
            .corr()
            .round(2)
        )

        analysis["correlations"] = (
            correlation_matrix.to_dict()
        )
    else:
        analysis["correlations"] = {}

    # --------------------------------------------------
    # Business-level group metrics
    # --------------------------------------------------

    business_metrics = {}

    if "Churn Label" in df.columns:
        churn_column = df["Churn Label"]

        # Overall churn distribution
        churn_counts = (
            churn_column.value_counts(
                dropna=False
            )
        )

        business_metrics[
            "churn_distribution"
        ] = churn_counts.to_dict()

        # Customer counts
        business_metrics["churned_customers"] = int(
            (churn_column == "Yes").sum()
        )

        business_metrics["retained_customers"] = int(
            (churn_column == "No").sum()
        )

        # Compare numeric metrics between
        # churn groups
        if len(numeric_columns) > 0:
            churn_group_stats = {}

            for churn_value in (
                churn_column.dropna().unique()
            ):
                group = df[
                    churn_column == churn_value
                ]

                churn_group_stats[
                    str(churn_value)
                ] = {
                    column: round(
                        group[column].mean(),
                        2
                    )
                    for column in numeric_columns
                }

            business_metrics[
                "churn_group_means"
            ] = churn_group_stats

        # Calculate churn rate for useful
        # categorical columns
        churn_rates = {}

        for column in groupable_columns:
            rates = (
                df.groupby(
                    column,
                    dropna=False
                )["Churn Label"]
                .apply(
                    lambda x: (
                        x.eq("Yes").mean()
                        * 100
                    )
                )
                .round(2)
                .to_dict()
            )

            churn_rates[column] = {
                str(key): value
                for key, value in rates.items()
            }

        business_metrics[
            "churn_rates_by_group"
        ] = churn_rates

        # Identify highest and lowest churn groups
        churn_extremes = {}

        excluded_churn_extremes = {
            "Churn Label",
            "Country",
            "State",
        }

        for column, rates in churn_rates.items():

            if column in excluded_churn_extremes:
                continue

            if not rates:
                continue

            valid_rates = {
                key: value
                for key, value in rates.items()
                if key != "nan"
            }

            if not valid_rates:
                continue

            highest_group = max(
                valid_rates,
                key=valid_rates.get,
            )

            lowest_group = min(
                valid_rates,
                key=valid_rates.get,
            )

            churn_extremes[column] = {
                "highest": {
                    "group": highest_group,
                    "churn_rate": valid_rates[highest_group],
                },
                "lowest": {
                    "group": lowest_group,
                    "churn_rate": valid_rates[lowest_group],
                },
            }

        business_metrics[
            "churn_rate_extremes"
        ] = churn_extremes

        # Monthly revenue associated with
        # churned customers
        if "Monthly Charges" in df.columns:
            churned_customers = df[
                df["Churn Label"] == "Yes"
            ]

            business_metrics[
                "churned_monthly_revenue"
            ] = round(
                churned_customers[
                    "Monthly Charges"
                ].sum(),
                2
            )

        analysis["business_metrics"] = business_metrics

            # Key findings
    key_findings = []

    # Dataset size
    key_findings.append(
        f"Dataset contains {len(df):,} rows and "
        f"{len(df.columns):,} columns."
    )

    # Missing data
    total_missing = int(
        df.isnull().sum().sum()
    )

    if total_missing > 0:
        columns_with_missing = int(
            (df.isnull().sum() > 0).sum()
        )

        key_findings.append(
            f"{total_missing:,} missing values found "
            f"across {columns_with_missing} columns."
        )
    else:
        key_findings.append(
            "No missing values were detected."
        )

    # Duplicate rows
    duplicate_rows = int(
        df.duplicated().sum()
    )

    if duplicate_rows > 0:
        key_findings.append(
            f"{duplicate_rows:,} duplicate rows were detected."
        )
    else:
        key_findings.append(
            "No duplicate rows were detected."
        )

    # Strongest numeric correlation
    if len(correlation_columns) > 1:
        correlation_matrix = (
            df[correlation_columns]
            .corr()
            .abs()
        )

        correlation_pairs = []

        columns = correlation_matrix.columns.tolist()

        for i in range(len(columns)):
            for j in range(
                i + 1,
                len(columns),
            ):
                value = correlation_matrix.iloc[i, j]

                correlation_pairs.append(
                    (
                        value,
                        columns[i],
                        columns[j],
                    )
                )

        if correlation_pairs:
            strongest = max(
                correlation_pairs,
                key=lambda x: x[0],
            )

            correlation_value = round(
                strongest[0],
                2,
            )

            key_findings.append(
                f"Strongest numeric relationship: "
                f"{strongest[1]} and {strongest[2]} "
                f"(absolute correlation: "
                f"{correlation_value})."
            )

    # Largest categorical group
    largest_group = None

    for column in categorical_columns:
        if column in low_information_columns:
            continue

        if column in [
            "CustomerID",
            "Churn Label",
        ]:
            continue

        counts = (
            df[column]
            .value_counts(dropna=True)
        )

        if counts.empty:
            continue

        value = counts.index[0]
        count = int(counts.iloc[0])

        if (
            largest_group is None
            or count > largest_group["count"]
        ):
            largest_group = {
                "column": column,
                "value": value,
                "count": count,
            }

    if largest_group:
        key_findings.append(
            f"Largest non-uniform categorical group: "
            f"{largest_group['column']} = "
            f"{largest_group['value']} "
            f"({largest_group['count']:,} rows)."
        )

        analysis["key_findings"] = key_findings

        return analysis