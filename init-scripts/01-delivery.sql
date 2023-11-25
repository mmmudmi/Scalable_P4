CREATE DATABASE IF NOT EXISTS delivery;

CREATE USER 'delivery-username'@'%' IDENTIFIED BY 'delivery-password';
GRANT ALL PRIVILEGES ON delivery.* TO 'delivery-username'@'%';
FLUSH PRIVILEGES;
