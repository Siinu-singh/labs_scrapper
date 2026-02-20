# Database Setup Instructions - Manual Steps

## Issue: MySQL Authentication

The automated Python script cannot connect to MySQL with your credentials. This is likely due to MySQL authentication configuration.

## Solution: Manual Setup Steps

### Step 1: Verify MySQL is Running
```bash
sudo systemctl status mysql
# or
sudo service mysql status
```

### Step 2: Connect to MySQL and Check Root User
```bash
# Try connecting as root (may not need password for localhost)
mysql -u root
# or with password
mysql -u root -p
# When prompted, enter: Suraj@24!
```

### Step 3: Once Connected to MySQL, Run These Commands
```sql
-- Check if scraper_db database exists
SHOW DATABASES;

-- If it doesn't exist, create it
CREATE DATABASE scraper_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Use the database
USE scraper_db;

-- Check if tables exist
SHOW TABLES;

-- If tables don't exist, create them:
CREATE TABLE tests (
  id INT AUTO_INCREMENT PRIMARY KEY,
  test_name VARCHAR(255) NOT NULL UNIQUE,
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_test_name (test_name)
);

CREATE TABLE test_prices (
  id INT AUTO_INCREMENT PRIMARY KEY,
  test_id INT NOT NULL,
  lab_name VARCHAR(50) NOT NULL,
  price DECIMAL(10, 2),
  matched_test_name VARCHAR(255),
  match_score FLOAT,
  is_available BOOLEAN DEFAULT true,
  scraped_at TIMESTAMP,
  is_latest BOOLEAN DEFAULT true,
  FOREIGN KEY (test_id) REFERENCES tests(id) ON DELETE CASCADE,
  UNIQUE KEY unique_test_lab (test_id, lab_name, is_latest),
  INDEX idx_test_id (test_id),
  INDEX idx_lab_name (lab_name),
  INDEX idx_latest (is_latest)
);

-- Now insert the 100 test names
-- See the file: insert_tests.sql in the project root
```

### Step 4: Insert 100 Test Names
Copy the contents of `insert_tests.sql` file and paste it in MySQL:

```bash
# Option A: From command line
mysql -u root -p scraper_db < insert_tests.sql

# Option B: From MySQL prompt
mysql> USE scraper_db;
mysql> source /path/to/insert_tests.sql;
```

### Step 5: Verify Data was Inserted
```sql
-- Check total tests
SELECT COUNT(*) as total_tests FROM tests;

-- View first 10 tests
SELECT * FROM tests LIMIT 10;

-- View test_prices table (should be empty initially)
SELECT COUNT(*) FROM test_prices;
```

## Alternative: Update MySQL Root Password

If you want to reset the root password to ensure it's correct:

```bash
sudo mysql
# Then run:
ALTER USER 'root'@'localhost' IDENTIFIED BY 'Suraj@24!';
FLUSH PRIVILEGES;
exit;
```

## Files Created

1. **requirements.txt** - Updated with SQLAlchemy and PyMySQL
2. **src/config.py** - Updated with DATABASE_* config variables
3. **src/db/connection.py** - Database connection setup
4. **src/models/test_models.py** - SQLAlchemy ORM models
5. **insert_tests.py** - Python script to insert tests (alternative method)
6. **insert_tests.sql** - SQL script to insert 100 tests (recommended)

## Next Steps

Once the 100 tests are inserted in the database:

1. Test the connection from Python
2. Create batch scraping service
3. Setup scheduler for automated cron jobs
4. Create API endpoints for users

