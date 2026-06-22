# 美國通膨與十年期公債儀表板

這是 `Python/CPI_vs_10Y_v4.py` 的靜態網頁版，可直接部署到 GitHub Pages。

## 資料方式

網頁會由瀏覽器直接下載 FRED CSV：

- `CPIAUCSL`：消費者物價指數
- `DGS10`：十年期美國公債殖利率

下載後資料只存在使用者瀏覽器的 `localStorage` 快取，不會存進本機專案資料夾，也不會提交到 GitHub。快取有效時間為 12 小時；按「重新整理資料」可強制重新下載。

如果瀏覽器直接讀取 FRED 時遇到跨網域限制，網頁會自動改用備援 CORS 通道下載 CSV；成功後仍然只存進瀏覽器快取。

若所有瀏覽器讀取通道都被擋，網頁無法在沒有使用者授權的情況下自動讀取已下載到電腦的 CSV。這是瀏覽器安全規則。此時請使用頁面底部的下載與匯入功能，資料仍只會存進瀏覽器快取。

## 部署到 GitHub Pages

1. 執行 `push-to-github.cmd` 上傳到 `Turnstone7512/CPI_Dashboard`。
2. 到 repository 的 `Settings > Pages`。
3. `Build and deployment` 選 `Deploy from a branch`。
4. Branch 選 `main`，資料夾選 `/root`。

## 功能

- 切換近 1、3、5、10、20、50、100 年。
- 比較消費者物價年增率與十年期美國公債殖利率。
- 顯示實質利率與區間統計。
- 下載目前儀表板圖片。
- 中文顯示專有名詞，滑鼠移過名詞時顯示英文對照。
- 底部提供偵錯紀錄，可查看 FRED 直連、備援 CORS 通道、HTTP 狀態、逾時與 CSV 解析結果。
- 若瀏覽器無法跨網域下載資料，可在底部下載 FRED CSV 後手動匯入瀏覽器快取。
