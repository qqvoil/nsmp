-- NeverSMP Master Database Schema (MariaDB / MySQL 8.0+)
-- Optimized for high-throughput cross-server synchronization

CREATE DATABASE IF NOT EXISTS `neversmp` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE `neversmp`;

-- ==============================================================================
-- 1. Unified Authentication (VeloAuth / LimboAuth / AuthMe Sync)
-- ==============================================================================
CREATE TABLE IF NOT EXISTS `auth_users` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `username` VARCHAR(32) NOT NULL,
    `realname` VARCHAR(32) NOT NULL,
    `uuid` VARCHAR(36) NOT NULL,
    `password_hash` VARCHAR(255) NOT NULL,
    `ip_address` VARCHAR(45) NOT NULL,
    `reg_date` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `last_login` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    `is_bedrock` TINYINT(1) DEFAULT 0,
    `email` VARCHAR(128) NULL,
    UNIQUE KEY `uk_username` (`username`),
    KEY `idx_uuid` (`uuid`),
    KEY `idx_ip` (`ip_address`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ==============================================================================
-- 2. Global Tokens Economy (NeverSMP Player Balances)
-- ==============================================================================
CREATE TABLE IF NOT EXISTS `player_tokens` (
    `uuid` VARCHAR(36) NOT NULL PRIMARY KEY,
    `username` VARCHAR(32) NOT NULL,
    `tokens_balance` BIGINT UNSIGNED NOT NULL DEFAULT 0,
    `total_earned` BIGINT UNSIGNED NOT NULL DEFAULT 0,
    `total_spent` BIGINT UNSIGNED NOT NULL DEFAULT 0,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    KEY `idx_username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `token_transactions` (
    `id` BIGINT AUTO_INCREMENT PRIMARY KEY,
    `uuid` VARCHAR(36) NOT NULL,
    `username` VARCHAR(32) NOT NULL,
    `type` ENUM('BUY_WEB', 'AUCTION_SELL', 'AUCTION_BUY', 'SHOP_PURCHASE', 'ADMIN_GIVE', 'HARDCORE_REVIVE') NOT NULL,
    `amount` INT NOT NULL,
    `description` VARCHAR(255) NOT NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    KEY `idx_user_time` (`uuid`, `created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ==============================================================================
-- 3. Web Store Invoices & Payment Logs (Platega.io)
-- ==============================================================================
CREATE TABLE IF NOT EXISTS `store_invoices` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `player_name` VARCHAR(32) NOT NULL,
    `item_id` VARCHAR(64) NOT NULL,
    `item_name` VARCHAR(128) NOT NULL,
    `amount` DECIMAL(10,2) NOT NULL,
    `currency` VARCHAR(8) DEFAULT 'RUB',
    `status` ENUM('pending', 'paid', 'cancelled', 'refunded') DEFAULT 'pending',
    `server_target` VARCHAR(32) DEFAULT 'global',
    `promo_code` VARCHAR(32) NULL,
    `payload` VARCHAR(64) UNIQUE,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `paid_at` TIMESTAMP NULL,
    KEY `idx_player` (`player_name`),
    KEY `idx_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `store_promocodes` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `code` VARCHAR(32) NOT NULL UNIQUE,
    `discount_percent` INT NOT NULL DEFAULT 10,
    `max_uses` INT NOT NULL DEFAULT 0,
    `current_uses` INT NOT NULL DEFAULT 0,
    `expires_at` TIMESTAMP NULL,
    `is_active` TINYINT(1) DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Seed default promo code
INSERT IGNORE INTO `store_promocodes` (`code`, `discount_percent`, `max_uses`, `is_active`)
VALUES ('NEVER2026', 15, 0, 1), ('NSMP2026', 15, 0, 1);
