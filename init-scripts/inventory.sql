-- Create a new database
CREATE DATABASE IF NOT EXISTS inventory;

-- Create a new user and grant privileges on the database
CREATE USER 'inventory_username'@'%' IDENTIFIED BY 'inventory_password';
GRANT ALL PRIVILEGES ON inventory.* TO 'inventory_username'@'%';
FLUSH PRIVILEGES;
