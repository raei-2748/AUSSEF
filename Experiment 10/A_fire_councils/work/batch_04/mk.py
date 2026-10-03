import csv
FYS=["2015-16","2016-17","2017-18","2018-19","2019-20","2020-21","2021-22","2022-23","2023-24"]
C=[("12350","Cowra"),("12390","Dubbo Regional"),("12700","Dungog"),("12750","Eurobodalla"),("13010","Glen Innes Severn"),("13310","Goulburn Mulwaree")]
ok={}
for r in csv.DictReader(open("downloads_log.csv")):
    if r["result"].startswith("OK"): ok[(r["region_id"],r["fy"])]=r
rows=[];
for rid,n in C:
    for fy in FYS:
        r=ok.get((rid,fy))
        if r:
            reason=""
            st="downloaded"
            if rid=="12390" and fy=="2016-17":
                reason="statements cover 13 May 2016 to 30 June 2017 (first period after amalgamation; also covers FY2015-16 partial period)"
            rows.append([rid,n,fy,st,r["local_path"],r["url"],reason])
        else:
            if rid=="12390" and fy=="2015-16":
                reason="Dubbo Regional's first statements cover 13 May 2016-30 June 2017 (see FY2016-17 file); council page only lists former Dubbo City and Wellington councils' 2015-16 statements, not chased"
            elif rid=="12390": reason="n/a"
            else:
                reason="site returned HTTP 403 (bot protection) to the guarded download tool; no workaround attempted; link found via search/council page"
            rows.append([rid,n,fy,"missing",""," ",reason])
w=csv.writer(open("found_status.csv","w",newline=""));w.writerow("region_id,council,fy,status,local_path,url,reason".split(","));w.writerows(rows)
# biblio
H="source_id,title,author_or_publisher,year,source_type,url,doi,accessed_date,local_path,bytes,sha256,used_in,what_it_was_used_for,pages_or_table,quote_or_value,notes".split(",")
b=[];n=[0]
def add(title,pub,year,st,url,lp="",by="",sha="",used="searched, not used",what="",notes=""):
    n[0]+=1;b.append([f"EXP10A-B04-{n[0]:03d}",title,pub,year,st,url,"","2026-10-02",lp,by,sha,used,what,"","",notes])
for (rid,fy),r in sorted(ok.items()):
    name=dict(C)[rid]
    add(f"{name} general purpose financial statements {fy}",name+" Council",fy.split("-")[0] if False else "20"+fy[-2:],"financial_statement",r["url"],r["local_path"],r["bytes"],r["sha256"],"Experiment 10/A_fire_councils",f"FY{fy} audited GPFS for capex, grants, disaster lines",r["notes"])
# failed links
for r in csv.DictReader(open("downloads_log.csv")):
    if not r["result"].startswith("OK"):
        name=dict(C)[r["region_id"]]
        add(f"{name} financial statements {r['fy']} (download blocked)",name+" Council","20"+r["fy"][-2:],"financial_statement",r["url"],used="searched, not used",what="found PDF link but download failed",notes="link failed 2026-10-02 (HTTP 403)")
pages=[("Dubbo Regional Council reporting page (annual reports and financial statements list)","Dubbo Regional Council","https://dubbo.nsw.gov.au/About-Council/Our-Responsibilities/reporting","web_page","Experiment 10/A_fire_councils","located direct links to all GPFS PDFs"),
("Dungog annual report pages 2017-18, 2018-19, 2021-22, 2022-23","Dungog Shire Council","https://www.dungog.nsw.gov.au/Council/Council-Documents/Integrated-Planning-Reporting/Annual-Reports","web_page","Experiment 10/A_fire_councils","located financial statements PDF links (downloads blocked 403)"),
("Cowra Council plans and reports page (AFS list)","Cowra Shire Council","https://www.cowracouncil.com.au/Council/Governance-and-transparency/Council-Plans-and-reports","web_page","Experiment 10/A_fire_councils","located AFS 2015-16 to 2023-24 links (downloads blocked 403)"),
("Glen Innes Severn audited financial statements page","Glen Innes Severn Council","https://www.gisc.nsw.gov.au/Council/Public-Documents-and-Policies/Audited-Financial-Statements","web_page","Experiment 10/A_fire_councils","located 2020-21 to 2023-24 links (downloads blocked 403)"),
("Glen Innes Severn annual reports page","Glen Innes Severn Council","https://www.gisc.nsw.gov.au/Council/Public-Documents-and-Policies/Annual-Reports","web_page","searched, not used","annual reports list; no pre-2019 statements found"),
("Eurobodalla financial statements page","Eurobodalla Shire Council","https://www.esc.nsw.gov.au/council/plans-and-reporting/financial-statements","government_page","searched, not used","page returned HTTP 403 to fetch"),
("Eurobodalla performance reporting page","Eurobodalla Shire Council","https://www.esc.nsw.gov.au/council/plans-and-reporting/performance-reporting","government_page","searched, not used","page returned HTTP 403 to fetch"),
("Goulburn Mulwaree access to information page","Goulburn Mulwaree Council","https://www.goulburn.nsw.gov.au/Council/Access-to-Information","web_page","searched, not used","no finance links on page"),
("Goulburn Mulwaree finance corporate documents page (guessed path)","Goulburn Mulwaree Council","https://www.goulburn.nsw.gov.au/Council/Corporate-Documents/Finance","web_page","searched, not used","link failed 2026-10-02 (404)"),
("Cowra annual financial statements page (guessed path)","Cowra Shire Council","https://www.cowracouncil.com.au/council/governance-and-transparency/annual-financial-statements","web_page","searched, not used","link failed 2026-10-02 (404)"),
("Dungog annual reports index (guessed path)","Dungog Shire Council","https://www.dungog.nsw.gov.au/council/council-documents/annual-reports","web_page","searched, not used","link failed 2026-10-02 (404)")]
for t,p,u,st,used,what in pages:
    add(t,p,"",st,u,used=used,what=what,notes="link failed 2026-10-02" if "failed" in what else "")
# search-found PDFs not downloaded
extra=[("Eurobodalla GPFS 2015 (not in scope)","https://www.esc.nsw.gov.au/__data/assets/pdf_file/0007/143980/General-Purpose-Financial-Statements-for-2014-15.pdf"),
("Eurobodalla Annual Financial Statements 2023 alternative file","https://www.esc.nsw.gov.au/__data/assets/pdf_file/0008/241748/Annual-Financial-Statements-for-the-year-ended-30-June-2023.pdf"),
("Goulburn GPFS 2019 alternative file","https://www.goulburn.nsw.gov.au/files/sharedassets/public/v/1/agenda-items/annual_financial_statements-gpfs-2019.pdf"),
("Goulburn annual report 2019-20 (may contain statements)","https://www.goulburn.nsw.gov.au/files/sharedassets/public/v/1/annual-report/annual-report-2020.pdf"),
("Goulburn annual report 2020-21","https://www.goulburn.nsw.gov.au/files/sharedassets/public/v/1/operational-plan/202021/202122/v2annual-report-2020.pdf"),
("Glen Innes Severn annual report 2019-20","https://www.gisc.nsw.gov.au/files/assets/public/v/1/council/documents/public-documents-and-polices/annual-report-2019-2020.pdf")]
for t,u in extra: add(t,"council","","pdf_report",u,what="found in search; not downloaded (site blocks downloads or not needed)")
w=csv.writer(open("biblio.csv","w",newline=""));w.writerow(H);w.writerows(b)
print(len(rows),len(b),sum(1 for r in rows if r[3]=="downloaded"))
