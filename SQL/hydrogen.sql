SELECT EXTRACT(year FROM date_online) as year_online, SUM(normalised_capacity_in_kilotons_hydrogen_per_year) as total_capacity_in_kiloton_per_year 
FROM project_capacity pc 
INNER JOIN project_status ps 
ON pc.project_id = ps.project_id WHERE ps.status = 'planning' 
AND pc.normalised_capacity_in_kilotons_hydrogen_per_year IS NOT NULL GROUP BY year_online


SELECT EXTRACT(year FROM date_online) as year_online,SUM(normalised_capacity_in_kilotons_hydrogen_per_year) as total_capacity_in_kiloton_per_year 
FROM project_capacity pc 
INNER JOIN project_status ps 
ON pc.project_id = ps.project_id WHERE ps.status = 'Operational' 
AND pc.normalised_capacity_in_kilotons_hydrogen_per_year IS NOT NULL 
GROUP BY year_online ORDER BY year_online ASC


SELECT date_trunc('year', date_online) AS Year, count(*) AS Number_of_projects FROM project_status GROUP BY Year ORDER BY Year;


SELECT technology, SUM(normalised_capacity_in_kilotons_hydrogen_per_year) AS total_hydrogen_capacity_kilotons_per_year 
FROM project_capacity a 
INNER JOIN project_technology b 
ON a.project_id = b.project_id 
GROUP BY technology ORDER BY total_hydrogen_capacity_kilotons_per_year DESC;


SELECT YEAR(date_online) AS year, a.technology, SUM(a.normalised_capacity_in_kilotons_hydrogen_per_year) AS capacity 
FROM project_capacity a 
INNER JOIN project_technology b  ON a.project_id = b.project_id 
INNER JOIN project_status c ON a.project_id = c.project_id 
GROUP BY YEAR(date_online), a.technology

SELECT EXTRACT(YEAR FROM date_online) AS year, b.technology, SUM(a.normalised_capacity_in_kilotons_hydrogen_per_year) AS capacity 
FROM project_capacity a INNER JOIN project_technology b ON a.project_id = b.project_id 
INNER JOIN project_status c ON a.project_id = c.project_id 
GROUP BY EXTRACT(YEAR FROM date_online), b.technology


SELECT b.country, 
CASE 
	WHEN EXTRACT(YEAR FROM date_online) BETWEEN 2020 AND 2030 THEN '2020-2030' 
	WHEN EXTRACT(YEAR FROM date_online) BETWEEN 2030 AND 2040 THEN '2030-2040' 
	WHEN EXTRACT(YEAR FROM date_online) >= 2040 THEN '2040+' 
	ELSE 'prior 2020' END AS period, 
SUM(a.normalised_capacity_in_kilotons_hydrogen_per_year) AS capacity 
FROM project_capacity a INNER JOIN project_location b ON a.project_id = b.project_id 
INNER JOIN project_status c ON a.project_id = c.project_id 
WHERE b.country = 'UK' OR b.country = 'United Kingdom' OR b.country = 'France' OR b.country = 'Germany' OR b.country = 'United States' OR b.country = 'China' OR b.country_code = 'UK' OR b.country_code = 'GBR' OR b.country_code = 'FRA' OR b.country_code = 'DEU' OR b.country_code = 'USA' OR b.country_code = 'CHN' 
GROUP BY b.country, period ORDER BY b.country, period

SELECT * FROM project_status

SELECT EXTRACT(year FROM date_online) as year_online,SUM(normalised_capacity_in_kilotons_hydrogen_per_year) as total_capacity_in_kiloton_per_year 
FROM project_capacity pc 
INNER JOIN project_status ps 
ON pc.project_id = ps.project_id WHERE ps.status = 'Operational' 
AND pc.normalised_capacity_in_kilotons_hydrogen_per_year IS NOT NULL 
GROUP BY year_online ORDER BY year_online ASC

Select project_name,  normalised_capacity_in_kilotons_hydrogen_per_year 
from project_capacity 
WHERE normalised_capacity_in_kilotons_hydrogen_per_year IS NOT NULL
ORDER BY normalised_capacity_in_kilotons_hydrogen_per_year DESC LIMIT 5






SELECT EXTRACT(YEAR FROM date_online) AS year, b.technology, SUM(a.normalised_capacity_in_kilotons_hydrogen_per_year) AS capacity 
FROM project_capacity a INNER JOIN project_technology b ON a.project_id = b.project_id 
INNER JOIN project_status c ON a.project_id = c.project_id 
GROUP BY EXTRACT(YEAR FROM date_online), b.technology



SELECT EXTRACT(YEAR FROM ps.date_online) AS year, pt.technology, SUM(pc.normalised_capacity_in_kilotons_hydrogen_per_year) 
AS total_capacity_kilotons_per_year FROM project_technology pt 
JOIN project_capacity pc ON pt.project_id = pc.project_id 
JOIN project_status ps ON pc.project_id = ps.project_id 
WHERE ps.date_online IS NOT NULL AND pc.normalised_capacity_in_kilotons_hydrogen_per_year IS NOT NULL 
GROUP BY EXTRACT(YEAR FROM ps.date_online), pt.technology ORDER BY EXTRACT(YEAR FROM ps.date_online), total_capacity_kilotons_per_year DESC

SELECT DISTINCT(status) FROM project_status

SELECT CONCAT(TABLE_NAME, ', ', COLUMN_NAME, ', ', DATA_TYPE, ', ', IS_NULLABLE) AS "Table, Column, DataType, Is_Nullable" 
FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME IN ('project_location')

SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME IN ('project_location')

SELECT STRING_AGG(DISTINCT("country_code"),', ') FROM project_location


SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA= 'public'

SELECT COLUMN_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME IN ('project_location')

SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME IN ('project_location')

SELECT 