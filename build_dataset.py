"""
build_dataset.py
----------------
Builds three CSV files in ./data from the tables published in:

  Pew Research Center, "Buying a home has gotten harder for young adults in
  most U.S. metro areas" (Richard Fry & Blen Wondimu, June 24, 2026)
  https://www.pewresearch.org/short-reads/2026/06/24/buying-a-home-has-gotten-harder-for-young-adults-in-most-us-metro-areas/

All figures are for households headed by adults UNDER 40.
Pew's source data: 2024 American Community Survey (IPUMS), the 1976-2025
Current Population Survey ASEC (IPUMS), and the OFHEO purchase-only price
index. National dollars are in 2024 dollars. Household income is size-adjusted
and scaled to a three-person household.

The values below were transcribed from Pew's published tables. If you want to
verify or refresh them, the same tables have "Download data as .csv" buttons
on the Pew page above.

Outputs (written next to this script, in ./data):
  national_price_income.csv   year, median_home_price, median_income_under40, price_to_income
  metro_price_income.csv      cbsa, metro, state, median_home_price, median_income_under40,
                              pew_ratio, ratio_calc, tier
  metro_tiers.csv             year, tier, pct_of_metros

Run:  python build_dataset.py
"""
import io
from pathlib import Path

import pandas as pd

BASE = Path(__file__).resolve().parent
DATA = BASE / "data"
DATA.mkdir(exist_ok=True)

# ---------------------------------------------------------------------------
# 1) National series: median home price vs. median income (under-40 households)
#    columns: year, median home price, median household income, price-to-income
# ---------------------------------------------------------------------------
NATIONAL = """
1975,154100,62900,2.5
1976,154800,64900,2.4
1977,161400,66300,2.4
1978,171600,69200,2.5
1979,176600,70200,2.5
1980,170700,67300,2.5
1981,164200,65400,2.5
1982,160100,65700,2.4
1983,159800,65000,2.5
1984,160500,68500,2.3
1985,165000,69300,2.4
1986,176000,71600,2.5
1987,183400,73600,2.5
1988,187800,74100,2.5
1989,189200,74700,2.5
1990,184300,72100,2.6
1991,178500,70300,2.5
1992,177800,69700,2.6
1993,176800,68200,2.6
1994,178300,68300,2.6
1995,178200,70700,2.5
1996,178300,71300,2.5
1997,179700,73000,2.5
1998,186800,75800,2.5
1999,194400,77800,2.5
2000,200500,79900,2.5
2001,209300,78900,2.7
2002,222500,78300,2.8
2003,234300,76300,3.1
2004,249600,75900,3.3
2005,265700,75700,3.5
2006,272700,76300,3.6
2007,265700,78100,3.4
2008,233600,75900,3.1
2009,221800,72400,3.1
2010,209700,70500,3.0
2011,192900,68300,2.8
2012,194200,69800,2.8
2013,205300,71200,2.9
2014,213000,72100,3.0
2015,226800,78000,2.9
2016,238800,83500,2.9
2017,249500,84600,2.9
2018,259500,87400,3.0
2019,269600,92700,2.9
2020,288800,92400,3.1
2021,318400,94200,3.4
2022,331000,92100,3.6
2023,337900,96000,3.5
2024,350000,100900,3.5
"""

# ---------------------------------------------------------------------------
# 2) Metro table, 2024 (160 metros): cbsa | metro | state | price | income | ratio
# ---------------------------------------------------------------------------
METROS = """
10420|Akron, OH|Ohio|230000|80000|2.9
10580|Albany-Schenectady-Troy, NY|New York|311000|106521|2.9
10740|Albuquerque, NM|New Mexico|300000|81406|3.7
10900|Allentown-Bethlehem-Easton, PA-NJ|Pennsylvania|310000|96995|3.2
11100|Amarillo, TX|Texas|250000|65000|3.8
11260|Anchorage, AK|Alaska|380000|96000|4.0
11460|Ann Arbor, MI|Michigan|350000|80000|4.4
11700|Asheville, NC|North Carolina|400000|84385|4.7
12060|Atlanta-Sandy Springs-Roswell, GA|Georgia|390000|102191|3.8
12100|Atlantic City-Hammonton, NJ|New Jersey|380000|99593|3.8
12260|Augusta-Richmond County, GA-SC|Georgia|295000|79674|3.7
12420|Austin-Round Rock-San Marcos, TX|Texas|450000|114640|3.9
12540|Bakersfield-Delano, CA|California|409000|72405|5.6
12580|Baltimore-Columbia-Towson, MD|Maryland|400000|111717|3.6
12940|Baton Rouge, LA|Louisiana|250000|71880|3.5
13140|Beaumont-Port Arthur, TX|Texas|200000|69282|2.9
13820|Birmingham, AL|Alabama|270000|86603|3.1
13980|Blacksburg-Christiansburg-Radford, VA|Virginia|280000|60013|4.7
14010|Bloomington, IL|Illinois|232000|67361|3.4
14260|Boise City, ID|Idaho|450000|94397|4.8
14460|Boston-Cambridge-Newton, MA-NH|Massachusetts|630000|147224|4.3
14740|Bremerton-Silverdale-Port Orchard, WA|Washington|580000|107979|5.4
14860|Bridgeport-Stamford-Danbury, CT|Connecticut|521000|129904|4.0
15180|Brownsville-Harlingen, TX|Texas|186000|53031|3.5
15380|Buffalo-Cheektowaga, NY|New York|250000|90067|2.8
15940|Canton-Massillon, OH|Ohio|200000|81406|2.5
15980|Cape Coral-Fort Myers, FL|Florida|400000|91799|4.4
16700|Charleston-North Charleston, SC|South Carolina|400000|103923|3.8
16740|Charlotte-Concord-Gastonia, NC-SC|North Carolina|380000|97980|3.9
16820|Charlottesville, VA|Virginia|425000|95040|4.5
16860|Chattanooga, TN-GA|Tennessee|300000|90933|3.3
16980|Chicago-Naperville-Elgin, IL-IN|Illinois|300000|107778|2.8
17020|Chico, CA|California|500000|56461|8.9
17140|Cincinnati, OH-KY-IN|Ohio|275000|93531|2.9
17300|Clarksville, TN-KY|Tennessee|300000|76210|3.9
17410|Cleveland, OH|Ohio|230000|90933|2.5
17780|College Station-Bryan, TX|Texas|315000|55000|5.7
17820|Colorado Springs, CO|Colorado|500000|98727|5.1
17900|Columbia, SC|South Carolina|290000|69282|4.2
18140|Columbus, OH|Ohio|312000|93081|3.4
18580|Corpus Christi, TX|Texas|240000|69975|3.4
19100|Dallas-Fort Worth-Arlington, TX|Texas|375000|100429|3.7
19430|Dayton-Kettering-Beavercreek, OH|Ohio|225000|79674|2.8
19660|Deltona-Daytona Beach-Ormond Beach, FL|Florida|360000|82272|4.4
19740|Denver-Aurora-Centennial, CO|Colorado|600000|129904|4.6
19780|Des Moines-West Des Moines, IA|Iowa|275000|98995|2.8
19820|Detroit-Warren-Dearborn, MI|Michigan|260000|90067|2.9
21340|El Paso, TX|Texas|220000|64952|3.4
21500|Erie, PA|Pennsylvania|210000|71014|3.0
21660|Eugene-Springfield, OR|Oregon|450000|78895|5.7
21780|Evansville, IN|Indiana|225000|79608|2.8
22180|Fayetteville, NC|North Carolina|255000|69282|3.7
22220|Fayetteville-Springdale-Rogers, AR|Arkansas|330000|80540|4.1
22660|Fort Collins-Loveland, CO|Colorado|575000|95263|6.0
23060|Fort Wayne, IN|Indiana|250000|76210|3.3
23420|Fresno, CA|California|455000|75934|6.0
24340|Grand Rapids-Wyoming-Kentwood, MI|Michigan|300000|93000|3.2
24660|Greensboro-High Point, NC|North Carolina|280000|69810|4.0
24860|Greenville-Anderson-Greer, SC|South Carolina|300000|90000|3.3
25420|Harrisburg-Carlisle, PA|Pennsylvania|290000|94000|3.1
25540|Hartford-West Hartford-East Hartford, CT|Connecticut|360000|112583|3.2
25860|Hickory-Lenoir-Morganton, NC|North Carolina|280000|80000|3.5
26420|Houston-Pasadena-The Woodlands, TX|Texas|320000|85855|3.7
26620|Huntsville, AL|Alabama|300000|98727|3.0
26900|Indianapolis-Carmel-Greenwood, IN|Indiana|280000|91243|3.1
27140|Jackson, MS|Mississippi|225000|73587|3.1
27260|Jacksonville, FL|Florida|400000|90067|4.4
28020|Kalamazoo-Portage, MI|Michigan|250000|75934|3.3
28140|Kansas City, MO-KS|Missouri|300000|93081|3.2
28880|Kiryas Joel-Poughkeepsie-Newburgh, NY|New York|425000|95263|4.5
28940|Knoxville, TN|Tennessee|350000|82303|4.3
29180|Lafayette, LA|Louisiana|250000|69000|3.6
29460|Lakeland-Winter Haven, FL|Florida|350000|76302|4.6
29540|Lancaster, PA|Pennsylvania|300000|95530|3.1
29620|Lansing-East Lansing, MI|Michigan|250000|83895|3.0
29820|Las Vegas-Henderson-North Las Vegas, NV|Nevada|450000|86603|5.2
30700|Lincoln, NE|Nebraska|275000|76179|3.6
30780|Little Rock-North Little Rock-Conway, AR|Arkansas|240000|70000|3.4
31080|Los Angeles-Long Beach-Anaheim, CA|California|850000|113137|7.5
31140|Louisville/Jefferson County, KY-IN|Kentucky|250000|85732|2.9
31180|Lubbock, TX|Texas|250000|59807|4.2
31340|Lynchburg, VA|Virginia|300000|84000|3.6
32580|McAllen-Edinburg-Mission, TX|Texas|200000|57563|3.5
32820|Memphis, TN-MS-AR|Tennessee|300000|73485|4.1
32900|Merced, CA|California|450000|60622|7.4
33100|Miami-Fort Lauderdale-West Palm Beach, FL|Florida|460000|92591|5.0
33340|Milwaukee-Waukesha, WI|Wisconsin|300000|95263|3.1
33460|Minneapolis-St. Paul-Bloomington, MN-WI|Minnesota|370000|113411|3.3
33660|Mobile, AL|Alabama|225000|68341|3.3
33700|Modesto, CA|California|500000|81813|6.1
33860|Montgomery, AL|Alabama|220000|66164|3.3
34980|Nashville-Davidson–Murfreesboro–Franklin, TN|Tennessee|400000|101654|3.9
35300|New Haven, CT|Connecticut|350000|105328|3.3
35380|New Orleans-Metairie, LA|Louisiana|250000|82272|3.0
35620|New York-Newark-Jersey City, NY-NJ|New York|600000|129904|4.6
35840|North Port-Bradenton-Sarasota, FL|Florida|450000|96755|4.7
35980|Norwich-New London-Willimantic, CT|Connecticut|350000|105181|3.3
36260|Ogden, UT|Utah|500000|91402|5.5
36420|Oklahoma City, OK|Oklahoma|250000|75000|3.3
36500|Olympia-Lacey-Tumwater, WA|Washington|538000|117346|4.6
36540|Omaha, NE-IA|Nebraska|270000|90067|3.0
36740|Orlando-Kissimmee-Sanford, FL|Florida|400000|88335|4.5
37100|Oxnard-Thousand Oaks-Ventura, CA|California|850000|120000|7.1
37340|Palm Bay-Melbourne-Titusville, FL|Florida|390000|92665|4.2
37860|Pensacola-Ferry Pass-Brent, FL|Florida|339000|81060|4.2
37980|Philadelphia-Camden-Wilmington, PA-NJ-DE-MD|Pennsylvania|350000|106207|3.3
38060|Phoenix-Mesa-Chandler, AZ|Arizona|450000|97000|4.6
38300|Pittsburgh, PA|Pennsylvania|250000|98727|2.5
38860|Portland-South Portland, ME|Maine|450000|109218|4.1
38900|Portland-Vancouver-Hillsboro, OR-WA|Oregon|550000|115861|4.7
39300|Providence-Warwick, RI-MA|Rhode Island|450000|103923|4.3
39340|Provo-Orem-Lehi, UT|Utah|550000|86949|6.3
39580|Raleigh-Cary, NC|North Carolina|450000|116351|3.9
39740|Reading, PA|Pennsylvania|289000|95275|3.0
39900|Reno, NV|Nevada|525000|95263|5.5
40060|Richmond, VA|Virginia|375000|95000|3.9
40140|Riverside-San Bernardino-Ontario, CA|California|600000|93081|6.4
40220|Roanoke, VA|Virginia|276000|89859|3.1
40380|Rochester, NY|New York|250000|94000|2.7
40420|Rockford, IL|Illinois|200000|71014|2.8
40900|Sacramento-Roseville-Folsom, CA|California|622000|103400|6.0
41180|St. Louis, MO-IL|Missouri|250000|93081|2.7
41500|Salinas, CA|California|760000|94918|8.0
41620|Salt Lake City-Murray, UT|Utah|525000|105000|5.0
41700|San Antonio-New Braunfels, TX|Texas|300000|80000|3.8
41740|San Diego-Chula Vista-Carlsbad, CA|California|875000|124924|7.0
41860|San Francisco-Oakland-Fremont, CA|California|1000000|173205|5.8
41940|San Jose-Sunnyvale-Santa Clara, CA|California|1300000|213106|6.1
42020|San Luis Obispo-Paso Robles, CA|California|829000|90400|9.2
42200|Santa Maria-Santa Barbara, CA|California|825000|86000|9.6
42220|Santa Rosa-Petaluma, CA|California|800000|122474|6.5
42540|Scranton–Wilkes-Barre, PA|Pennsylvania|225000|83190|2.7
42660|Seattle-Tacoma-Bellevue, WA|Washington|700000|140846|5.0
43900|Spartanburg, SC|South Carolina|280000|74478|3.8
44060|Spokane-Spokane Valley, WA|Washington|450000|90067|5.0
44100|Springfield, IL|Illinois|200000|85732|2.3
44140|Springfield, MA|Massachusetts|350000|90067|3.9
44180|Springfield, MO|Missouri|250000|77942|3.2
44700|Stockton-Lodi, CA|California|600000|94305|6.4
45060|Syracuse, NY|New York|225000|86256|2.6
45300|Tampa-St. Petersburg-Clearwater, FL|Florida|400000|93098|4.3
45780|Toledo, OH|Ohio|200000|72746|2.7
45820|Topeka, KS|Kansas|212000|76000|2.8
45940|Trenton-Princeton, NJ|New Jersey|425000|111800|3.8
46060|Tucson, AZ|Arizona|385000|77942|4.9
46140|Tulsa, OK|Oklahoma|245000|77782|3.1
46520|Urban Honolulu, HI|Hawaii|900000|102879|8.7
46540|Utica-Rome, NY|New York|210000|88335|2.4
46700|Vallejo, CA|California|650000|109119|6.0
47260|Virginia Beach-Chesapeake-Norfolk, VA-NC|Virginia|360000|88182|4.1
47300|Visalia, CA|California|400000|68200|5.9
47380|Waco, TX|Texas|280000|69282|4.0
47900|Washington-Arlington-Alexandria, DC-VA-MD-WV|Virginia|550000|139430|3.9
48620|Wichita, KS|Kansas|225000|74478|3.0
48900|Wilmington, NC|North Carolina|388000|94305|4.1
49180|Winston-Salem, NC|North Carolina|280000|72746|3.8
49340|Worcester, MA|Massachusetts|500000|108444|4.6
49420|Yakima, WA|Washington|385000|62873|6.1
49620|York-Hanover, PA|Pennsylvania|280000|98727|2.8
49660|Youngstown-Warren, OH|Ohio|180000|69628|2.6
"""

# Share of the 160 metros in each affordability tier (percent), from Pew's chart.
# Tiers use the median home price / median under-40 household income ratio.
TIER_ORDER = [
    "Very affordable",        # ratio < 2.5
    "Somewhat affordable",    # 2.5 <= ratio < 3.5
    "Somewhat unaffordable",  # 3.5 <= ratio < 5
    "Very unaffordable",      # ratio >= 5
]
TIER_SHARES = {
    2019: [14, 46, 27, 14],
    2024: [2, 38, 41, 19],
}


def tier_for(ratio: float) -> str:
    if ratio < 2.5:
        return TIER_ORDER[0]
    if ratio < 3.5:
        return TIER_ORDER[1]
    if ratio < 5.0:
        return TIER_ORDER[2]
    return TIER_ORDER[3]


def main() -> None:
    # --- national ---
    national = pd.read_csv(
        io.StringIO(NATIONAL.strip()),
        header=None,
        names=["year", "median_home_price", "median_income_under40", "price_to_income"],
    )
    national.to_csv(DATA / "national_price_income.csv", index=False)

    # --- metros ---
    metros = pd.read_csv(
        io.StringIO(METROS.strip()),
        sep="|",
        header=None,
        names=["cbsa", "metro", "state", "median_home_price",
               "median_income_under40", "pew_ratio"],
    )
    # Pew publishes the ratio rounded to 1 decimal; recompute from the medians
    # so tiers aren't distorted by rounding.
    metros["ratio_calc"] = (
        metros["median_home_price"] / metros["median_income_under40"]
    ).round(2)
    metros["tier"] = metros["ratio_calc"].apply(tier_for)
    metros.to_csv(DATA / "metro_price_income.csv", index=False)

    # --- tiers ---
    rows = []
    for year, shares in TIER_SHARES.items():
        for tier, pct in zip(TIER_ORDER, shares):
            rows.append({"year": year, "tier": tier, "pct_of_metros": pct})
    pd.DataFrame(rows).to_csv(DATA / "metro_tiers.csv", index=False)

    # --- sanity checks ---
    print(f"national rows: {len(national)} (expect 50, 1975-2024)")
    print(f"metro rows:    {len(metros)} (expect 160)")
    counts = (metros["tier"].value_counts(normalize=True) * 100).round(0)
    print("\n2024 tier shares recomputed from medians (Pew chart: 2 / 38 / 41 / 19):")
    print(counts.reindex(TIER_ORDER).to_string())
    print(f"\nCSV files written to {DATA}")


if __name__ == "__main__":
    main()
