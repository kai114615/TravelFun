CREATE TABLE IF NOT EXISTS travel(
  travel_id int not null primary key auto_increment, 
  travel_name varchar(50) not null, 
  travel_txt text , 
  tel VARCHAR(50), 
  travel_address text not null, 
  region varchar(10) not null,
  town varchar(10) not null,
  travel_linginfo text,
  opentime text,
  image1 text,
  image2 text,
  image3 text,
  Px decimal(12,8),
  Py decimal(12,8),
  class1 int not null,
  class2 int,
  class3 int,
  website text,
  ticketinfo text,
  parkinginfo text,
  upload date,
  FOREIGN KEY (class1) REFERENCES travel_class (class_id),
  FOREIGN KEY (class2) REFERENCES travel_class (class_id),
  FOREIGN KEY (class3) REFERENCES travel_class (class_id)
 );
 show warnings;
 
# drop table full_passengers;

LOAD DATA
INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/travel.csv'
INTO TABLE travel
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\r\n'
IGNORE 1 ROWS
(travel_id, travel_name, travel_txt, tel, travel_address, region, town, @travel_linginfo, @opentime, @image1, @image2, @image3, Px, Py, class1, @class2, @class3, @website, @ticketinfo, @parkinginfo, @upload)
SET 
travel_linginfo = NULLIF(@travel_linginfo,''), 
opentime = nullif(@opentime, ''), 
image1 = nullif(@image1, ''), 
image2 = nullif(@image2, ''),
image3 = nullif(@image3, ''),
class2 = nullif(@class2, ''),
class3 = nullif(@class3, ''),
website = nullif(@website, ''),
ticketinfo = nullif(@ticketinfo, ''),
parkinginfo = nullif(@parkinginfo, ''),
upload = nullif(@upload, "");
show variables like "secure_file_priv";
show warnings;
select * from travel;