CREATE DATABASE IF NOT EXISTS orders;

CREATE USER 'orders-username' @'%' IDENTIFIED BY 'orders-password';

GRANT ALL PRIVILEGES ON orders.* TO 'orders-username' @'%';

FLUSH PRIVILEGES;

USE orders;

CREATE TABLE
    orders (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user VARCHAR(60) NOT NULL,
        item VARCHAR(60) NOT NULL,
        amount INT NOT NULL,
        total DECIMAL(10, 2) NOT NULL,
        status VARCHAR(60) NOT NULL,
        error VARCHAR(60) NULL
    );

create index ix_orders_id on orders (id);

create index ix_orders_item on orders (item);

create index ix_orders_status on orders (status);

create index ix_orders_user on orders (user);