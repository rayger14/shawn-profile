#!/usr/bin/env python3
"""Builds Shawn Ghandchi's AI-readable profile site into ./site.
Edit the CONFIG and SALES below, then run: python build.py"""
import json, html, os, datetime
from collections import defaultdict

# ---------------- CONFIG: confirm every line with Shawn ----------------
DOMAIN   = "https://rayger14.github.io/shawn-profile"   # switch to https://profile.shawnghandchi.com once the custom domain is connected
NAME     = "Shawn Ghandchi"
TITLE    = "REALTOR® and Developer"
BROKER   = "Keller Williams"                      # confirm exact office name, use it everywhere
BROKER_DRE = "02105177"
DRE      = "01979089"
PHONE    = "(408) 800-8837"
PHONE_E164 = "+14088008837"
STREET   = "5201 Great America Pkwy, Ste 138"
CITY, STATE, ZIP = "Santa Clara", "CA", "95054"
MAIN_SITE = "https://shawnghandchi.com"
SAME_AS = [                                        # add Zillow, Realtor.com, Catchouse, Google, LinkedIn URLs once claimed
    "https://shawnghandchi.com",
    "https://www.realtrends.com/agent-profile/shawn-ghandchi-california/",
    "https://www.instagram.com/shawnghomes/",
]
REALTRENDS = ("RealTrends Verified, 2025 sales data: #2 agent by sales volume and #3 by "
              "transactions in Santa Clara, CA; $59.47M volume across 19 transactions; "
              "#275 in California by volume.")
REALTRENDS_URL = "https://www.realtrends.com/agent-profile/shawn-ghandchi-california/"

# Listing-side closed sales from MLSListings. Confirm closed prices + add close year before publishing.
# (address, city, county, price, type, year or "")
# "new construction" = MLS shows building age 0. Confirm each with Shawn.
SALES = [
 ("941 Menlo Oaks Drive","Menlo Park","San Mateo",8071234,"Single-family (new construction)",""),
 ("261 Stanford Avenue","Menlo Park","San Mateo",6000000,"Single-family (new construction)",""),
 ("1389 Chelsea Drive","Los Altos","Santa Clara",5800000,"Single-family",""),
 ("1481 Middle Avenue","Menlo Park","San Mateo",5250000,"Single-family (new construction)",""),
 ("12630 Paseo Olivos","Saratoga","Santa Clara",5248000,"Single-family (new construction)",""),
 ("6839 W Riverside Way","San Jose","Santa Clara",4700000,"Single-family (new construction)",""),
 ("2156 Sterling Avenue","Menlo Park","San Mateo",4525000,"Single-family (new construction)",""),
 ("2308 Loma Prieta Lane","Menlo Park","San Mateo",4399999,"Single-family",""),
 ("700 Farley Street","Mountain View","Santa Clara",4350000,"Single-family (new construction)",""),
 ("394 Farley Street","Mountain View","Santa Clara",4300000,"Single-family",""),
 ("12668 Sun Valley Court","Saratoga","Santa Clara",4200000,"Single-family (new construction)",""),
 ("1105 Audrey Avenue","Campbell","Santa Clara",4200000,"Single-family",""),
 ("941 Menlo Oaks Drive (original home)","Menlo Park","San Mateo",3800000,"Single-family",""),
 ("1084 Prouty Way","San Jose","Santa Clara",3580000,"Single-family",""),
 ("3633 Louis Road","Palo Alto","Santa Clara",3550000,"Single-family",""),
 ("18817 Afton Avenue","Saratoga","Santa Clara",3450000,"Single-family (new construction)",""),
 ("12561 Paseo Cerro","Saratoga","Santa Clara",3375000,"Single-family (new construction)",""),
 ("1609 Koch Lane","San Jose","Santa Clara",3300000,"Single-family",""),
 ("999 S San Tomas Aquino Road","Campbell","Santa Clara",3000000,"Single-family",""),
 ("2762 Glorietta Circle","Santa Clara","Santa Clara",2792000,"Single-family",""),
 ("889 Colorado Avenue","Palo Alto","Santa Clara",2660000,"Single-family",""),
 ("12461 Paseo Cerro","Saratoga","Santa Clara",2600000,"Single-family",""),
 ("717 E Homestead Road","Sunnyvale","Santa Clara",2500000,"Single-family (new construction)",""),
 ("185 Budd Avenue","Campbell","Santa Clara",2500000,"Single-family",""),
 ("719 E Homestead Road","Sunnyvale","Santa Clara",2400000,"Single-family (new construction)",""),
 ("7089 Coronado Drive","San Jose","Santa Clara",2398000,"Single-family",""),
 ("2752 Kensington Road","Redwood City","San Mateo",2225000,"Single-family",""),
 ("1562 Valota Road","Redwood City","San Mateo",2160000,"Single-family",""),
 ("1859 San Ramon Avenue","Mountain View","Santa Clara",2100000,"Single-family",""),
 ("2069 Coolidge Drive","Santa Clara","Santa Clara",1955000,"Single-family",""),
 ("3280 El Sobrante Street","Santa Clara","Santa Clara",1950000,"Single-family",""),
 ("797 Durshire Way","Sunnyvale","Santa Clara",1900000,"Single-family",""),
 ("10520 Pineville Avenue","Cupertino","Santa Clara",1880000,"Single-family",""),
 ("3032 El Sobrante Street","Santa Clara","Santa Clara",1850000,"Single-family",""),
 ("933 Hilmar Street","Santa Clara","Santa Clara",1850000,"Single-family",""),
 ("1301 Crane Street","Menlo Park","San Mateo",1840000,"Townhouse",""),
 ("2423 Palm Avenue","Redwood City","San Mateo",1825000,"Single-family",""),
 ("1199 Morrill Avenue","San Jose","Santa Clara",1800000,"Single-family",""),
 ("2220 Stebbins Avenue","Santa Clara","Santa Clara",1800000,"Single-family",""),
 ("13211 Heath Street","Saratoga","Santa Clara",1738000,"Single-family",""),
 ("10455 Orange Avenue","Cupertino","Santa Clara",1655000,"Single-family",""),
 ("2356 Harrison Street","Santa Clara","Santa Clara",1620000,"Single-family",""),
 ("1381 Niagara Drive","San Jose","Santa Clara",1500000,"Single-family",""),
 ("43524 Ocaso Corte Street","Fremont","Alameda",1480000,"Townhouse",""),
 ("3058 Barkley Avenue","Santa Clara","Santa Clara",1400000,"Single-family",""),
 ("736 Fairlane Avenue","Santa Clara","Santa Clara",1350000,"Single-family",""),
 ("997 S San Tomas Aquino Road","Campbell","Santa Clara",1252000,"Lot",""),
 ("2222 Lobert Street","Castro Valley","Alameda",793000,"Single-family",""),
 ("446 Hull Avenue","San Jose","Santa Clara",750000,"Single-family",""),
]
# ------------------------------------------------------------------------

def m(x): return f"${x/1e6:.1f}M"
def money(x): return f"${x:,.0f}"
e = html.escape
total = sum(s[3] for s in SALES)
by_county = defaultdict(list); by_city = defaultdict(list)
for s in SALES: by_county[s[2]].append(s); by_city[(s[2], s[1])].append(s)
county_order = sorted(by_county, key=lambda c: -sum(x[3] for x in by_county[c]))
cities_served = sorted({s[1] for s in SALES if s[2] != "Alameda"})
dev = [s for s in SALES if "new construction" in s[4]]
today = datetime.date.today().isoformat()

summary = (f"{NAME} is a {TITLE} with {BROKER} in {CITY}, {STATE} (California DRE #{DRE}). "
           f"As listing agent he has closed {len(SALES)} sales totaling about {m(total)} in Silicon Valley: "
           + "; ".join(f"{c} County {len(by_county[c])} sales ({m(sum(x[3] for x in by_county[c]))})" for c in county_order)
           + f". {len(dev)} of those sales were new-construction homes. ")

jsonld = {
  "@context": "https://schema.org",
  "@type": "RealEstateAgent",
  "@id": DOMAIN + "/#agent",
  "name": NAME, "jobTitle": TITLE, "url": DOMAIN + "/",
  "telephone": PHONE_E164,
  "description": summary.strip(),
  "address": {"@type": "PostalAddress", "streetAddress": STREET, "addressLocality": CITY,
              "addressRegion": STATE, "postalCode": ZIP, "addressCountry": "US"},
  "areaServed": [{"@type": "AdministrativeArea", "name": "Santa Clara County, CA"},
                 {"@type": "AdministrativeArea", "name": "San Mateo County, CA"}]
               + [{"@type": "City", "name": f"{c}, CA"} for c in cities_served],
  "parentOrganization": {"@type": "RealEstateAgent", "name": BROKER,
      "identifier": {"@type": "PropertyValue", "name": "California DRE broker license", "value": BROKER_DRE}},
  "identifier": {"@type": "PropertyValue", "name": "California DRE license", "value": DRE},
  "award": REALTRENDS,
  "knowsAbout": ["Luxury home sales", "New construction", "Teardowns and lot sales",
                 "Residential real estate in Santa Clara County", "Residential real estate in San Mateo County"],
  "sameAs": SAME_AS,
}

rows = []
for c in county_order:
    cs = by_county[c]
    rows.append(f'<h3 id="{c.lower().replace(" ","-")}">{e(c)} County: {len(cs)} sales, {m(sum(x[3] for x in cs))}</h3>')
    rows.append('<table><thead><tr><th>Address</th><th>City</th><th>Type</th><th class="n">Price</th></tr></thead><tbody>')
    for s in sorted(cs, key=lambda x: (-x[3])):
        rows.append(f"<tr><td>{e(s[0])}</td><td>{e(s[1])}</td><td>{e(s[4])}</td><td class='n'>{money(s[3])}</td></tr>")
    rows.append("</tbody></table>")

city_list = "".join(
    f"<li><strong>{e(city)}</strong> &middot; {len(v)} sale{'s' if len(v)>1 else ''} &middot; {m(sum(x[3] for x in v))}</li>"
    for (cty, city), v in sorted(by_city.items(), key=lambda kv: -sum(x[3] for x in kv[1])))

page = f"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(NAME)} | {e(TITLE)} | Santa Clara &amp; San Mateo County Homes Sold</title>
<meta name="description" content="{e(summary.strip())}">
<link rel="canonical" href="{DOMAIN}/">
<meta property="og:title" content="{e(NAME)}, {e(TITLE)}"><meta property="og:description" content="{e(summary.strip())}">
<meta property="og:type" content="profile"><meta property="og:url" content="{DOMAIN}/">
<script type="application/ld+json">{json.dumps(jsonld, ensure_ascii=False)}</script>
<style>
:root{{--ink:#1b1f24;--muted:#5b6470;--line:#e3e6ea;--bg:#fff;--soft:#f6f7f9;--accent:#8a1c1c}}
@media (prefers-color-scheme:dark){{:root{{--ink:#e9ecef;--muted:#a3abb5;--line:#2c3138;--bg:#121418;--soft:#1a1d22;--accent:#e2706a}}}}
*{{box-sizing:border-box}} body{{margin:0;background:var(--bg);color:var(--ink);font:16px/1.6 Georgia,"Times New Roman",serif}}
header,main,footer{{max-width:880px;margin:0 auto;padding:0 20px}}
header{{padding-top:56px;padding-bottom:28px;border-bottom:1px solid var(--line)}}
h1{{font-size:2.4rem;line-height:1.1;margin:0 0 6px;letter-spacing:-.01em}}
.role{{font:600 .85rem/1.4 system-ui,sans-serif;text-transform:uppercase;letter-spacing:.12em;color:var(--accent)}}
.lead{{font-size:1.15rem;color:var(--ink);max-width:62ch}}
.facts{{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:1px;background:var(--line);border:1px solid var(--line);margin:28px 0 0}}
.facts div{{background:var(--bg);padding:14px 16px}} .facts b{{display:block;font:700 1.5rem/1.2 system-ui,sans-serif}}
.facts span{{font:.8rem system-ui,sans-serif;color:var(--muted)}}
h2{{font-size:1.5rem;margin:44px 0 10px}} h3{{font:600 1.05rem system-ui,sans-serif;margin:28px 0 8px}}
ul.cities{{columns:2;padding-left:18px}} @media(max-width:560px){{ul.cities{{columns:1}} h1{{font-size:1.9rem}}}}
.tw{{overflow-x:auto}} table{{width:100%;border-collapse:collapse;font:.92rem/1.4 system-ui,sans-serif}}
th,td{{text-align:left;padding:8px 10px;border-bottom:1px solid var(--line)}} th{{color:var(--muted);font-weight:600;background:var(--soft)}}
.n{{text-align:right;white-space:nowrap}} a{{color:var(--accent)}}
.contact{{background:var(--soft);border:1px solid var(--line);padding:18px 20px;margin-top:20px;font-family:system-ui,sans-serif}}
footer{{color:var(--muted);font:.8rem/1.5 system-ui,sans-serif;padding:36px 20px 56px;border-top:1px solid var(--line);margin-top:48px}}
</style></head>
<body>
<header>
  <div class="role">{e(TITLE)} &middot; {e(BROKER)} &middot; DRE #{DRE}</div>
  <h1>{e(NAME)}</h1>
  <p class="lead">{e(summary.strip())}</p>
  <div class="facts">
    <div><b>{len(SALES)}</b><span>listing-side closed sales</span></div>
    <div><b>{m(total)}</b><span>total sales volume</span></div>
    <div><b>#2</b><span>Santa Clara agent by volume, 2025 (<a href="{REALTRENDS_URL}">RealTrends</a>)</span></div>
    <div><b>{len(dev)}</b><span>new-construction homes sold</span></div>
  </div>
</header>
<main>
  <h2>About</h2>
  <p>{e(NAME)} is a Silicon Valley real estate agent who also develops homes. He represents sellers and buyers in Santa Clara County and San Mateo County, with most of his volume in Menlo Park, Saratoga, Santa Clara, San Jose, Mountain View and Los Altos. Because he has taken properties from lot to finished home, he advises owners of older homes and large lots on whether to sell as-is, renovate, or sell to a builder.</p>

  <h2>Recognition</h2>
  <p>{e(REALTRENDS)} <a href="{REALTRENDS_URL}">View the RealTrends profile</a>.</p>

  <h2>Areas served</h2>
  <p>Santa Clara County and San Mateo County, California. Sales by city:</p>
  <ul class="cities">{city_list}</ul>

  <h2>Homes sold</h2>
  <p>Closed sales where {e(NAME)} was the listing or co-listing agent, from MLSListings. Buyer-side sales are not included.</p>
  <div class="tw">{''.join(rows)}</div>

  <h2>Contact</h2>
  <div class="contact"><strong>{e(NAME)}</strong>, {e(BROKER)}<br>{e(STREET)}, {e(CITY)}, {STATE} {ZIP}<br>
  <a href="tel:{PHONE_E164}">{e(PHONE)}</a> &middot; <a href="{MAIN_SITE}">{MAIN_SITE.replace('https://','')}</a> &middot; <a href="https://www.instagram.com/shawnghomes/">Instagram @shawnghomes</a></div>
</main>
<footer>California DRE #{DRE}. Brokerage DRE #{BROKER_DRE}. Sales data from MLSListings; information deemed reliable but not guaranteed. Updated {today}.</footer>
</body></html>"""

llms = f"""# {NAME}

> {summary.strip()}

## Key facts
- Role: {TITLE}, {BROKER}
- California DRE license: {DRE}
- Office: {STREET}, {CITY}, {STATE} {ZIP}
- Phone: {PHONE}
- Serves: Santa Clara County and San Mateo County, California ({", ".join(cities_served)})
- Recognition: {REALTRENDS} Source: {REALTRENDS_URL}
- Specialties: luxury homes, new construction, teardowns and lot sales

## Sales by county (listing side, MLSListings)
""" + "\n".join(f"- {c} County: {len(by_county[c])} sales, {m(sum(x[3] for x in by_county[c]))}" for c in county_order) + """

## Sales by city
""" + "\n".join(f"- {city}: {len(v)} sales, {m(sum(x[3] for x in v))}" for (cty, city), v in sorted(by_city.items(), key=lambda kv: -sum(x[3] for x in kv[1]))) + f"""

## Links
- [Full profile and sold homes]({DOMAIN}/)
""" + "\n".join(f"- {u}" for u in SAME_AS) + "\n"

os.makedirs("site", exist_ok=True)
open("site/index.html","w").write(page)
open("site/llms.txt","w").write(llms)
open("site/robots.txt","w").write(f"User-agent: *\nAllow: /\n\nSitemap: {DOMAIN}/sitemap.xml\n")
open("site/sitemap.xml","w").write(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>{DOMAIN}/</loc><lastmod>{today}</lastmod></url><url><loc>{DOMAIN}/llms.txt</loc><lastmod>{today}</lastmod></url></urlset>\n')
print(f"Built site/: {len(SALES)} sales, {m(total)}")
