import pandas as pd


def process_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Basic data cleaning pipeline:
    - Remove duplicates
    - Handle missing values
    - Standardize columns
    """

    df = df.drop_duplicates()
    df = df.fillna(0)

    # Example normalization
    df.columns = [col.strip().lower() for col in df.columns]

    return df