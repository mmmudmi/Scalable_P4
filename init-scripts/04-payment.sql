CREATE DATABASE IF NOT EXISTS payment;

CREATE USER 'payment-username' @'%' IDENTIFIED BY 'payment-password';

GRANT ALL PRIVILEGES ON payment.* TO 'payment-username' @'%';

FLUSH PRIVILEGES;

USE payment;

create table
    users (
        id int auto_increment primary key,
        username varchar(60) not null,
        credit int not null,
        constraint ix_users_username unique (username)
    );

create table
    payments (
        id int auto_increment primary key,
        user_id int null,
        status varchar(60) not null,
        constraint payments_ibfk_1 foreign key (user_id) references users (id)
    );

create index ix_payments_id on payments (id);

create index user_id on payments (user_id);

create index ix_users_id on users (id);