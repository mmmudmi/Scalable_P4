CREATE DATABASE IF NOT EXISTS inventory;

CREATE USER
    'inventory-username' @'%' IDENTIFIED BY 'inventory-password';

GRANT ALL PRIVILEGES ON inventory.* TO 'inventory-username' @'%';

FLUSH PRIVILEGES;

USE inventory;

CREATE TABLE
    items (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(60) NOT NULL,
        quantity INT NOT NULL,
        price DECIMAL(10, 2) NOT NULL,
        CONSTRAINT ix_items_name UNIQUE (name)
    );

create index ix_items_id on items (id);


INSERT INTO
    items (name, quantity, price)
VALUES ('scalable credit', 100, 19.99);