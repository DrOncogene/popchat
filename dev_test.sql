-- sets up the test database

CREATE USER IF NOT EXISTS 'popchat_dev'@'localhost' IDENTIFIED BY 'popchat_pwd';
CREATE DATABASE IF NOT EXISTS popchat_dev_db;


GRANT ALL ON `popchat_dev_db`.* TO 'popchat_dev'@'localhost';

FLUSH PRIVILEGES
