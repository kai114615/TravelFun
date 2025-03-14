DROP TABLE IF EXISTS `theme_query_results`;
CREATE TABLE `theme_query_results` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `query_timestamp` datetime(6) DEFAULT NULL,
  `limit_count` int DEFAULT NULL,
  `offset_count` int DEFAULT NULL,
  `total_count` int DEFAULT NULL,
  `sort_order` varchar(50) DEFAULT NULL,
  `created_at` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

LOCK TABLES `theme_query_results` WRITE;
UNLOCK TABLES;
