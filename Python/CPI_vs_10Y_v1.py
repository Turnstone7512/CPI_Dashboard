import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# ==========================
# 下載 FRED 資料
# ==========================

cpi_url = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=CPIAUCSL"
teny_url = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=DGS10"

cpi = pd.read_csv(cpi_url)
teny = pd.read_csv(teny_url)

# ==========================
# 日期處理
# ==========================

cpi["observation_date"] = pd.to_datetime(cpi["observation_date"])
teny["observation_date"] = pd.to_datetime(teny["observation_date"])

# ==========================
# CPI YoY
# ==========================

cpi["CPI"] = pd.to_numeric(cpi["CPIAUCSL"], errors="coerce")

cpi["CPI_YoY"] = (
    cpi["CPI"].pct_change(12) * 100
)

# ==========================
# 10Y Yield
# ==========================

teny["10Y"] = pd.to_numeric(
    teny["DGS10"],
    errors="coerce"
)

# ==========================
# 最近一年
# ==========================

end_date = datetime.today()
start_date = end_date - timedelta(days=365)

cpi = cpi[
    cpi["observation_date"] >= start_date
][["observation_date", "CPI_YoY"]]

teny = teny[
    teny["observation_date"] >= start_date
][["observation_date", "10Y"]]

# ==========================
# 合併資料
# CPI(月)
# 10Y(日)
# ==========================

df = pd.merge_asof(
    teny.sort_values("observation_date"),
    cpi.sort_values("observation_date"),
    on="observation_date",
    direction="backward"
)

df = df.dropna()

# ==========================
# 畫圖
# ==========================

plt.figure(figsize=(15, 8))

# CPI
plt.plot(
    df["observation_date"],
    df["CPI_YoY"],
    linewidth=2.5,
    label="CPI YoY (%)"
)

# 10Y
plt.plot(
    df["observation_date"],
    df["10Y"],
    linewidth=2.5,
    label="10Y Treasury Yield (%)"
)

# ==========================
# CPI > 10Y
# 馬卡龍紅
# ==========================

plt.fill_between(
    df["observation_date"],
    df["CPI_YoY"],
    df["10Y"],
    where=(df["CPI_YoY"] > df["10Y"]),
    interpolate=True,
    color="#FFB6C1",      # 馬卡龍粉紅
    alpha=0.45,
    label="CPI > 10Y"
)

# ==========================
# CPI < 10Y
# 馬卡龍綠
# ==========================

plt.fill_between(
    df["observation_date"],
    df["CPI_YoY"],
    df["10Y"],
    where=(df["CPI_YoY"] < df["10Y"]),
    interpolate=True,
    color="#B7E4C7",      # 馬卡龍綠
    alpha=0.45,
    label="CPI < 10Y"
)

# ==========================
# 美化
# ==========================

plt.title(
    "US CPI YoY vs 10-Year Treasury Yield (Last 1 Year)",
    fontsize=16,
    pad=20
)

plt.ylabel("Percent (%)")
plt.xlabel("Date")

plt.grid(
    linestyle="--",
    alpha=0.3
)

plt.legend()
plt.tight_layout()

plt.show()