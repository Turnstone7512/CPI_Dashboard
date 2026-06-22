import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.widgets import RadioButtons, Button
from datetime import datetime, timedelta

CPI_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=CPIAUCSL"
TENY_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=DGS10"

PERIODS = {
    "1Y": 1,
    "3Y": 3,
    "5Y": 5,
    "10Y": 10,
    "20Y": 20,
    "50Y": 50,
    "100Y": 100
}

cpi = pd.read_csv(CPI_URL)
teny = pd.read_csv(TENY_URL)

cpi["observation_date"] = pd.to_datetime(cpi["observation_date"])
teny["observation_date"] = pd.to_datetime(teny["observation_date"])

cpi["CPI"] = pd.to_numeric(cpi["CPIAUCSL"], errors="coerce")
cpi["CPI_YoY"] = cpi["CPI"].pct_change(12) * 100

teny["10Y"] = pd.to_numeric(teny["DGS10"], errors="coerce")

cpi = cpi[["observation_date", "CPI_YoY"]].dropna()
teny = teny[["observation_date", "10Y"]].dropna()

current_years = 1

fig = plt.figure(figsize=(18, 9))

ax_chart = fig.add_axes([0.20, 0.43, 0.55, 0.47])
ax_spread = fig.add_axes([0.20, 0.12, 0.55, 0.22])
ax_info = fig.add_axes([0.78, 0.12, 0.20, 0.78])
ax_info.axis("off")

radio_ax = fig.add_axes([0.03, 0.42, 0.12, 0.35])
button_ax = fig.add_axes([0.03, 0.28, 0.12, 0.06])

radio = RadioButtons(
    radio_ax,
    ("1Y", "3Y", "5Y", "10Y", "20Y", "50Y", "100Y")
)

save_button = Button(button_ax, "Save PNG")


def draw_chart(years):
    global current_years
    current_years = years

    ax_chart.clear()
    ax_spread.clear()
    ax_info.clear()
    ax_info.axis("off")

    end_date = datetime.today()
    start_date = end_date - timedelta(days=365 * years)

    cpi_filtered = cpi[cpi["observation_date"] >= start_date]
    teny_filtered = teny[teny["observation_date"] >= start_date]

    df = pd.merge_asof(
        teny_filtered.sort_values("observation_date"),
        cpi_filtered.sort_values("observation_date"),
        on="observation_date",
        direction="backward"
    ).dropna()

    if df.empty:
        ax_chart.set_title("No data available for this period")
        fig.canvas.draw_idle()
        return

    df["Spread"] = df["10Y"] - df["CPI_YoY"]

    latest = df.iloc[-1]
    latest_date = latest["observation_date"].strftime("%Y-%m-%d")
    latest_cpi = latest["CPI_YoY"]
    latest_10y = latest["10Y"]
    latest_spread = latest["Spread"]

    cpi_higher_days = (df["CPI_YoY"] > df["10Y"]).sum()
    ten_y_higher_days = (df["CPI_YoY"] < df["10Y"]).sum()
    total_days = len(df)

    cpi_higher_pct = cpi_higher_days / total_days * 100
    ten_y_higher_pct = ten_y_higher_days / total_days * 100

    ax_chart.plot(
        df["observation_date"],
        df["CPI_YoY"],
        linewidth=2.2,
        label="CPI YoY (%)"
    )

    ax_chart.plot(
        df["observation_date"],
        df["10Y"],
        linewidth=2.2,
        label="10Y Treasury Yield (%)"
    )

    ax_chart.fill_between(
        df["observation_date"],
        df["CPI_YoY"],
        df["10Y"],
        where=(df["CPI_YoY"] > df["10Y"]),
        interpolate=True,
        color="#FFB6C1",
        alpha=0.45,
        label="CPI > 10Y"
    )

    ax_chart.fill_between(
        df["observation_date"],
        df["CPI_YoY"],
        df["10Y"],
        where=(df["CPI_YoY"] < df["10Y"]),
        interpolate=True,
        color="#B7E4C7",
        alpha=0.45,
        label="CPI < 10Y"
    )

    ax_chart.axhline(0, linewidth=1, alpha=0.4)

    ax_chart.set_title(
        f"US CPI YoY vs 10-Year Treasury Yield - Last {years} Year(s)",
        fontsize=15,
        pad=22
    )

    ax_chart.set_ylabel("Percent (%)")
    ax_chart.grid(True, linestyle="--", alpha=0.3)

    ax_chart.legend(
        loc="upper center",
        bbox_to_anchor=(0.5, 1.15),
        ncol=4,
        frameon=False,
        fontsize=10
    )

    ax_spread.plot(
        df["observation_date"],
        df["Spread"],
        linewidth=2,
        label="Real Yield (10Y - CPI)"
    )

    ax_spread.fill_between(
        df["observation_date"],
        df["Spread"],
        0,
        where=(df["Spread"] >= 0),
        interpolate=True,
        color="#B7E4C7",
        alpha=0.5
    )

    ax_spread.fill_between(
        df["observation_date"],
        df["Spread"],
        0,
        where=(df["Spread"] < 0),
        interpolate=True,
        color="#FFB6C1",
        alpha=0.5
    )

    ax_spread.axhline(
        0,
        color="black",
        linewidth=1,
        alpha=0.7
    )

    ax_spread.set_title(
        "Real Yield = 10Y Treasury Yield - CPI YoY",
        fontsize=12,
        pad=10
    )

    ax_spread.set_xlabel("Date")
    ax_spread.set_ylabel("Percent (%)")
    ax_spread.grid(True, linestyle="--", alpha=0.3)

    info_text = (
        f"Current Data\n"
        f"====================\n\n"
        f"Date\n"
        f"{latest_date}\n\n"
        f"CPI YoY\n"
        f"{latest_cpi:.2f}%\n\n"
        f"10Y Yield\n"
        f"{latest_10y:.2f}%\n\n"
        f"Real Yield\n"
        f"{latest_spread:.2f}%\n\n"
        f"====================\n\n"
        f"Period Summary\n"
        f"Total data days: {total_days}\n\n"
        f"Red Area\n"
        f"CPI > 10Y\n"
        f"{cpi_higher_days} days\n"
        f"{cpi_higher_pct:.1f}%\n\n"
        f"Green Area\n"
        f"CPI < 10Y\n"
        f"{ten_y_higher_days} days\n"
        f"{ten_y_higher_pct:.1f}%\n\n"
        f"Interpretation\n"
        f"--------------------\n"
        f"Red:\n"
        f"Inflation is higher\n"
        f"than 10Y yield.\n\n"
        f"Green:\n"
        f"10Y yield is higher\n"
        f"than inflation."
    )

    ax_info.text(
        0,
        1,
        info_text,
        fontsize=11,
        va="top",
        ha="left",
        bbox=dict(
            boxstyle="round",
            alpha=0.15
        )
    )

    fig.canvas.draw_idle()


def change_period(label):
    draw_chart(PERIODS[label])


def save_png(event):
    filename = f"CPI_vs_10Y_Dashboard_{current_years}Y.png"
    fig.savefig(filename, dpi=300, bbox_inches="tight")
    print(f"Saved: {filename}")


radio.on_clicked(change_period)
save_button.on_clicked(save_png)

draw_chart(1)

plt.show()