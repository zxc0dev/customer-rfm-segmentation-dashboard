import pandas as pd
import re

def df_overview(df):
    print(f"{'='*33} Shape {'='*33}")
    print(df.shape)
    print(f"{'='*33} Info {'='*33}")
    print(df.info())
    print(f"{'='*33} Columns {'='*33}")
    print(df.columns)
    print(f"{'='*33} Describe {'='*33}")
    print(df.describe())
    print(f"{'='*33} NaN {'='*33}")
    print(df.isnull().sum())
    print(f"{'='*33} Duplicates {'='*33}")
    print(df.duplicated().sum())
    print(f"{'='*33} Cardinality & Top Values {'='*33}")
    for c in df.select_dtypes(include='object').columns:
        print(c, df[c].nunique(), df[c].value_counts(normalize=True).head())


def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:

    def clean_name(name: str) -> str:
        s1 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', name)
        s2 = re.sub(r'[^a-zA-Z0-9]+', '_', s1)
        return s2.lower().strip('_')

    df.columns = [clean_name(col) for col in df.columns]
    return df