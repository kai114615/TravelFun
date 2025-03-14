CREATE TABLE `theme_query_event_relations` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `display_order` int NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `event_id` bigint NOT NULL,
  `query_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `theme_query_event_relations_event_id_c384177a_fk_theme_events_id` (`event_id`),
  KEY `theme_query_event_re_query_id_8bffcdae_fk_theme_que` (`query_id`),
  CONSTRAINT `theme_query_event_re_query_id_8bffcdae_fk_theme_que` FOREIGN KEY (`query_id`) REFERENCES `theme_query_results` (`id`),
  CONSTRAINT `theme_query_event_relations_event_id_c384177a_fk_theme_events_id` FOREIGN KEY (`event_id`) REFERENCES `theme_events` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

LOCK TABLES `theme_query_event_relations` WRITE;
UNLOCK TABLES;
