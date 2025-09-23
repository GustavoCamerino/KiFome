-- Executar como root/admin no MySQL (mysql -u root -p < scripts/mysql_init.sql)

CREATE DATABASE IF NOT EXISTS `kifome` CHARACTER SET utf8 COLLATE utf8_general_ci;

CREATE USER IF NOT EXISTS 'kifome_user'@'localhost' IDENTIFIED BY 'SUA_SENHA_AQUI';
GRANT ALL PRIVILEGES ON `kifome`.* TO 'kifome_user'@'localhost';
FLUSH PRIVILEGES;
