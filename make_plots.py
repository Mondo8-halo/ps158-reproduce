"""
make_plots.py
-------------
Reads the CSVs created by build_dataset.py and saves three figures to ./figures,
focused on the relationship between young adults' incomes and home prices.

  fig1_price_vs_income_national.png   home price vs. income over time + price-to-income ratio
  fig2_metro_income_vs_price.png      2024 metro scatter: income (x) vs. home price (y)
  fig3_metro_extremes.png             10 least and 10 most affordable metros (price-to-income)

Data: Pew Research Center (June 24, 2026), households headed by adults under 40.

Run:
    python build_dataset.py
    python make_plots.py
"""
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import pandas as pd

BASE = Path(__file__).resolve().parent
DATA = BASE / "data"
FIGS = BASE / "figures"
FIGS.mkdir(exist_ok=True)

SOURCE = ("Source: Pew Research Center analysis of ACS and CPS-ASEC (IPUMS); "
          "households headed by adults under 40")

PRICE_COLOR = "#c0392b"
INCOME_COLOR = "#1f6fb2"
TIER_COLORS = {
    "Very affordable": "#2e8b57",
    "Somewhat affordable": "#9acd32",
    "Somewhat unaffordable": "#f5a623",
    "Very unaffordable": "#c0392b",
}

plt.rcParams.update({
    "figure.dpi": 130,
    "savefig.dpi": 200,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.alpha": 0.25,
    "font.size": 10,
})


def dollars(x, _pos=None):
    return f"${x:,.0f}"


def dollars_k(x, _pos=None):
    return "$0" if x == 0 else f"${x / 1000:,.0f}k"


# ---------------------------------------------------------------------------
# Figure 1: national price vs. income, and the ratio
# ---------------------------------------------------------------------------
def fig_national() -> None:
    df = pd.read_csv(DATA / "national_price_income.csv")
    fig, (ax1, ax2) = plt.subplots(
        2, 1, figsize=(10, 8.5), sharex=True,
        gridspec_kw={"height_ratios": [2, 1.3], "hspace": 0.12},
    )

    # Top: price and income in 2024 dollars
    ax1.plot(df["year"], df["median_home_price"], color=PRICE_COLOR, lw=2.4,
             label="Median home price")
    ax1.plot(df["year"], df["median_income_under40"], color=INCOME_COLOR, lw=2.4,
             label="Median household income (under 40)")
    ax1.axvspan(2019, 2024, color="grey", alpha=0.10)
    ax1.yaxis.set_major_formatter(mtick.FuncFormatter(dollars_k))
    ax1.set_ylabel("2024 dollars")
    ax1.set_title("Home prices have outrun young adults' incomes",
                  loc="left", fontsize=14, fontweight="bold")
    ax1.legend(loc="upper left", frameon=False, bbox_to_anchor=(0, 1.0))

    r = df.set_index("year")
    ax1.set_ylim(0, 385000)
    # (year, price label offset, income label offset, horizontal alignment)
    for yr, po, io_, ha in [(1975, (0, -16), (0, -16), "left"),
                            (2019, (-8, 4), (-4, -16), "right"),
                            (2024, (-2, 8), (-2, -16), "right")]:
        p, i = r.loc[yr, "median_home_price"], r.loc[yr, "median_income_under40"]
        ax1.annotate(dollars(p), (yr, p), textcoords="offset points",
                     xytext=po, ha=ha, color=PRICE_COLOR, fontsize=9)
        ax1.annotate(dollars(i), (yr, i), textcoords="offset points",
                     xytext=io_, ha=ha, color=INCOME_COLOR, fontsize=9)

    p19, p24 = r.loc[2019, "median_home_price"], r.loc[2024, "median_home_price"]
    i19, i24 = r.loc[2019, "median_income_under40"], r.loc[2024, "median_income_under40"]
    ax1.text(1976, 265000,
             f"2019 to 2024\nHome price: {p24 / p19 - 1:+.0%}\nIncome: {i24 / i19 - 1:+.0%}",
             fontsize=10, bbox=dict(boxstyle="round", fc="white", ec="#bbbbbb"))

    # Bottom: price-to-income ratio
    ax2.plot(df["year"], df["price_to_income"], color="#333333", lw=2.2)
    ax2.axhline(2.5, color="grey", ls="--", lw=1)
    ax2.text(1975.3, 2.53, "about 2.5 before 2000", fontsize=8.5, color="grey", va="bottom")
    ax2.axvspan(2019, 2024, color="grey", alpha=0.10)
    ax2.set_ylim(2.0, 4.0)
    ax2.set_ylabel("Price-to-income ratio")
    ax2.set_xlabel("Year")

    ratio = r["price_to_income"]
    peak_year = int(ratio.loc[:2010].idxmax())
    ax2.annotate(f"{ratio.loc[peak_year]:.1f} ({peak_year} peak)",
                 (peak_year, ratio.loc[peak_year]), textcoords="offset points",
                 xytext=(-10, 8), ha="right", fontsize=9)
    ax2.annotate(f"{ratio.loc[2019]:.1f}", (2019, ratio.loc[2019]),
                 textcoords="offset points", xytext=(-4, -14), ha="right", fontsize=9)
    ax2.annotate(f"{ratio.loc[2024]:.1f}", (2024, ratio.loc[2024]),
                 textcoords="offset points", xytext=(0, 8), ha="center", fontsize=9)

    fig.text(0.01, 0.005, SOURCE, fontsize=8, color="#555555")
    fig.savefig(FIGS / "fig1_price_vs_income_national.png", bbox_inches="tight")
    plt.close(fig)


# ---------------------------------------------------------------------------
# Figure 2: metro scatter of income vs. home price with ratio guide lines
# ---------------------------------------------------------------------------
LABELS = {
    "Santa Maria-Santa Barbara, CA": "Santa Maria-Santa Barbara",
    "San Luis Obispo-Paso Robles, CA": "San Luis Obispo",
    "Chico, CA": "Chico",
    "Urban Honolulu, HI": "Honolulu",
    "Los Angeles-Long Beach-Anaheim, CA": "Los Angeles",
    "San Francisco-Oakland-Fremont, CA": "San Francisco",
    "San Jose-Sunnyvale-Santa Clara, CA": "San Jose",
    "Seattle-Tacoma-Bellevue, WA": "Seattle",
    "New York-Newark-Jersey City, NY-NJ": "New York",
    "Boston-Cambridge-Newton, MA-NH": "Boston",
    "Denver-Aurora-Centennial, CO": "Denver",
    "Austin-Round Rock-San Marcos, TX": "Austin",
    "Chicago-Naperville-Elgin, IL-IN": "Chicago",
    "Pittsburgh, PA": "Pittsburgh",
    "Cleveland, OH": "Cleveland",
    "Springfield, IL": "Springfield, IL",
}


def fig_metro_scatter() -> None:
    df = pd.read_csv(DATA / "metro_price_income.csv")
    fig, ax = plt.subplots(figsize=(10, 7.5))

    # Guide lines: price = k * income, using Pew's tier cut-offs
    x_max = 230000
    for k, txt in [(2.5, "2.5x income"), (3.5, "3.5x"), (5.0, "5x")]:
        ax.plot([0, x_max], [0, k * x_max], color="grey", ls="--", lw=1, zorder=1)
        ax.text(x_max * 0.995, k * x_max * 0.995, txt, ha="right", va="bottom",
                color="grey", fontsize=8.5, rotation=0)

    for tier, color in TIER_COLORS.items():
        sub = df[df["tier"] == tier]
        ax.scatter(sub["median_income_under40"], sub["median_home_price"],
                   s=38, color=color, alpha=0.85, edgecolor="white", lw=0.5,
                   label=f"{tier} ({len(sub)})", zorder=3)

    offsets = {  # small manual nudges so labels do not collide
        "San Francisco": (-6, 6), "San Jose": (-6, -12), "Seattle": (6, -4),
        "Los Angeles": (6, 2), "New York": (6, -10), "Boston": (6, 4),
        "Denver": (6, 2), "Austin": (6, -4), "Chicago": (8, 8),
        "Santa Maria-Santa Barbara": (-6, 7), "San Luis Obispo": (8, -3),
        "Chico": (6, 0), "Honolulu": (6, 2),
        "Pittsburgh": (10, 14), "Cleveland": (-8, 10), "Springfield, IL": (6, -14),
    }
    for full, short in LABELS.items():
        row = df[df["metro"] == full]
        if row.empty:
            continue
        x, y = row["median_income_under40"].iloc[0], row["median_home_price"].iloc[0]
        dx, dy = offsets.get(short, (6, 3))
        ha = "right" if dx < 0 else "left"
        ax.annotate(short, (x, y), textcoords="offset points", xytext=(dx, dy),
                    ha=ha, fontsize=8.5, zorder=4)

    ax.set_xlim(40000, x_max)
    ax.set_ylim(100000, 1350000)
    ax.xaxis.set_major_formatter(mtick.FuncFormatter(dollars_k))
    ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda v, p: f"${v / 1e6:.1f}M"
                                                     if v >= 1e6 else f"${v / 1000:,.0f}k"))
    ax.set_xlabel("Median household income, under-40 households")
    ax.set_ylabel("Median home price")
    ax.set_title("Where young adults' incomes cover the price of a home (2024)",
                 loc="left", fontsize=14, fontweight="bold")
    ax.legend(title="Affordability (price-to-income)", loc="upper left", frameon=False)
    fig.text(0.01, 0.005,
             SOURCE + " | 160 metros | dashed lines = price-to-income ratio of 2.5, 3.5, 5",
             fontsize=8, color="#555555")
    fig.savefig(FIGS / "fig2_metro_income_vs_price.png", bbox_inches="tight")
    plt.close(fig)


# ---------------------------------------------------------------------------
# Figure 3: 10 least and 10 most affordable metros
# ---------------------------------------------------------------------------
def fig_metro_extremes() -> None:
    df = pd.read_csv(DATA / "metro_price_income.csv")
    df["short"] = df["metro"].str.replace(r",\s[A-Z\-]+$", "", regex=True)
    df["label"] = df["short"].str.slice(0, 30) + ", " + df["metro"].str.extract(r",\s([A-Z\-]+)$")[0]

    worst = df.nlargest(10, "ratio_calc").sort_values("ratio_calc")
    best = df.nsmallest(10, "ratio_calc").sort_values("ratio_calc", ascending=False)

    fig, (axl, axr) = plt.subplots(1, 2, figsize=(12, 6), sharex=True)
    for ax, sub, color, title in [
        (axl, best, TIER_COLORS["Very affordable"], "10 most affordable"),
        (axr, worst, TIER_COLORS["Very unaffordable"], "10 least affordable"),
    ]:
        ax.barh(sub["label"], sub["ratio_calc"], color=color)
        for y, (v, pew, p, i) in enumerate(zip(sub["ratio_calc"], sub["pew_ratio"],
                                               sub["median_home_price"],
                                               sub["median_income_under40"])):
            # escape "$" so matplotlib does not treat paired dollar signs as math text
            ax.text(v + 0.1, y,
                    f"{pew:.1f}  ({dollars_k(p)} / {dollars_k(i)})".replace("$", r"\$"),
                    va="center", fontsize=8)
        ax.set_title(title, loc="left", fontweight="bold")
        ax.set_xlabel("Median home price / median income")
        ax.grid(axis="y", alpha=0)
    axl.set_xlim(0, 13)
    fig.suptitle("Price-to-income ratio by metro, 2024 (home price / income shown in parentheses)",
                 x=0.01, ha="left", fontsize=13, fontweight="bold")
    fig.text(0.01, 0.005, SOURCE, fontsize=8, color="#555555")
    fig.tight_layout(rect=(0, 0.02, 1, 0.95))
    fig.savefig(FIGS / "fig3_metro_extremes.png", bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    if not (DATA / "national_price_income.csv").exists():
        raise SystemExit("Missing data/ files. Run `python build_dataset.py` first.")
    fig_national()
    fig_metro_scatter()
    fig_metro_extremes()
    print(f"Saved figures to {FIGS}")


if __name__ == "__main__":
    main()
