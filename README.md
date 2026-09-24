# InsightCSV

InsightCSV is an AI-powered CSV data analysis application that combines deterministic data analysis with AI-generated business insights.

Users can upload a CSV file and explore its structure, data quality, descriptive statistics, correlations, and dataset-specific analysis through an interactive Streamlit dashboard.

## Features

* Upload and analyze CSV datasets
* Dataset overview and column information
* Missing-value and duplicate detection
* Automatic identification of numeric and categorical variables
* Descriptive statistics
* Correlation analysis
* Dataset-specific analysis for customer churn data
* Churn rates by customer characteristics
* Customer tenure analysis
* Interactive visualizations with Plotly
* Optional AI-generated business insights using Claude
* Export analysis results as JSON

## How it works

InsightCSV separates statistical computation from AI interpretation.

```text
CSV Dataset
    ↓
Pandas Analysis
    ├── Data quality
    ├── Descriptive statistics
    ├── Group analysis
    ├── Correlations
    └── Business metrics
            ↓
      Structured profile
            ↓
        Claude API
            ↓
   Business interpretation
```

Important metrics are calculated deterministically with Pandas rather than asking the language model to perform the underlying analysis. Claude is used primarily to interpret the resulting metrics and communicate useful business insights.

## Tech Stack

* Python
* Pandas
* Streamlit
* Plotly
* Anthropic Claude API
* python-dotenv

## Project Structure

```text
insightcsv/
├── app.py
├── requirements.txt
├── data/
│   └── sample.csv
├── src/
│   ├── analyzer.py
│   ├── claude.py
│   └── visualizer.py
├── test_analyzer.py
├── test_claude.py
├── test_profile.py
├── .gitignore
└── README.md
```

## Running Locally

### 1. Clone the repository

```bash
git clone https://github.com/SavindiSilva/insightcsv.git
cd insightcsv
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows:

```bash
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the application

```bash
streamlit run app.py
```

The application will open in your browser.

## AI Analysis Setup

The core statistical analysis works without an API key.

The optional AI insights feature requires an Anthropic API key.

Create a `.env` file in the project root:

```env
ANTHROPIC_API_KEY=your_api_key_here
```

The `.env` file is excluded from Git through `.gitignore` and should never be committed to the repository.

## Example Dataset

The repository includes a small sample sales dataset in:

```text
data/sample.csv
```

The application can also be tested with larger datasets, including the customer churn dataset used during development.

## Testing

The project includes lightweight tests for the analysis and profile-generation components.

```bash
python test_analyzer.py
python test_profile.py
```

The profile test does not make an API request.

## Limitations

* AI-generated insights depend on the quality and structure of the uploaded dataset.
* The current application provides dataset-specific churn analysis when compatible churn columns are detected.
* The Claude API is optional; statistical analysis does not depend on it.

## Project Purpose

This project was built to explore how traditional data analysis workflows can be combined with LLM-based interpretation while keeping important calculations deterministic and reproducible.
