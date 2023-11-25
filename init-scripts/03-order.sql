CREATE DATABASE IF NOT EXISTS orders;

CREATE USER 'orders-username'@'%' IDENTIFIED BY 'orders-password';
GRANT ALL PRIVILEGES ON orders.* TO 'orders-username'@'%';
FLUSH PRIVILEGES;

USE orders;

create table orders
(
    id     int auto_increment
        primary key,
    user   varchar(60) not null,
    item   varchar(60) not null,
    price  int         not null,
    status varchar(60) not null
);

create index ix_orders_id
    on orders (id);

create index ix_orders_item
    on orders (item);

create index ix_orders_status
    on orders (status);

create index ix_orders_user
    on orders (user);

