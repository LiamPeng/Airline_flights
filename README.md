# Airline flights (Flask + Postgres)

作業用的簡單網頁：後端是課程裡那套 airline schema（Postgres），前端用 Flask + Jinja。首頁輸入起迄機場三字碼、日期區間，會列出符合的航班；點某一班可以看該班機容量、已訂幾位、還剩幾位。

## 兩個 SQL 檔在幹嘛

`schema.sql` 只負責建表（含外鍵），用 `python app.py --init-db` 跑。

`flights.sql` 只有 INSERT 範例資料，在 init 之後再跑 `python app.py --load-sample-data`。不要和 init 重複跑「裡面又含 CREATE TABLE」的舊版整包，不然表已存在會報錯。

當初作業給的一整份 script 常常是表+資料但沒外鍵；這邊拆成 schema / data 比較好對齊 ER 圖。

## 環境變數

一定要有 Postgres，並設連線字串（資料庫名稱要和 `createdb` 的一致，例如 `airline`）：

```bash
export DATABASE_URL="postgresql://帳號:密碼@localhost:5432/airline"
```

範例裡請換成你自己機器上的帳密，不要真的留 `...` 三個點，否則連線會怪掉。本機若用 trust/peer，可以試：

```bash
export DATABASE_URL="postgresql:///airline"
```

也接受 `AIRLINE_DATABASE_URL`，二擇一即可。

## 第一次怎麼起來

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL="（照上面改）"
python app.py --init-db
python app.py --load-sample-data
```

資料已經亂掉就 `dropdb` / `createdb` 清掉重來再跑這兩步。

## Demo 當天

```bash
export DATABASE_URL="（同上）"
python app.py
```

瀏覽器開 http://127.0.0.1:5000 。若載入的是專案裡的 `flights.sql`，可以搜 JFK→LAX、日期含 2026 的區間，比較容易有結果。

## 路由（交報告可抄）

| 路徑 | 做什麼 |
|------|--------|
| `GET /` | 搜尋表單 |
| `POST /search` | 檢查輸入後 redirect 到結果 |
| `GET /flights?...` | 航班列表 |
| `GET /flights/<班號>/<日期>` | 該班座位資訊 |

日期格式 `YYYY-MM-DD`，起訖都算在內。起飛時間照資料庫存的顯示，當作 GMT。
