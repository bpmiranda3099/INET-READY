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

        // Fetch data from user table
        $userQuery = "SELECT * FROM user WHERE user_id = :user_id";  
        $userStmt = $conn->prepare($userQuery);
        $userStmt->execute([':user_id' => $userId]);
        $userData = $userStmt->fetch(PDO::FETCH_ASSOC);

        // Insert data into LockedUser table
        $lockedUserQuery = "INSERT INTO LockedUser (user_id, name, username, email, password, salt) VALUES (:user_id, :name, :username, :email, :password, :salt)";
        $lockedUserStmt = $conn->prepare($lockedUserQuery);
        $lockedUserStmt->execute([
            ':user_id' => $userData['user_id'],
            ':name' => $userData['name'],
            ':username' => $userData['username'],
            ':email' => $userData['email'],
            ':password' => $userData['password'],
            ':salt' => $userData['salt']
        ]);

        // Fetch data from userprofile table
        $userprofileQuery = "SELECT * FROM userprofile WHERE user_id = :user_id";
        $userprofileStmt = $conn->prepare($userprofileQuery);
        $userprofileStmt->execute([':user_id' => $userId]);
        $userProfileData = $userprofileStmt->fetch(PDO::FETCH_ASSOC);

        // Insert data into LockedUserProfile table
        $lockedUserProfileQuery = "INSERT INTO LockedUserProfile (user_id, phone_number, date_of_birth, gender, address, city, state, country, postal_code, profile_picture, bio) VALUES (:user_id, :phone_number, :date_of_birth, :gender, :address, :city, :state, :country, :postal_code, :profile_picture, :bio)";
        $lockedUserProfileStmt = $conn->prepare($lockedUserProfileQuery);
        $lockedUserProfileStmt->execute([
            ':user_id' => $userProfileData['user_id'],
            ':phone_number' => $userProfileData['phone_number'],
            ':date_of_birth' => $userProfileData['date_of_birth'],
            ':gender' => $userProfileData['gender'],
            ':address' => $userProfileData['address'],
            ':city' => $userProfileData['city'],
            ':state' => $userProfileData['state'],
            ':country' => $userProfileData['country'],
            ':postal_code' => $userProfileData['postal_code'],
            ':profile_picture' => $userProfileData['profile_picture'],
            ':bio' => $userProfileData['bio']
        ]);

        // Fetch data from userdevice table
        $userDeviceQuery = "SELECT * FROM userdevice WHERE user_id = :user_id";
        $userDeviceStmt = $conn->prepare($userDeviceQuery);
        $userDeviceStmt->execute([':user_id' => $userId]);
        $userDeviceData = $userDeviceStmt->fetch(PDO::FETCH_ASSOC);

        // Insert data into LockedUserDevice table
        $lockedUserDeviceQuery = "INSERT INTO LockedUserDevice (user_id, device_id, device_type, device_model, os_version, app_version, last_login) VALUES (:user_id, :device_id, :device_type, :device_model, :os_version, :app_version, :last_login)";
        $lockedUserDeviceStmt = $conn->prepare($lockedUserDeviceQuery);
        $lockedUserDeviceStmt->execute([
            ':user_id' => $userDeviceData['user_id'],
            ':device_id' => $userDeviceData['device_id'],
            ':device_type' => $userDeviceData['device_type'],
            ':device_model' => $userDeviceData['device_model'],
            ':os_version' => $userDeviceData['os_version'],
            ':app_version' => $userDeviceData['app_version'],
            ':last_login' => $userDeviceData['last_login']
        ]);

        // Fetch data from userpreferences table
        $userPreferencesQuery = "SELECT * FROM userpreferences WHERE user_id = :user_id";
        $userPreferencesStmt = $conn->prepare($userPreferencesQuery);
        $userPreferencesStmt->execute([':user_id' => $userId]);
        $userPreferencesData = $userPreferencesStmt->fetch(PDO::FETCH_ASSOC);

        // Insert data into LockedUserPreferences table
        $lockedUserPreferencesQuery = "INSERT INTO LockedUserPreferences (user_id, language, timezone, notification_enabled) VALUES (:user_id, :language, :timezone, :notification_enabled)";
        $lockedUserPreferencesStmt = $conn->prepare($lockedUserPreferencesQuery);
        $lockedUserPreferencesStmt->execute([
            ':user_id' => $userPreferencesData['user_id'],
            ':language' => $userPreferencesData['language'],
            ':timezone' => $userPreferencesData['timezone'],
            ':notification_enabled' => $userPreferencesData['notification_enabled']
        ]);

        // Fetch data from useractivitylog table
        $userActivityLogQuery = "SELECT * FROM useractivitylog WHERE user_id = :user_id";
        $userActivityLogStmt = $conn->prepare($userActivityLogQuery);
        $userActivityLogStmt->execute([':user_id' => $userId]);
        $userActivityLogData = $userActivityLogStmt->fetch(PDO::FETCH_ASSOC);

        // Insert data into LockedUserActivityLog table
        $lockedUserActivityLogQuery = "INSERT INTO LockedUserActivityLog (user_id, activity_type, activity_timestamp, activity_details) VALUES (:user_id, :activity_type, :activity_timestamp, :activity_details)";
        $lockedUserActivityLogStmt = $conn->prepare($lockedUserActivityLogQuery);
        $lockedUserActivityLogStmt->execute([
            ':user_id' => $userActivityLogData['user_id'],
            ':activity_type' => $userActivityLogData['activity_type'],
            ':activity_timestamp' => $userActivityLogData['activity_timestamp'],
            ':activity_details' => $userActivityLogData['activity_details']
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