"""Guard: no ACM (Australian Community Media) source may appear in any research/findings_*.csv or fill_table.csv."""
import re, sys
import pandas as pd
from pathlib import Path

ACM = (r"newcastleherald|canberratimes|northerndailyleader|namoivalleyindependent|armidaleexpress|gleninnesexaminer|inverelltimes|"
       r"tenterfieldstar|dailyliberal|westernadvocate|goulburnpost|cowraguardian|centralwesterndaily|mudgeeguardian|lithgowmercury|"
       r"singletonargus|muswellbrookchronicle|sconeadvocate|maitlandmercury|illawarramercury|begadistrictnews|naroomanewsonline|"
       r"bayandbasin|southcoastregister|portnews|macleayargus|manningrivertimes|theland\.com|farmonline|cessnockadvertiser|"
       r"portstephensexaminer|greatlakesadvocate|dailyexaminer|coffscoastadvocate|bathurstadvocate|nnsw|crookwellgazette")
bad = 0
here = Path(__file__).parent
files = list((here / 'research').glob('findings_*.csv')) + [here / 'fill_table.csv']
for f in files:
    if not f.exists():
        continue
    d = pd.read_csv(f)
    for col in [c for c in d.columns if c in ('url', 'source_title', 'quote')]:
        hit = d[d[col].fillna('').str.contains(ACM, flags=re.I, regex=True)]
        for i, r in hit.iterrows():
            bad += 1
            print('ACM HIT', f.name, i, col, str(r[col])[:120])
print('files checked', [f.name for f in files if f.exists()], '| ACM hits:', bad)
sys.exit(1 if bad else 0)
