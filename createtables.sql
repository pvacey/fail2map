--!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
--tables to store IP + GPS coordinates
--!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
DROP TABLE coordinates;
CREATE TABLE coordinates
(
	ip var_char PRIMARY KEY,
	lat double,
	lon double
);
