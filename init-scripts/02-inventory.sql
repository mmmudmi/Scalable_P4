CREATE DATABASE IF NOT EXISTS inventory;

CREATE USER 'inventory-username'@'%' IDENTIFIED BY 'inventory-password';
GRANT ALL PRIVILEGES ON inventory.* TO 'inventory-username'@'%';
FLUSH PRIVILEGES;
