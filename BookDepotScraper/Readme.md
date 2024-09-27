

---
### 说明
* 所有Bubbles and Books历史上买过的书都存放在这个[Google Sheet](https://docs.google.com/spreadsheets/d/1UlbMqsK0LkasETKOgwWD5up9xxRBCg7dXgRTS6OTVJQ/edit?gid=0#gid=0)中
* `gs_to_mysql.py` - 这个代码用来将上面提到的Google Sheet数据(inplace)写入MySQL数据库`BookDepot.BOOKDEPOT_FICTION_ROMANCE`中。
* `scraper.py` - 该代码可以将BookDepot网站上所有Fiction类别的书爬取到 (可能需要对其中的css selector做一些Debug)。爬到的数据存放在当前文件夹的`output.csv`文件中
* `scraper_to_mysql.py`
  * 将爬取到的数据`output.csv`文件进行清理得到`cleaned_output.csv`
  * 同时在MySQL数据库中定义schema
  * 将`cleaned_output.csv`存放在MySQL数据库`BookDepot.BOOKS_PURCHASED`中。

---
### Todos
- [ ] 对于上面[Google Sheet](https://docs.google.com/spreadsheets/d/1UlbMqsK0LkasETKOgwWD5up9xxRBCg7dXgRTS6OTVJQ/edit?gid=0#gid=0)，每个月还是需要手动将购买的书的信息写入Google Sheet
- [ ] ...

