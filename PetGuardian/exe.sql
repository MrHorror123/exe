CREATE DATABASE IF NOT EXISTS `geeklogin` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE `geeklogin`;

CREATE TABLE IF NOT EXISTS `accounts` (
	`id` integer NOT NULL AUTO_INCREMENT,
    `username` varchar(50) NOT NULL,
    `password` varchar(100) NOT NULL,
    `email` varchar(100) NOT NULL,
    PRIMARY KEY (`id`)
) ENGINE = InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET = utf8mb4;
ALTER TABLE accounts ADD COLUMN user_type VARCHAR(50) NOT NULL;

CREATE TABLE pets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    pet_name VARCHAR(100),	
    pet_type VARCHAR(50),
    pet_birthday VARCHAR(50),
    pet_age INT,
    pet_gender VARCHAR(50),
    pet_color VARCHAR(50),
    FOREIGN KEY (user_id) REFERENCES accounts(id)
);
ALTER TABLE pets ADD COLUMN pet_image VARCHAR(255);

CREATE TABLE veterinarian_contacts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    contact_name VARCHAR(100),
    contact_gender VARCHAR(100),	
    contact_language VARCHAR(50),
    contact_phone VARCHAR(100),
    FOREIGN KEY (user_id) REFERENCES accounts(id)
);
