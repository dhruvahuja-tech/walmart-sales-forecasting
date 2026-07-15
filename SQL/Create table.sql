DROP TABLE IF EXISTS train;
DROP TABLE IF EXISTS stores;
DROP TABLE IF EXISTS features;

CREATE TABLE stores (
    store       INT PRIMARY KEY,      
    type        VARCHAR(1),           
    size        INT                  
);


CREATE TABLE features (
    store               INT,
    date                DATE,
    temperature         FLOAT,        
    fuel_price          FLOAT,        
    markdown1           FLOAT,       
    markdown2           FLOAT,
    markdown3           FLOAT,
    markdown4           FLOAT,
    markdown5           FLOAT,
    cpi                 FLOAT,        
    unemployment        FLOAT,        
    is_holiday          BOOLEAN,      
    PRIMARY KEY (store, date)
);


CREATE TABLE train (
    store           INT,
    dept            INT,             
    date            DATE,
    weekly_sales    FLOAT,           
    is_holiday      BOOLEAN,
    PRIMARY KEY (store, dept, date)
);


--LOAD DATA FROM CSV--


COPY stores
FROM 'D:\Data Science\Sales Forecasting Project\original dataset\stores (1).csv'
DELIMITER ',' CSV HEADER;

COPY features
FROM 'D:\Data Science\Sales Forecasting Project\original dataset\features.csv'
DELIMITER ',' CSV HEADER NULL 'NA';

COPY train
FROM 'D:\Data Science\Sales Forecasting Project\original dataset\train.csv'
DELIMITER ',' CSV HEADER;


-- Verify row counts
SELECT 'stores'      AS table_name, COUNT(*) FROM stores
UNION ALL
SELECT 'features'    AS table_name, COUNT(*) FROM features
UNION ALL
SELECT 'train'       AS table_name, COUNT(*) FROM train