<!-- SQL setup: -->
<!-- CREATE TABLE `media` (media_id INT PRIMARY KEY AUTO_INCREMENT, media_data BLOB) ENGINE = InnoDB; -->

<?php

use .env;
(new DotEnv(__DIR__ . '/.env'))->load();
echo get('PASSWORD');

define('DB_NAME', 'test_company');
define('DB_USER', 'test_user');
define('DB_PASSWORD', 'PASSWORD');
define('DB_HOST', 'localhost');

$pdo = new PDO("mysql:host=" . DB_HOST . "; dbname=" . DB_NAME, DB_USER, DB_PASSWORD);
$pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
$pdo->setAttribute(PDO::ATTR_EMULATE_PREPARES, false);