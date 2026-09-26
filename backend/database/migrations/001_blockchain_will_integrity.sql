-- Apply against dmsdb. CREATE TABLE IF NOT EXISTS makes this migration rerunnable.

CREATE TABLE IF NOT EXISTS wills_versions (
  id BIGINT NOT NULL AUTO_INCREMENT,
  will_id INT NOT NULL,
  version INT NOT NULL,
  pdf_path VARCHAR(1024) NOT NULL,
  hash CHAR(64) CHARACTER SET ascii COLLATE ascii_bin NOT NULL,
  blockchain_tx VARCHAR(66) NULL,
  blockchain_status ENUM('pending', 'submitted', 'confirmed', 'failed') NOT NULL DEFAULT 'pending',
  blockchain_block BIGINT NULL,
  encryption_key_id VARCHAR(255) NOT NULL,
  encryption_nonce VARBINARY(12) NOT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  confirmed_at DATETIME NULL,
  PRIMARY KEY (id),
  UNIQUE KEY uq_wills_versions_will_version (will_id, version),
  INDEX idx_wills_versions_latest (will_id, version),
  INDEX idx_wills_versions_hash (hash),
  CONSTRAINT fk_wills_versions_will FOREIGN KEY (will_id) REFERENCES wills(id)
);

CREATE TABLE IF NOT EXISTS blockchain_events (
  id BIGINT NOT NULL AUTO_INCREMENT,
  will_id INT NOT NULL,
  event_type VARCHAR(64) NOT NULL,
  tx_hash VARCHAR(66) NULL,
  payload JSON NOT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  INDEX idx_blockchain_events_will_created (will_id, created_at),
  INDEX idx_blockchain_events_tx (tx_hash),
  CONSTRAINT fk_blockchain_events_will FOREIGN KEY (will_id) REFERENCES wills(id)
);

CREATE TABLE IF NOT EXISTS blockchain_outbox (
  id BIGINT NOT NULL AUTO_INCREMENT,
  will_version_id BIGINT NOT NULL,
  event_type VARCHAR(64) NOT NULL,
  payload JSON NOT NULL,
  status ENUM('pending', 'processing', 'completed', 'failed') NOT NULL DEFAULT 'pending',
  attempt_count INT NOT NULL DEFAULT 0,
  available_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  locked_at DATETIME NULL,
  locked_by VARCHAR(128) NULL,
  last_error TEXT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  completed_at DATETIME NULL,
  PRIMARY KEY (id),
  UNIQUE KEY uq_blockchain_outbox_version_event (will_version_id, event_type),
  INDEX idx_blockchain_outbox_ready (status, available_at),
  CONSTRAINT fk_blockchain_outbox_version FOREIGN KEY (will_version_id) REFERENCES wills_versions(id)
);