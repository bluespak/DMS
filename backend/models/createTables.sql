CREATE TABLE UserInfo (
  id INT PRIMARY KEY AUTO_INCREMENT,
  email VARCHAR(255) UNIQUE NOT NULL,
  lastname VARCHAR(100),
  firstname VARCHAR(100),
  grade VARCHAR(3),
  password_hash VARCHAR(255),
  DOB DATE,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE wills (
  id INT PRIMARY KEY AUTO_INCREMENT,
  body TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES UserInfo(id)
);

CREATE TABLE recipients (
  id INT PRIMARY KEY AUTO_INCREMENT,
  will_id INT NOT NULL,
  recipient_email VARCHAR(255) NOT NULL,
  recipient_name VARCHAR(100),
  relatedCode CHAR(1),
  FOREIGN KEY (will_id) REFERENCES wills(id)
);

CREATE TABLE triggers (
  id INT PRIMARY KEY AUTO_INCREMENT,
  user_id VARCHAR(10) NOT NULL,  
  trigger_type ENUM('inactivity', 'date', 'manual') NOT NULL,
  trigger_value VARCHAR(255), -- 예: '30'일, '2025-12-01'
  last_checked DATETIME,
  is_triggered BOOLEAN DEFAULT FALSE,
  FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE dispatch_log (
  id INT PRIMARY KEY AUTO_INCREMENT,
  will_id INT NOT NULL,
  recipient_id INT NOT NULL,
  sent_at DATETIME,
  status ENUM('pending', 'sent', 'failed') DEFAULT 'pending',
  FOREIGN KEY (will_id) REFERENCES wills(id),
  FOREIGN KEY (recipient_id) REFERENCES recipients(id)
);