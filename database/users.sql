CREATE DATABASE swa_v1;

USE swa_v1;

CREATE TABLE users (
    user_id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    f_name VARCHAR(75),
    l_name VARCHAR(75),
    email VARCHAR(255),
    username VARCHAR(75),
    password VARCHAR(20),
    contact_number VARCHAR(20)
);