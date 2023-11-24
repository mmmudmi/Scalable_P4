-- Create a new database
CREATE DATABASE IF NOT EXISTS payment;

-- Create a new user and grant privileges on the database
CREATE USER 'payment_username'@'%' IDENTIFIED BY 'payment_password';
GRANT ALL PRIVILEGES ON payment.* TO 'payment_username'@'%';
FLUSH PRIVILEGES;
