# Disaster-overlap screen for recovered project histories

The screen covers all eight distinct council-years represented in budget_snapshots, using the inherited V2 exposure panel with its original quality limits. Six have positive declarations or mapped burn; two have no certified untreated status. This is screening evidence, not proof of local asset damage or complete event coverage. No comparison was certified.

Ballina FY2018/19 lists AGRN834; FY2019/20 lists AGRN871 and898 and mapped burn; FY2020/21 lists AGRN943 and960. Therefore its three recovered annual histories cannot be labelled three unaffected pre-event years. Earlier exposure does not automatically invalidate an event-study design, but requires explicit event histories, recovery carryover and appropriate comparison selection.

The supplied August2026 activation register independently contains Ballina regional disaster-start dates 2020-12-10 (943), 2021-03-10 (960) and 2022-02-22 (1012). These dates are stored in disaster_observations and are not local flood onset, public announcement dates or project-damage dates. The December event precedes the January2021 deferral decision; the March event precedes the April decision. Temporal ordering alone does not establish why the budget changed.

The inherited panel also flags overlapping events for Lismore and Richmond Valley (987 and1012), and Eurobodalla (871 and898). Snowy Valleys is outside the inherited continuing-council panel. Wagga's lack of a listed event in this panel is not physical zero. Existing project damage_status remains unknown where unsupported.

Canonical council_year_exposure_screen.csv and its SQLite table retain council-year identifiers, event IDs, mapped-burn status, physical flood status and source provenance. Sources are a frozen inherited candidate panel and a user-supplied register; their primary-source provenance and coverage are not newly certified here. The register's missing earlier years cannot erase positive older records.

Reproduction: run screen_disaster_overlap.py after extend_ballina_history.py. Next work: reconcile each AGRN against primary event records, recover local impact and asset-level damage/access evidence, then screen broader comparison candidates and their pre-event budgets. No modelling or causal attribution performed.
