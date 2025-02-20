-- 使用正確的資料庫
USE fun;

-- 設定字符集
SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- 創建資料表來儲存匯入時間資訊
CREATE TABLE IF NOT EXISTS theme_import_dates (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    import_date DATETIME NOT NULL,
    timezone_type INTEGER NOT NULL,
    timezone VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 創建主要的活動/展覽資訊表
CREATE TABLE IF NOT EXISTS theme_events (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    uid VARCHAR(100) NOT NULL,
    activity_name TEXT NOT NULL,
    description TEXT,
    organizer VARCHAR(200),
    address TEXT,
    start_date DATE,
    end_date DATE,
    location VARCHAR(200),
    latitude DECIMAL(12, 8),
    longitude DECIMAL(12, 8),
    ticket_price TEXT,
    related_link TEXT,
    image_url TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 創建查詢結果資訊表
CREATE TABLE IF NOT EXISTS theme_query_results (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    query_timestamp VARCHAR(50) NOT NULL,
    limit_count INTEGER NOT NULL,
    offset_count INTEGER NOT NULL,
    total_count INTEGER NOT NULL,
    sort_order VARCHAR(50),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 創建關聯表，連接查詢結果和事件
CREATE TABLE IF NOT EXISTS theme_query_event_relations (
    query_id BIGINT NOT NULL,
    event_id BIGINT NOT NULL,
    display_order INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (query_id, event_id),
    FOREIGN KEY (query_id) REFERENCES theme_query_results(id),
    FOREIGN KEY (event_id) REFERENCES theme_events(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

SET FOREIGN_KEY_CHECKS = 1;