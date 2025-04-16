import pandas as pd
import numpy as np
import os
from pathlib import Path

parent_dir = Path(__file__).resolve().parent.parent
data_dir = os.path.join(parent_dir, "data")


def load_data(file_path: str = data_dir + '/account_activity.csv') -> pd.DataFrame:
    df = pd.read_csv(file_path)
    return df


# print(load_data().head())
