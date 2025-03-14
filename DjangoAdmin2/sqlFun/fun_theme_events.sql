DROP TABLE IF EXISTS `theme_events`;
CREATE TABLE `theme_events` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `uid` varchar(255) NOT NULL,
  `activity_name` varchar(255) NOT NULL,
  `description` longtext,
  `organizer` varchar(255) DEFAULT NULL,
  `address` longtext,
  `start_date` datetime(6) DEFAULT NULL,
  `end_date` datetime(6) DEFAULT NULL,
  `location` varchar(255) DEFAULT NULL,
  `latitude` decimal(10,8) DEFAULT NULL,
  `longitude` decimal(11,8) DEFAULT NULL,
  `ticket_price` longtext,
  `source_url` longtext,
  `image_url` longtext,
  `created_at` datetime(6) NOT NULL,
  `updated_at` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uid` (`uid`)
) ENGINE=InnoDB CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

LOCK TABLES `theme_events` WRITE;
UNLOCK TABLES;
