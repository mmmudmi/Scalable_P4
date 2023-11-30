CREATE DATABASE IF NOT EXISTS delivery;

CREATE USER
    'delivery-username' @'%' IDENTIFIED BY 'delivery-password';

GRANT ALL PRIVILEGES ON delivery.* TO 'delivery-username' @'%';

FLUSH PRIVILEGES;

USE delivery;

create table
    deliveries (
        id int auto_increment primary key,
        username varchar(60) not null,
        status varchar(60) not null
    );

create index ix_deliveries_id on deliveries (id);

create index ix_deliveries_status on deliveries (status);

create index ix_deliveries_username on deliveries (username);