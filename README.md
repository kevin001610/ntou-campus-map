# 海大課程地圖

國立臺灣海洋大學校本部互動地圖，可依館樓、館樓代碼、課程名稱、教師或教室搜尋上課資訊。

## 功能

- 70 個可點選的地圖地點
- 40 組館樓代碼對照
- 106 筆上課資訊
- 地圖拖曳、縮放、鍵盤與手機操作
- 搜尋課程並定位館樓

目前 85 筆上課資訊已對應單一館樓；21 筆 MAF 海事大樓資料尚待確認甲、乙、丙棟。原始資料中的兩筆 ACTCER 已依資料維護者要求排除。資料更新日期：2026-10-01。

## 本機執行

本專案為 HTML、CSS、JavaScript 靜態網站，不需要安裝前端套件。請在專案資料夾執行：

```sh
python -m http.server 8000 --directory dist
```

再開啟 http://localhost:8000 。請使用 HTTP 伺服器，避免直接雙擊 HTML 造成 JSON 資料讀取失敗。

## 檔案結構

- `dist/index.html`：網站主頁
- `dist/app.js`：搜尋、地圖互動與課程顯示
- `dist/styles.css`：桌面與手機樣式
- `dist/data/places.json`：地圖位置與可點選區域
- `dist/data/codes.json`：館樓代碼
- `dist/data/courses.json`：課程資料
- `dist/assets/`：提供的校園地圖與代碼對照表
- `scripts/import_courses.py`：讀取四欄 Excel 課程表
- `validate.py`：資料、代碼與資源檢查

## 更新課程資料

Excel 欄位順序為：課程名稱、上課時間、上課地點、授課老師。

```sh
python scripts/import_courses.py "課程地點資料庫.xlsx" --date YYYY-MM-DD --edition 更新課表 --coverage provided-complete --exclude-location ACTCER
python validate.py
node --check dist/app.js
```

匯入會以提供的整份課程表取代現有資料。若僅提供新增課程，應先合併原有資料再匯入。時間碼以每三碼表示星期與節次，例如 303304 為週三第 3、4 節。

## 資料來源

校園地圖與館樓代碼取自專案維護者提供的校方圖表；課程資訊由維護者整理。此專案並非校方官方系統。館樓代碼無法唯一判定位置時，保留待確認標示，不推測實際棟別。
