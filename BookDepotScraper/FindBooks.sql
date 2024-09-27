USE BookDepot;


select * from BookDepot.BOOKS_PURCHASED;

select count(*) from BookDepot.BOOKS_PURCHASED;

select count(*) from BookDepot.BOOKDEPOT_FICTION_ROMANCE;


select * from BookDepot.BOOKDEPOT_FICTION_ROMANCE;


-- 选出下个月份的书

WITH filtered_books AS (
    SELECT
        bfr.STOCK_QUANTITY,
        bfr.CATEGORIES,
        bfr.URL,
        bfr.BOOK_TITLE,
        bfr.AUTHOR,
        bfr.SALES_PRICE,
        bfr.LENGTH,
        bfr.WIDTH,
        bfr.HEIGHT,
        bfr.ISBN
    FROM BookDepot.BOOKDEPOT_FICTION_ROMANCE AS bfr
    WHERE bfr.LENGTH <= 8.5
        AND bfr.WIDTH <= 5.5
        AND bfr.HEIGHT <= 2
        AND bfr.SALES_PRICE <= 2.0
        AND bfr.STOCK_QUANTITY >= 30
        AND bfr.ISBN NOT IN (
            SELECT ISBN FROM BookDepot.BOOKS_PURCHASED
        )
        AND bfr.BOOK_TITLE NOT IN (
            SELECT BOOK_TITLE FROM BookDepot.BOOKS_PURCHASED
        )
        AND (
            bfr.CATEGORIES LIKE '%Mystery%'
            OR bfr.CATEGORIES LIKE '%Contemporary%'
            OR bfr.CATEGORIES LIKE '%Fantasy%'
            OR bfr.CATEGORIES LIKE '%Historical%'
        )
)
SELECT *
FROM filtered_books
ORDER BY SALES_PRICE ASC;











































