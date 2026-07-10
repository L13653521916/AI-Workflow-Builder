CREATE TABLE users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(50) NOT NULL UNIQUE,
  email VARCHAR(100) NOT NULL UNIQUE,
  hashed_password VARCHAR(255) NOT NULL,
  is_active BOOLEAN DEFAULT TRUE,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE conversations (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  title VARCHAR(255) DEFAULT '新对话',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE messages (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  conversation_id BIGINT NOT NULL,
  role ENUM('user', 'assistant', 'system') NOT NULL,
  content TEXT NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (conversation_id) REFERENCES conversations(id)
);

CREATE TABLE workflows (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  name VARCHAR(100) NOT NULL,
  description TEXT,
  graph_json JSON,
  config_json JSON,
  status ENUM('draft', 'published') DEFAULT 'draft',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE knowledge_bases (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  name VARCHAR(100) NOT NULL,
  description TEXT,
  doc_count INT DEFAULT 0,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE documents (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  kb_id BIGINT NOT NULL,
  filename VARCHAR(255) NOT NULL,
  file_path VARCHAR(500),
  chunk_count INT DEFAULT 0,
  status ENUM('processing', 'ready', 'failed') DEFAULT 'processing',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (kb_id) REFERENCES knowledge_bases(id)
);

CREATE TABLE tools (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL UNIQUE,
  description TEXT,
  category VARCHAR(50),
  schema_json JSON,
  handler_name VARCHAR(100) NOT NULL,
  is_active BOOLEAN DEFAULT TRUE,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE workflow_runs (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  workflow_id BIGINT NOT NULL,
  user_id INT NOT NULL,
  status VARCHAR(20) DEFAULT 'running',
  input_json JSON,
  output_json JSON,
  logs_json JSON,
  started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  finished_at DATETIME,
  FOREIGN KEY (workflow_id) REFERENCES workflows(id),
  FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE model_profiles (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  name VARCHAR(100) NOT NULL,
  provider VARCHAR(50) NOT NULL,
  base_url VARCHAR(500) NOT NULL,
  api_key VARCHAR(500) NOT NULL,
  model_id VARCHAR(100) NOT NULL,
  config_json JSON,
  is_default BOOLEAN DEFAULT FALSE,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id)
);