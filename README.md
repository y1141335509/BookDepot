说明一下该项目


--- 
```
BookDepot
│   README.md
│
│
└───BookDepotScraper
│   │   cleaned_output.csv  -> 清理完成的数据。将会被写入MySQL
│   │   credentials.json    -> 存放Google Sheets API的credential
│   │   FindBooks.sql       -> 4. 通过该sql文件查找可以购买的书📖
│   │   gs_to_mysql.py      -> 3. 将所有已经买过的数据写入MySQL，方便查重
│   │   output.csv          -> 爬虫爬到的原始数据存放在此
│   │   Readme.md           -> 说明文件
│   │   scraper.py          -> 1. 爬虫
│   └── scraper_to_mysql.py -> 2. 清理爬取的数据，然后写入MySQL
│
│
└───Cratejoy
│   │   cratejoy_connector.py
│   └── 
│
└───Products（空）
│   │   
│   └── 
│
└───ShopifyStore
│   │   Shopify.py
│   └── shopofy_to_mysql.py
│
└───Stock（将要被删除）
│   │   
│   │   
```





































