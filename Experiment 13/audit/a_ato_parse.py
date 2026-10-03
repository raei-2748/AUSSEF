# Audit: parse ATO Table 6 postcode sheets independently -> audit_ato.parquet (NSW postcode x income year)
import pandas as pd, numpy as np, re
R = '../income_ato/raw/'
SHEETS = {2010:'Individuals Tax Table 6a', 2011:'Individual tax table 6A', 2012:'Postcode only'}
rows = []
for y in range(2010, 2023):
    f = f'{R}ato_t6_{y}-{str(y+1)[2:]}.xlsx'
    if y in SHEETS: sh = SHEETS[y]
    else:
        import openpyxl
        sh = [s for s in openpyxl.load_workbook(f, read_only=True).sheetnames if s.strip().upper().endswith('6B')][0]
    raw = pd.read_excel(f, sheet_name=sh, header=None, dtype=object)
    hr = next(i for i in range(10) if any(str(v).strip() == 'Postcode' for v in raw.iloc[i]))
    hdr = [str(a) for a in raw.iloc[hr]]
    # unit row (2010-11 has a separate unit row)
    unit = [str(a) for a in raw.iloc[hr+1]]
    has_unit_row = sum(u in ('$', 'no.') for u in unit) > 5
    names = [(h + ('\n' + u if has_unit_row and u != 'nan' else '')).replace('\n', ' ') for h, u in zip(hdr, unit)]
    body = raw.iloc[hr + (2 if has_unit_row else 1):].copy(); body.columns = range(len(names))
    def col(pat, unit_s):
        c = [i for i, n in enumerate(names) if re.search(pat, n, re.I) and n.strip().endswith(unit_s)]
        return c
    ipc = names.index('Postcode'); ist = [i for i, n in enumerate(names) if n.startswith('State')][0]
    inum = [i for i, n in enumerate(names) if re.match(r'(Number of individuals|Individuals)( no\.)?\s*$', n.strip())]
    iti = col(r'^Taxable income or loss\d?\s*\$?', '$')
    iti = [i for i in iti if names[i].lower().startswith('taxable income or loss')]
    assert len(inum) == 1 and len(iti) == 1, (y, inum, iti, names[:8])
    d = pd.DataFrame({'state': body[ist].astype(str).str.strip(), 'pc': body[ipc], 'n_ind': pd.to_numeric(body[inum[0]], errors='coerce'),
                      'ti': pd.to_numeric(body[iti[0]], errors='coerce')})
    d = d[d.state == 'NSW']
    d['pc'] = pd.to_numeric(d.pc, errors='coerce')
    d = d[d.pc.notna()]
    d['pc'] = d.pc.astype(int).astype(str).str.zfill(4)
    dup = d.pc.duplicated().sum()
    print(y, sh, 'hdr', names[inum[0]], '|', names[iti[0]], '| NSW rows', len(d), 'dup pcs', dup, 'missing ti', d.ti.isna().sum())
    d = d.groupby('pc', as_index=False)[['n_ind', 'ti']].sum(min_count=1)
    d['year'] = y
    rows.append(d)
out = pd.concat(rows)
out.to_parquet('audit_ato.parquet')
print(out.groupby('year').size())
