DROP TABLE IF EXISTS `theme_import_dates`;
CREATE TABLE `theme_import_dates` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `import_date` datetime(6) NOT NULL,
  `timezone_type` int NOT NULL,
  `timezone` varchar(50) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

LOCK TABLES `theme_import_dates` WRITE;
UNLOCK TABLES;
