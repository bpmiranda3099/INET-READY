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

    try {
        $conn = new PDO("mysql:host={$dbConfig['host']};dbname={$dbConfig['dbname']}", $dbConfig['username'], $dbConfig['password']);
        $conn->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

        // Begin transaction
        $conn->beginTransaction();

        // Fetch data from LockedUser table
        $lockedUserQuery = "SELECT * FROM LockedUser WHERE user_id = :user_id";  
        $lockedUserStmt = $conn->prepare($lockedUserQuery);
        $lockedUserStmt->execute([':user_id' => $userId]);
        $lockedUserData = $lockedUserStmt->fetch(PDO::FETCH_ASSOC);

        // Insert data into User table
        $userQuery = "INSERT INTO User (user_id, name, username, email, password, salt) VALUES (:user_id, :name, :username, :email, :password, :salt)";
        $userStmt = $conn->prepare($userQuery);
        $userStmt->execute([
            ':user_id' => $lockedUserData['user_id'],
            ':name' => $lockedUserData['name'],
            ':username' => $lockedUserData['username'],
            ':email' => $lockedUserData['email'],
            ':password' => $lockedUserData['password'],
            ':salt' => $lockedUserData['salt']
        ]);

        // Fetch data from LockedUserProfile table
        $lockedUserProfileQuery = "SELECT * FROM LockedUserProfile WHERE user_id = :user_id";
        $lockedUserProfileStmt = $conn->prepare($lockedUserProfileQuery);
        $lockedUserProfileStmt->execute([':user_id' => $userId]);
        $lockedUserProfileData = $lockedUserProfileStmt->fetch(PDO::FETCH_ASSOC);

        // Insert data into UserProfile table
        $userProfileQuery = "INSERT INTO UserProfile (user_id, phone_number, date_of_birth, gender, address, city, state, country, postal_code, profile_picture, bio) VALUES (:user_id, :phone_number, :date_of_birth, :gender, :address, :city, :state, :country, :postal_code, :profile_picture, :bio)";
        $userProfileStmt = $conn->prepare($userProfileQuery);
        $userProfileStmt->execute([
            ':user_id' => $lockedUserProfileData['user_id'],
            ':phone_number' => $lockedUserProfileData['phone_number'],
            ':date_of_birth' => $lockedUserProfileData['date_of_birth'],
            ':gender' => $lockedUserProfileData['gender'],
            ':address' => $lockedUserProfileData['address'],
            ':city' => $lockedUserProfileData['city'],
            ':state' => $lockedUserProfileData['state'],
            ':country' => $lockedUserProfileData['country'],
            ':postal_code' => $lockedUserProfileData['postal_code'],
            ':profile_picture' => $lockedUserProfileData['profile_picture'],
            ':bio' => $lockedUserProfileData['bio']
        ]);

        // Fetch data from LockedUserDevice table
        $lockedUserDeviceQuery = "SELECT * FROM LockedUserDevice WHERE user_id = :user_id";
        $lockedUserDeviceStmt = $conn->prepare($lockedUserDeviceQuery);
        $lockedUserDeviceStmt->execute([':user_id' => $userId]);
        $lockedUserDeviceData = $lockedUserDeviceStmt->fetch(PDO::FETCH_ASSOC);

        // Insert data into UserDevice table
        $userDeviceQuery = "INSERT INTO UserDevice (user_id, device_id, device_type, device_model, os_version, app_version, last_login) VALUES (:user_id, :device_id, :device_type, :device_model, :os_version, :app_version, :last_login)";
        $userDeviceStmt = $conn->prepare($userDeviceQuery);
        $userDeviceStmt->execute([
            ':user_id' => $lockedUserDeviceData['user_id'],
            ':device_id' => $lockedUserDeviceData['device_id'],
            ':device_type' => $lockedUserDeviceData['device_type'],
            ':device_model' => $lockedUserDeviceData['device_model'],
            ':os_version' => $lockedUserDeviceData['os_version'],
            ':app_version' => $lockedUserDeviceData['app_version'],
            ':last_login' => $lockedUserDeviceData['last_login']
        ]);

        // Fetch data from LockedUserPreferences table
        $lockedUserPreferencesQuery = "SELECT * FROM LockedUserPreferences WHERE user_id = :user_id";
        $lockedUserPreferencesStmt = $conn->prepare($lockedUserPreferencesQuery);
        $lockedUserPreferencesStmt->execute([':user_id' => $userId]);
        $lockedUserPreferencesData = $lockedUserPreferencesStmt->fetch(PDO::FETCH_ASSOC);

        // Insert data into UserPreferences table
        $userPreferencesQuery = "INSERT INTO UserPreferences (user_id, language, timezone, notification_enabled) VALUES (:user_id, :language, :timezone, :notification_enabled)";
        $userPreferencesStmt = $conn->prepare($userPreferencesQuery);
        $userPreferencesStmt->execute([
            ':user_id' => $lockedUserPreferencesData['user_id'],
            ':language' => $lockedUserPreferencesData['language'],
            ':timezone' => $lockedUserPreferencesData['timezone'],
            ':notification_enabled' => $lockedUserPreferencesData['notification_enabled']
        ]);

        // Fetch data from LockedUserActivityLog table
        $lockedUserActivityLogQuery = "SELECT * FROM LockedUserActivityLog WHERE user_id = :user_id";
        $lockedUserActivityLogStmt = $conn->prepare($lockedUserActivityLogQuery);
        $lockedUserActivityLogStmt->execute([':user_id' => $userId]);
        $lockedUserActivityLogData = $lockedUserActivityLogStmt->fetch(PDO::FETCH_ASSOC);

        // Insert data into UserActivityLog table
        $userActivityLogQuery = "INSERT INTO UserActivityLog (user_id, activity_type, activity_timestamp, activity_details) VALUES (:user_id, :activity_type, :activity_timestamp, :activity_details)";
        $userActivityLogStmt = $conn->prepare($userActivityLogQuery);
        $userActivityLogStmt->execute([
            ':user_id' => $lockedUserActivityLogData['user_id'],
            ':activity_type' => $lockedUserActivityLogData['activity_type'],
            ':activity_timestamp' => $lockedUserActivityLogData['activity_timestamp'],
            ':activity_details' => $lockedUserActivityLogData['activity_details']
        ]);

        // Commit transaction
        $conn->commit();

    } catch (PDOException $e) {
        // Rollback transaction if something failed
        $conn->rollBack();
        echo "Error: " . $e->getMessage();
    }

    $conn = null;  // Close connection

    try {
        $conn = new PDO("mysql:host={$dbConfig['host']};dbname={$dbConfig['dbname']}", $dbConfig['username'], $dbConfig['password']);
        $conn->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

        // Delete data from LockedUser table
        $deleteLockedUserQuery = "DELETE FROM LockedUser WHERE user_id = :user_id";
        $deleteLockedUserStmt = $conn->prepare($deleteLockedUserQuery);
        $deleteLockedUserStmt->bindParam(':user_id', $userId, PDO::PARAM_STR);
        $deleteLockedUserStmt->execute();

        // Delete data from LockedUserProfile table
        $deleteLockedUserProfileQuery = "DELETE FROM LockedUserProfile WHERE user_id = :user_id";
        $deleteLockedUserProfileStmt = $conn->prepare($deleteLockedUserProfileQuery);
        $deleteLockedUserProfileStmt->bindParam(':user_id', $userId, PDO::PARAM_STR);
        $deleteLockedUserProfileStmt->execute();

        // Delete data from LockedUserDevice table
        $deleteLockedUserDeviceQuery = "DELETE FROM LockedUserDevice WHERE user_id = :user_id";
        $deleteLockedUserDeviceStmt = $conn->prepare($deleteLockedUserDeviceQuery);
        $deleteLockedUserDeviceStmt->bindParam(':user_id', $userId, PDO::PARAM_STR);
        $deleteLockedUserDeviceStmt->execute();

        // Delete data from LockedUserPreferences table
        $deleteLockedUserPreferencesQuery = "DELETE FROM LockedUserPreferences WHERE user_id = :user_id";
        $deleteLockedUserPreferencesStmt = $conn->prepare($deleteLockedUserPreferencesQuery);
        $deleteLockedUserPreferencesStmt->bindParam(':user_id', $userId, PDO::PARAM_STR);
        $deleteLockedUserPreferencesStmt->execute();

        // Delete data from LockedUserActivityLog table
        $deleteLockedUserActivityLogQuery = "DELETE FROM LockedUserActivityLog WHERE user_id = :user_id";
        $deleteLockedUserActivityLogStmt = $conn->prepare($deleteLockedUserActivityLogQuery);
        $deleteLockedUserActivityLogStmt->bindParam(':user_id', $userId, PDO::PARAM_STR);
        $deleteLockedUserActivityLogStmt->execute();

    } catch (PDOException $e) {
        echo "Error: " . $e->getMessage();
    }

    $conn = null;  // Close connection
} else {
    echo "Invalid request.";
}
?>