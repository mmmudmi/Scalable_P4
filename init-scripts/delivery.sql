-- Create a new database
CREATE DATABASE IF NOT EXISTS delivery;

-- Create a new user and grant privileges on the database
CREATE USER 'delivery_username'@'%' IDENTIFIED BY 'delivery_password';
GRANT ALL PRIVILEGES ON delivery.* TO 'delivery_username'@'%';
FLUSH PRIVILEGES;
