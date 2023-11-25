CREATE DATABASE IF NOT EXISTS orders;

CREATE USER 'orders-username'@'%' IDENTIFIED BY 'orders-password';
GRANT ALL PRIVILEGES ON orders.* TO 'orders-username'@'%';
FLUSH PRIVILEGES;

USE orders;
create or replace table orders
(
    id     int auto_increment
        primary key,
    user   varchar(60) null,
    item   varchar(60) null,
    price  int         null,
    status varchar(60) null
);

create or replace index ix_orders_id
    on orders (id);

create or replace index ix_orders_item
    on orders (item);

create or replace index ix_orders_status
    on orders (status);

create or replace index ix_orders_user
    on orders (user);

