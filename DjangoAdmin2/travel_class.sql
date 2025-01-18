CREATE TABLE IF NOT EXISTS travel_class(
   class_id int not null primary key , 
   class_name varchar(30) not null
);
INSERT INTO travel_class(class_id,  class_name) VALUES (1, "文化類");
INSERT INTO travel_class(class_id,  class_name) VALUES (2, "生態類");
INSERT INTO travel_class(class_id,  class_name) VALUES (3, '古蹟類');
INSERT INTO travel_class(class_id,  class_name) VALUES (4, '廟宇類');
INSERT INTO travel_class(class_id,  class_name) VALUES (5, '藝術類');
INSERT INTO travel_class(class_id,  class_name) VALUES (6, '小吃/特產類');
INSERT INTO travel_class(class_id,  class_name) VALUES (7, '國家公園類');
INSERT INTO travel_class(class_id,  class_name) VALUES (8, '國家風景區類');
INSERT INTO travel_class(class_id,  class_name) VALUES (9, '休閒農業類');
INSERT INTO travel_class(class_id,  class_name) VALUES (10, '溫泉類');
INSERT INTO travel_class(class_id,  class_name) VALUES (11, '自然風景類');
INSERT INTO travel_class(class_id,  class_name) VALUES (12, '遊憩類');
INSERT INTO travel_class(class_id,  class_name) VALUES (13, '體育健身類');
INSERT INTO travel_class(class_id,  class_name) VALUES (14, '觀光工廠類');
INSERT INTO travel_class(class_id,  class_name) VALUES (15, '都會公園類');
INSERT INTO travel_class(class_id,  class_name) VALUES (16, '森林遊樂區類');
INSERT INTO travel_class(class_id,  class_name) VALUES (17, '林場類');
INSERT INTO travel_class(class_id,  class_name) VALUES (18, '其他');
