# AI Tailor Smart Allocator

AI Tailor Smart Allocator is a Streamlit-based decision support tool for recommending tailors to garment production projects. It combines data cleaning, feature engineering, K-Means clustering, and a scoring model for project allocation.

## Overview

The project analyzes tailor performance and profile data, groups tailors into capability clusters, and recommends the best candidates for incoming production work. It is designed for tailoring cooperatives or small garment operations that need a more consistent way to assign orders.

## Key Features

- Data cleaning pipeline for raw tailor data.
- Feature engineering using age, distance, neatness, punctuality, quantity, and commitment indicators.
- K-Means clustering into operational groups such as elite, standard, and needs-guidance tailors.
- Project allocation scoring based on capability, specialist fit, distance, productivity, attitude, and urgency.
- Streamlit dashboard for exploring tailor clusters and top recommendations.
- Top-10 tailor recommendation output for each project scenario.
- Support for project categories such as custom, gamis, and difficult orders.

## Tech Stack

- Language: Python
- App framework: Streamlit
- Data processing: pandas
- Machine learning: scikit-learn, KMeans, MinMaxScaler
- Data files: CSV and Excel datasets

## Project Structure

```text
app.py                         Streamlit dashboard
allocation.py                  Tailor recommendation and scoring logic
clustering_penjahit.py         Clustering helpers
feature_engineering.py         Feature engineering and cluster labeling pipeline
data_cleaning.py               Data cleaning flow
DATA CLEANED.xlsx              Cleaned source dataset
DATA_FINAL_CLUSTERED.csv       Clustered dataset used by the dashboard
```

## Getting Started

Create a virtual environment and install dependencies:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install streamlit pandas scikit-learn openpyxl
```

Regenerate the clustered dataset when the source spreadsheet changes:

```bash
python data_cleaning.py
python feature_engineering.py
```

Run the dashboard:

```bash
streamlit run app.py
```

## Allocation Logic

The allocator filters and scores candidates based on project type and operational signals. Urgent orders prioritize capacity, speed, and proximity more heavily. Normal orders balance capability, attitude, historical quantity, and specialist match.

## Limitations

- Recommendations depend heavily on the quality and freshness of the source dataset.
- K-Means clusters are descriptive and should be reviewed by a human manager before assignment.
- The scoring weights are business rules, not automatically learned optimization weights.
- More validation is needed before using this as the only assignment authority in a live operation.

## Suggested Tests

- Unit tests for project category mapping.
- Regression tests for scoring weight changes.
- Dataset validation checks for missing columns and invalid numeric ranges.
- Manual review against historical project outcomes.

## Status

Data-driven portfolio prototype for production allocation support.
