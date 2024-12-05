<?php
ini_set('display_errors', 1);
ini_set('display_startup_errors', 1);
error_reporting(E_ALL);

require __DIR__ . '/dbConfig.php';

$dbConfig = [
    'host' => DB_SERVER,
    'username' => DB_USERNAME,
    'password' => DB_PASSWORD,
    'dbname' => DB_DATABASE_TWO,
];

if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['user_id'])) {
    $userId = filter_input(INPUT_POST, 'user_id', FILTER_SANITIZE_STRING);

    if (!$userId) {
        echo "Invalid user ID.";
        exit;
    }

    $conn = null;  // Close connection

    try {
        $conn = new PDO("mysql:host={$dbConfig['host']};dbname={$dbConfig['dbname']}", $dbConfig['username'], $dbConfig['password']);
        $conn->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

        // Delete user data from user table
        $deleteQuery = "DELETE FROM user WHERE user_id = :user_id";
        $deleteStmt = $conn->prepare($deleteQuery);
        $deleteStmt->bindParam(':user_id', $userId, PDO::PARAM_STR);
        $deleteStmt->execute();

    } catch (PDOException $e) {
        echo "Error: " . $e->getMessage();
    }

    $conn = null;  // Close connection
} else {
    echo "Invalid request.";
}
?>