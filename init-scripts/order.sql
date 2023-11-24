-- Create a new database
CREATE DATABASE IF NOT EXISTS order;

-- Create a new user and grant privileges on the database
CREATE USER 'order_username'@'%' IDENTIFIED BY 'order_password';
GRANT ALL PRIVILEGES ON order.* TO 'order_username'@'%';
FLUSH PRIVILEGES;
