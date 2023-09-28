import pandas as pd

ASDU_TYPES_CSV = 'ASDU_types.csv'
asdu_types_df = pd.read_csv(ASDU_TYPES_CSV)
print(asdu_types_df)