# تمرین‌های عملی (Labs)

**پیش‌نیاز:** اسکریپت `Setup-FabricLab.ps1` رو اجرا کن. داده‌ها در پوشه‌ی `data\` ساخته می‌شن و (اگر مجاز باشه) در Lakehouse با نام `lh_prep` زیر `Files/raw/...` آپلود می‌شن.
**برای هر Lab چی بفرستی:** کد/اسکریپت (متن)، خروجی‌ها (تعداد ردیف، نتیجه‌ی کوئری)، اسکرین‌شات یا توضیح تصمیم‌هات، و ۳-۵ خط "چرا این‌طور طراحی کردم".
مشکلات داده عمداً پنهان گذاشته شده. کشفشون بخشی از تمرینه.

## Lab 1 - Workspace، Capacity و نقش‌ها
- ساخت دو workspace: `ws_dev` و `ws_prod` (یا استفاده از workspace اسکریپت).
- یک کاربر/گروه تستی رو Viewer و دیگری رو Contributor کن. بگو هر کدوم چه کاری می‌تونن بکنن و چه کاری نه (تست کن).
- **بفرست:** جدول نقش‌ها + نتیجه‌ی تست.

## Lab 2 - Bronze
- با Notebook فایل‌های `orders_batch_1.csv` رو از `Files/raw/orders/` بخون و در جدول Delta به نام `bronze_orders` بنویس. ستون‌های `_ingest_ts` و `_source_file` اضافه کن.
- Schema رو **صریح** تعریف کن (infer نکن).
- **بفرست:** کد + `DESCRIBE DETAIL bronze_orders` + تعداد ردیف.

## Lab 3 - Silver (Data Quality)
- از bronze به `silver_orders`: تمیزکاری، dedupe، تایپ‌ها، نرمال‌سازی status، parse تاریخ‌های ناهمگون.
- ردیف‌های بد رو دور نریز: در `silver_orders_rejected` با ستون `reject_reason` ذخیره کن.
- یک جدول `dq_report` بساز: تعداد ردیف ورودی/خروجی/ردشده به تفکیک دلیل.
- **بفرست:** کد + `dq_report` + لیست مشکلاتی که پیدا کردی.

## Lab 4 - SCD Type 2
- `customers_day1.csv` رو بارگذاری کن و `dim_customer` (SCD2) بساز (ستون‌های `valid_from`, `valid_to`, `is_current`, surrogate key).
- بعد `customers_day2.csv` رو با MERGE اعمال کن.
- **تست:** برای مشتری‌ای که city عوض کرده باید دو ردیف باشه و فقط یکی `is_current`.
- **بفرست:** کد + کوئری اعتبارسنجی + توضیح درباره‌ی idempotent بودن (اگر دوبار اجرا شه چی می‌شه؟).

## Lab 5 - Incremental Pipeline
- یک Pipeline بساز که `orders_batch_1..3` رو به‌ترتیب و با پارامتر پردازش کنه (Lookup + ForEach یا پارامتر batch).
- batch 3 شامل داده‌ی دیررسیده و آپدیت سطرهای قدیمی است. با MERGE (کلید `order_id`) درست اعمالش کن.
- یک بار pipeline رو دوباره اجرا کن. نتیجه نباید عوض بشه.
- **بفرست:** تعریف pipeline (JSON یا توضیح)، تعداد ردیف قبل و بعد، استراتژی deletes/late data.

## Lab 6 - Gold و Warehouse
- مدل star: `fact_sales`, `dim_customer`, `dim_product`, `dim_store`, `dim_date`.
- یک Warehouse بساز (`wh_prep`) و جدول‌ها رو با CTAS یا cross-database query از Lakehouse بیار.
- یک stored procedure برای بارگذاری fact بنویس. یک **clone** بگیر و time travel بزن.
- **بفرست:** DDL، stored procedure، کوئری time travel.

## Lab 7 - Shortcut و Dataflow Gen2
- در Lakehouse یک Shortcut بساز (مثلاً به یک پوشه در Lakehouse دیگر یا ADLS).
- یک Dataflow Gen2 بساز که `products.csv` رو تمیز کنه (trim، تایپ، حذف تکراری) و در Lakehouse بنویسه.
- **بفرست:** توضیح تفاوت هزینه/عملکرد این روش با Notebook برای همین کار.

## Lab 8 - Semantic Model و DAX
- روی gold یک semantic model بساز (Direct Lake)، رابطه‌ها و Date table.
- این measureها رو بنویس: Total Sales، Sales LY، YoY %، Sales YTD، Rolling 3-Month Sales، Avg Order Value، Customers with >1 order، Sales % of Total (همه‌ی فروشگاه‌ها)، Top 3 Products by Sales (با TOPN).
- **بفرست:** کد DAX هر measure + توضیح context transition جایی که استفاده کردی.

## Lab 9 - امنیت (RLS / CLS / DDM)
- RLS داینامیک در semantic model بر اساس `USERPRINCIPALNAME()` و جدول mapping کاربر-فروشگاه.
- در Warehouse: RLS با security policy، ماسک روی ایمیل مشتری، و CLS روی `unit_cost`.
- **بفرست:** کد + سناریوی تست + توضیح اثر روی Direct Lake.

## Lab 10 - Performance و نگهداری Delta
- پوشه‌ی `small_files/` (۱۰۰ فایل ریز) رو به Delta بنویس. تعداد فایل‌ها رو با `DESCRIBE DETAIL` ببین.
- OPTIMIZE (با و بدون ZORDER) و VACUUM بزن. قبل و بعد رو مقایسه کن. یک بار با V-Order فعال و یک بار غیرفعال بنویس.
- **بفرست:** جدول مقایسه (تعداد فایل، اندازه، زمان کوئری).

## Lab 11 - Real-Time و KQL
- `telemetry.jsonl` رو در Eventhouse ingest کن (Get data → OneLake). یک ingestion mapping بنویس.
- کوئری‌ها: (a) میانگین دما هر ۵ دقیقه به تفکیک device، (b) دستگاه‌هایی که ۱۰ دقیقه گزارش ندادن، (c) outlier با `-999`، (d) top 5 دستگاه با بیشترین نوسان، (e) dedupe روی (device_id, ts).
- یک Real-Time Dashboard یا Activator rule ساده بساز.
- **بفرست:** کوئری‌های KQL + توضیح update policy که برای تمیزکاری می‌ذاشتی.

## Lab 12 - ALM
- workspace dev رو به Git (GitHub یا Azure DevOps) وصل کن. یک تغییر در notebook بده و commit و PR کن.
- یک deployment pipeline (Dev → Test → Prod) با deployment rule برای تغییر Lakehouse/پارامتر.
- **بفرست:** توضیح مراحل و مشکلاتی که دیدی.

## Lab 13 - Troubleshooting (چالشی)
- یک Pipeline عمداً خراب بساز (مثلاً مسیر فایل غلط، ستون حذف‌شده، timeout) و ۳ نوع خطا رو در Monitoring hub بررسی کن.
- یک Notebook با OOM یا skew بساز (join روی کلید با توزیع نامتوازن) و با Spark UI تشخیص بده و رفعش کن.
- **بفرست:** Runbook ۱ صفحه‌ای: علامت → علت → اقدام.

---
## تمرین SQL/KQL/DAX بیشتر
- `SELECT` پنجره‌ای: ROW_NUMBER، LAG، SUM OVER برای running total روی `fact_sales`.
- ۱۰ کوئری KQL پیشرفته (join، mv-expand، series_decompose) روی telemetry.
