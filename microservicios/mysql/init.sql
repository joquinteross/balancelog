CREATE DATABASE IF NOT EXISTS usuarios1;
CREATE DATABASE IF NOT EXISTS laravel_gateway;

CREATE USER IF NOT EXISTS 'laravel'@'%' IDENTIFIED BY 'laravelpass';

GRANT ALL PRIVILEGES ON usuarios1.* TO 'laravel'@'%';
GRANT ALL PRIVILEGES ON laravel_gateway.* TO 'laravel'@'%';

FLUSH PRIVILEGES;
