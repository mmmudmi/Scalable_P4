CREATE DATABASE IF NOT EXISTS payment;

CREATE USER 'payment-username'@'%' IDENTIFIED BY 'payment-password';
GRANT ALL PRIVILEGES ON payment.* TO 'payment-username'@'%';
FLUSH PRIVILEGES;
