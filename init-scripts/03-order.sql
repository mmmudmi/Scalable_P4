CREATE DATABASE IF NOT EXISTS orders;

CREATE USER 'orders-username'@'%' IDENTIFIED BY 'orders-password';
GRANT ALL PRIVILEGES ON orders.* TO 'orders-username'@'%';
FLUSH PRIVILEGES;
