"""Step 3: apply the fill rule and write fill_table.csv (one line per council row that gets a value) and SEASON_BUDGET.csv.

Fill rule, in order of reliability (every filled cell carries its flag, so estimated values are never mixed silently):

 reported_new              a published source states the homes-destroyed figure (or 'no homes destroyed') for a fire that is one of the row's
                           fires, in that council. Includes 'duplicate link': the same physical fire is linked to two declarations in the
                           dataset and only one of them already had the figure.
 inferred_zero_season      the row is 0 because an OFFICIAL statewide season total of homes destroyed (RFS) is used up by fires already
                           attributed: residual = official total - attributed <= 1 home, so at most one unexplained home in the whole season.
                           Applied to 2015/16, 2018/19 and 2022/23.
 reported_weak             a source states a figure but the match is weak: hedged 'at least', news 'locals believe', a different date for the
                           same locality, or the fire spans several councils. Only used from variant v3.
 estimated_area_share      one whole-fire figure split across the councils it burned in, by burned area (the dataset's own proxy). Estimate.
 estimated_zero_season_budget  0 because the season residual is small but > 1 (2017/18: 3 homes unexplained across all remaining rows). Estimate.
 estimated_zero_small_fire 0 by a size rule (share burned < 2% of the council AND < 5,000 ha in the council), no evidence of loss found. Estimate.
 missing                   everything else.

Season = 1 July to 30 June of the row's first_fire_start (the RFS season box is by financial year / bush fire danger period).
"""
import numpy as np
import pandas as pd

from common import HERE, OUT, load_master

SEASON_TOTALS = {
    # season: (official homes destroyed, attributed inside the 218 rows is computed, named fires outside the rows, source)
    '2015/16': dict(total=1, outside=0, src='NSW RFS Annual Report 2015/16, Fire season overview box (p.28): "Loss/damage 1 habitable structure"',
                    url='https://www.rfs.nsw.gov.au/resources/publications/annual-reports/general/nsw-rural-fire-service-2015-16-annual-report/3-NSW-RFS-Annual-Report-2015-16-Summary-Review-of-Operations.pdf'),
    '2016/17': dict(total=65, outside=6 + 1 + 11 + 1,
                    src='NSW RFS media release 31 Mar 2017 "Bush fire season draws to a close": "Total number of properties destroyed - 65"; outside the rows: Pappinbarra 6, Boggabri 1, Carwoola 11, Currandooley 1 (RFS 18 Feb 2017 final assessment; RFS 31 Mar 2017)',
                    url='https://www.rfs.nsw.gov.au/news-and-media/media-releases/bush-fire-season-draws-to-a-close3'),
    '2017/18': dict(total=74, outside=0,
                    src='NSW RFS media release 3 Apr 2018 "Bush Fire Danger Period wraps up": "74 homes and 58 structures destroyed"; NSW RFS Annual Report 2017/18 p.28: 74 habitable structures destroyed',
                    url='https://www.rfs.nsw.gov.au/news-and-media/media-releases/bush-fire-danger-period-wraps-up'),
    '2018/19': dict(total=37, outside=0,
                    src='NSW RFS Annual Report 2018/19 p.26: "37 habitable structures destroyed and 27 damaged"',
                    url='https://www.rfs.nsw.gov.au/__data/assets/pdf_file/0004/129892/NSW-RFS-Annual-Report-2018-19-web.pdf'),
    '2022/23': dict(total=8, outside=6,
                    src='NSW RFS media release 28 Apr 2023 "Bush Fire Season ends for NSW": "the loss of eight homes, 15 outbuildings"; outside the rows: Hill End/Tambaroora (Alpha Rd) 6 (RFS Bush Fire Bulletin 45(1) p.3 "at least six"; AIDR Major Incidents Report 2022-23 case study 5 "Six houses ... destroyed")',
                    url='https://www.rfs.nsw.gov.au/news-and-media/media-releases/end-of-fire-season-for-nsw'),
    '2023/24': dict(total=29, outside=0,
                    src='NSW RFS media release 31 Mar 2024 "Fire season comes to a close for most of NSW": "A total of 29 homes, 142 outbuildings"',
                    url='https://www.rfs.nsw.gov.au/news-and-media/media-releases/fire-season-comes-to-a-close-for-most-of-nsw'),
}
INFER_MAX_RESIDUAL = 1        # residual <= this  -> inferred_zero_season
BUDGET_MAX_RESIDUAL = 3       # residual <= this  -> estimated_zero_season_budget
SMALL_SHARE, SMALL_HA = 0.02, 5000
NO_ESTIMATE = {('RAA-raa_2016_p13_r17', 15270): 'Sir Ivan fire (35 homes, council split not published) may be part of this row; left missing'}


def season(t):
    y = t.year if t.month >= 7 else t.year - 1
    return f'{y}/{str(y + 1)[2:]}'


def main():
    m = load_master()
    d = pd.DataFrame({'agrn': m.agrn, 'region_id': m.region_id, 'region_name': m.region_name,
                      'start': pd.to_datetime(m.first_fire_start), 'share': m.share, 'burn_ha': m.burn_ha,
                      'homes': pd.to_numeric(m.DL_homes_destroyed_in_council, errors='coerce')})
    d['season'] = d.start.map(season)
    d['missing'] = d.homes.isna()

    # ---- season budget
    rows = []
    for s, v in SEASON_TOTALS.items():
        inside = d[(d.season == s) & ~d.missing].homes.sum()
        res = v['total'] - inside - v['outside']
        rule = ('inferred_zero_season' if res <= INFER_MAX_RESIDUAL else
                'estimated_zero_season_budget' if res <= BUDGET_MAX_RESIDUAL else 'none (residual too large)')
        rows.append(dict(season=s, official_total=v['total'], attributed_in_rows=inside, attributed_named_outside_rows=v['outside'],
                         residual=res, rows=int((d.season == s).sum()), rows_missing=int(((d.season == s) & d.missing).sum()),
                         rule=rule, source=v['src'], url=v['url']))
    sb = pd.DataFrame(rows)
    sb.to_csv(OUT / 'SEASON_BUDGET.csv', index=False)
    print(sb.drop(columns=['source', 'url']).to_string(index=False))

    fills = []

    def add(agrn, rid, value, flag, scope, url, quote, note, stype, conf):
        fills.append(dict(agrn=agrn, region_id=rid, value=value, flag=flag, scope=scope, url=url, quote=quote, note=note,
                          source_type=stype, confidence=conf))

    rid = lambda agrn, name: int(d[(d.agrn == agrn) & (d.region_name == name)].region_id.iloc[0])

    # ---- reported_new
    add('818', rid('818', 'Shoalhaven'), 0, 'reported_new', 'fire_in_council',
        'https://www.abc.net.au/news/2018-08-16/nsw-fires-shock-nowra-as-authorities-warn-conditions-dangerous/10123456',
        'The Nowra fire was one of three blazes in New South Wales that was threatening properties, although no homes were destroyed.',
        'Kingiman (Croobyar Rd) fire 15-16 Aug 2018. Same-day RFS Building Impact Assessment list (ABC, https://www.abc.net.au/news/2018-08-16/houses-destroyed-bega-fire/10129172): 1 house damaged (North Nowra), 11 outbuildings destroyed at Kingiman, no house destroyed. Dataset already holds homes_damaged=1 for this row.',
        'news', 'medium')
    add('1052', rid('1052', 'Cowra'), 1, 'reported_new', 'fire_in_council',
        'https://www.abc.net.au/news/2023-02-17/cowra-fire-threatens-properties-homes/101988150',
        'A house has been destroyed in the blaze near Cowra.',
        'Duplicate link: Conimbla Rd fire (16 Feb 2023) is linked to both AGRN 1052 and 1055; the dataset already holds 1 home for the 1055/Cowra row. RFS Bush Fire Bulletin 45(1) p.4 says only that the roof of a brick house was blown off, so destroyed-vs-damaged is not settled.',
        'news', 'medium')
    add('1089', rid('1089', 'Mid-Coast'), 1, 'reported_new', 'fire_in_council',
        'https://www.abc.net.au/news/2023-10-21/nsw-weather-preview-hot-windy-bom-rfs-forecast-fire-danger/102998776',
        'One home was been destroyed in the Booral Road fire at Girvan',
        'Duplicate link: Booral Rd, Girvan fire is in the main-fire lists of both AGRN 1076 and 1089; the dataset already holds 1 home for the 1076/Mid-Coast row (same ABC article). Lower bound for the council.',
        'news', 'medium')

    # ---- reported_weak
    add('880', rid('880', 'Clarence Valley'), 9, 'reported_weak', 'multi_council',
        'https://coroners.nsw.gov.au/documents/reports/bushfires/2019-20-NSW-Bushfires-Coronial-Inquiry-Vol1.pdf',
        'At least 9 residences were destroyed',
        'Bees Nest (Guy Fawkes NP) fire, 30 Aug - 13 Nov 2019, chapter 10 p.234: burned in Armidale Regional, Clarence Valley and Bellingen; the Coroner does not split the residences by council. Lower bound ("at least"). These homes are also inside the 168 homes the dataset holds for Clarence Valley under AGRN 871 (NBRA profile, whole 2019-20 season).',
        'official', 'low')
    add('1081', rid('1081', 'Walgett'), 3, 'reported_weak', 'fire_in_council',
        'https://www.abc.net.au/news/2024-01-15/grawin-opal-fields-bushfire-recovery/103284620',
        'locals believe about 16 camps and three residences where lost',
        'Hudson fire (Grawin/Glengarry opal fields), Nov 2023. AIDR Major Incidents Report 2023-24 gives 24 "properties" destroyed and 20 damaged (unit is properties, not homes; includes mining camps). ABC quotes a local belief of about three residences. RFS statewide 2023/24 total is 29 homes, so 24 cannot all be houses.',
        'news', 'low')
    add('RAA-raa_2016_p13_r12', rid('RAA-raa_2016_p13_r12', 'Penrith'), 0, 'reported_weak', 'fire_in_council',
        'https://www.rfs.nsw.gov.au/news-and-media/media-releases/llandilo-bush-fire-assessment',
        'No homes have been destroyed.',
        'RFS Building Impact Assessment of the Llandilo fire of 4 Nov 2016 (4 houses damaged). The dataset row is "The Northern Rd, Londonderry" started 13 Nov 2016 and the dataset lists a separate unlinked "BUSHFIRE Llandilo" record for 4-10 Nov, so the match is by locality, not by fire.',
        'official', 'low')

    # ---- estimated_area_share: Hill End / Tambaroora (Alpha Rd) fire, 6 homes over Bathurst + Mid-Western
    hb = d[(d.agrn == '1052') & d.region_name.isin(['Bathurst Regional', 'Mid-Western Regional'])]
    for r in hb.itertuples():
        add('1052', int(r.region_id), round(6 * r.burn_ha / hb.burn_ha.sum(), 3), 'estimated_area_share', 'multi_council',
            'https://www.rfs.nsw.gov.au/__data/assets/pdf_file/0007/253267/Bush-Fire-Bulletin-V45-No1-2023.pdf',
            'At least six homes and five outbuildings in the area were destroyed and a further nine damaged',
            f'Alpha Rd / Hill End fire, whole-fire figure (RFS Bush Fire Bulletin 45(1) p.3; AIDR 2022-23 "Six houses"). No source says which council; split 6 x burned area in council / both. ESTIMATE.',
            'official', 'low')

    done = {(f['agrn'], f['region_id']) for f in fills}
    fl = pd.DataFrame(fills)

    # ---- inferred_zero_season / estimated_zero_season_budget
    miss = d[d.missing & ~d.set_index(['agrn', 'region_id']).index.isin(done)]
    sbi = sb.set_index('season')
    for r in miss.itertuples():
        if r.season not in sbi.index:
            continue
        s = sbi.loc[r.season]
        if s.rule == 'inferred_zero_season':
            flag, conf = 'inferred_zero_season', 'medium'
        elif s.rule == 'estimated_zero_season_budget':
            flag, conf = 'estimated_zero_season_budget', 'low'
        else:
            continue
        if (r.agrn, r.region_id) in NO_ESTIMATE:
            continue
        add(r.agrn, int(r.region_id), 0, flag, 'season_total', s.url, s.source,
            f'season {r.season}: official total {s.official_total}, attributed {s.attributed_in_rows + s.attributed_named_outside_rows}, residual {s.residual}',
            'official', conf)
    done = {(f['agrn'], f['region_id']) for f in fills}

    # ---- estimated_zero_small_fire
    miss = d[d.missing & ~d.set_index(['agrn', 'region_id']).index.isin(done)]
    for r in miss.itertuples():
        if (r.agrn, r.region_id) in NO_ESTIMATE:
            continue
        if r.share < SMALL_SHARE and r.burn_ha < SMALL_HA:
            add(r.agrn, int(r.region_id), 0, 'estimated_zero_small_fire', 'size_rule', '', '',
                f'0 by rule: {r.share:.2%} of council and {r.burn_ha:,.0f} ha burned in council (< {SMALL_SHARE:.0%} and < {SMALL_HA:,} ha), no loss found in any source; season {r.season}',
                '', 'low')

    f = pd.DataFrame(fills)
    f.to_csv(HERE / 'fill_table.csv', index=False)
    print(f.flag.value_counts().to_string())
    left = d[d.missing & ~d.set_index(['agrn', 'region_id']).index.isin({(a, b) for a, b in zip(f.agrn, f.region_id)})]
    print('still missing:', len(left))
    left[['agrn', 'region_name', 'season', 'share', 'burn_ha']].to_csv(OUT / 'STILL_MISSING.csv', index=False)
    return f


if __name__ == '__main__':
    main()
