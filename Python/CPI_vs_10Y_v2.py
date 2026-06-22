import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.widgets import RadioButtons, Button
from datetime import datetime, timedelta

# ==========================
# FRED 資料來源
# ==========================

CPI_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=CPIAUCSL"
TENY_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=DGS10"

# ==========================
# 期間設定
# ==========================

PERIODS = {
    "1Y": 1,
    "3Y": 3,
    "5Y": 5,
    "10Y": 10,
    "20Y": 20,
    "50Y": 50,
    "100Y": 100
}

# ==========================
# 讀取資料
# ==========================

cpi = pd.read_csv(CPI_URL)
teny = pd.read_csv(TENY_URL)

cpi["observation_date"] = pd.to_datetime(cpi["observation_date"])
teny["observation_date"] = pd.to_datetime(teny["observation_date"])

cpi["CPI"] = pd.to_numeric(cpi["CPIAUCSL"], errors="coerce")
cpi["CPI_YoY"] = cpi["CPI"].pct_change(12) * 100

teny["10Y"] = pd.to_numeric(teny["DGS10"], errors="coerce")

cpi = cpi[["observation_date", "CPI_YoY"]].dropna()
teny = teny[["observation_date", "10Y"]].dropna()

# ==========================
# 建立圖表
# ==========================

fig, ax = plt.subplots(figsize=(16, 8))
plt.subplots_adjust(left=0.22, bottom=0.15)

current_years = 1

# ==========================
# 畫圖函數
# ==========================

def draw_chart(years):
    global current_years
    current_years = years

    ax.clear()

    end_date = datetime.today()
    start_date = end_date - timedelta(days=365 * years)

    cpi_filtered = cpi[
        cpi["observation_date"] >= start_date
    ]

    teny_filtered = teny[
        teny["observation_date"] >= start_date
    ]

    df = pd.merge_asof(
        teny_filtered.sort_values("observation_date"),
        cpi_filtered.sort_values("observation_date"),
        on="observation_date",
        direction="backward"
    ).dropna()

    if df.empty:
        ax.set_title("No data available for this period")
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

    # CPI 折線
    ax.plot(
        df["observation_date"],
        df["CPI_YoY"],
        linewidth=2.2,
        label="CPI YoY (%)"
    )

    # 10Y 折線
    ax.plot(
        df["observation_date"],
        df["10Y"],
        linewidth=2.2,
        label="10Y Treasury Yield (%)"
    )

    # CPI > 10Y：馬卡龍紅
    ax.fill_between(
        df["observation_date"],
        df["CPI_YoY"],
        df["10Y"],
        where=(df["CPI_YoY"] > df["10Y"]),
        interpolate=True,
        color="#FFB6C1",
        alpha=0.45,
        label="CPI > 10Y"
    )

    # CPI < 10Y：馬卡龍綠
    ax.fill_between(
        df["observation_date"],
        df["CPI_YoY"],
        df["10Y"],
        where=(df["CPI_YoY"] < df["10Y"]),
        interpolate=True,
        color="#B7E4C7",
        alpha=0.45,
        label="CPI < 10Y"
    )

    ax.axhline(0, linewidth=1, alpha=0.4)

    ax.set_title(
        f"US CPI YoY vs 10-Year Treasury Yield - Last {years} Year(s)",
        fontsize=15,
        pad=18
    )

    ax.set_xlabel("Date")
    ax.set_ylabel("Percent (%)")

    ax.grid(True, linestyle="--", alpha=0.3)
    ax.legend(loc="upper left")

    info_text = (
        f"Latest Date: {latest_date}\n"
        f"CPI YoY: {latest_cpi:.2f}%\n"
        f"10Y Yield: {latest_10y:.2f}%\n"
        f"10Y - CPI: {latest_spread:.2f}%\n\n"
        f"Red Days\n"
        f"CPI > 10Y: {cpi_higher_days}\n\n"
        f"Green Days\n"
        f"CPI < 10Y: {ten_y_higher_days}"
    )

    ax.text(
        1.02,
        0.50,
        info_text,
        transform=ax.transAxes,
        fontsize=10,
        verticalalignment="center",
        bbox=dict(
            boxstyle="round",
            alpha=0.15
        )
    )

    fig.canvas.draw_idle()

# ==========================
# 左側期間按鈕
# ==========================

radio_ax = plt.axes([0.03, 0.38, 0.12, 0.35])

radio = RadioButtons(
    radio_ax,
    ("1Y", "3Y", "5Y", "10Y", "20Y", "50Y", "100Y")
)

def change_period(label):
    years = PERIODS[label]
    draw_chart(years)

radio.on_clicked(change_period)

# ==========================
# 匯出 PNG 按鈕
# ==========================

button_ax = plt.axes([0.03, 0.25, 0.12, 0.06])
save_button = Button(button_ax, "Save PNG")

def save_png(event):
    filename = f"CPI_vs_10Y_{current_years}Y.png"
    fig.savefig(filename, dpi=300, bbox_inches="tight")
    print(f"Saved: {filename}")

save_button.on_clicked(save_png)

# ==========================
# 初始顯示 1 年
# ==========================

draw_chart(1)

plt.show()