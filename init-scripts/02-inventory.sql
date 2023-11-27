CREATE DATABASE IF NOT EXISTS inventory;

CREATE USER 'inventory-username'@'%' IDENTIFIED BY 'inventory-password';
GRANT ALL PRIVILEGES ON inventory.* TO 'inventory-username'@'%';
FLUSH PRIVILEGES;

USE inventory;

create table items
(
    id       int auto_increment
        primary key,
    name     varchar(60) not null,
    quantity int         null,
    price    DECIMAL(10, 2) NOT NULL,
    constraint ix_items_name
        unique (name),
    
);

create index ix_items_id
    on items (id);

