"""Export SA rows (Table 4) of the ABS 2021 Mesh Block Counts workbook (already on disk) to a CSV in the git-ignored data folder, for build_scores.py."""
import pandas as pd
src = '/Users/ray/Research/AUSSEF - Local/fire_event_dataset/data/raw/grp_insurance/asgs/Mesh_Block_Counts_2021.xlsx'
d = pd.read_excel(src, sheet_name='Table 4', header=6, dtype={'MB_CODE_2021': str})
d = d[d.MB_CODE_2021.astype(str).str.fullmatch(r'\d{11}', na=False)]
print(d.columns.tolist(), len(d))
d.to_csv('/Users/ray/Research/AUSSEF - Local/fire_event_dataset/data/extra_fires/mb2021_sa_counts.csv', index=False)
print(d.head(3)); print(d[['Dwelling', 'Person']].sum())
