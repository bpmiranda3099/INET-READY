<?php
ini_set('display_errors', 1);
ini_set('display_startup_errors', 1);
error_reporting(E_ALL);

// Database connection details
require __DIR__ . '/dbConfig.php';

$dbConfig = [
    'host' => DB_SERVER,
    'username' => DB_USERNAME,
    'password' => DB_PASSWORD,
    'dbname' => DB_DATABASE_TWO,
];

try {
    // Create connection
    $conn = new PDO("mysql:host={$dbConfig['host']};dbname={$dbConfig['dbname']}", $dbConfig['username'], $dbConfig['password']);
    $conn->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

    // Fetch data from user table
    $userQuery = "SELECT * FROM user";  
    $userStmt = $conn->prepare($userQuery);
    $userStmt->execute();
    $userData = $userStmt->fetchAll(PDO::FETCH_ASSOC);

    // Fetch data from userprofile table
    $userprofileQuery = "SELECT * FROM userprofile";
    $userprofileStmt = $conn->prepare($userprofileQuery);
    $userprofileStmt->execute();
    $userProfileData = $userprofileStmt->fetchAll(PDO::FETCH_ASSOC);

    // Fetch data from preferences table
    $userPreferencesQuery = "SELECT * FROM userpreferences";
    $userPreferencesStmt = $conn->prepare($userPreferencesQuery);
    $userPreferencesStmt->execute();
    $userPreferencesData = $userPreferencesStmt->fetchAll(PDO::FETCH_ASSOC);

    // Fetch data from userdevice table
    $userDeviceQuery = "SELECT * FROM userdevice";
    $userDeviceStmt = $conn->prepare($userDeviceQuery);
    $userDeviceStmt->execute();
    $userDeviceData = $userDeviceStmt->fetchAll(PDO::FETCH_ASSOC);

    // Fetch data from useractivitylog table
    $userActivityLogQuery = "SELECT * FROM useractivitylog";
    $userActivityLogStmt = $conn->prepare($userActivityLogQuery);
    $userActivityLogStmt->execute();
    $userActivityLogData = $userActivityLogStmt->fetchAll(PDO::FETCH_ASSOC);


} catch (PDOException $e) {
    $error = $e->getMessage();
    echo "Connection failed: " . $error;
}

$conn = null;  // Close connection
?>

<!DOCTYPE html>
<html lang="en">

<head>
	<meta charset="utf-8">
	<meta http-equiv="X-UA-Compatible" content="IE=edge">
	<meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
	<meta name="description" content="Responsive Admin &amp; Dashboard Template based on Bootstrap 5">
	<meta name="author" content="INET-READY">
	<meta name="keywords" content="INET-READY, bootstrap, bootstrap 5, admin, dashboard, template, responsive, css, sass, html, theme, front-end, ui kit, web">

	<link rel="preconnect" href="https://fonts.gstatic.com">
	<link rel="shortcut icon" href="img/icons/icon-48x48.png" />

	<link rel="canonical" href="https://demo-basic.INET-READY.io/" />

	<!-- DataTables CSS -->
	<link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.13.4/css/jquery.dataTables.min.css">

	<title>INET-READY</title>

	<link href="css/app.css" rel="stylesheet">
	<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap" rel="stylesheet">
	<style>
		.swiper-container {
			height: 250px; 
			overflow: hidden;
		}

		.swiper-slide {
			display: flex;
			justify-content: center;
			align-items: center;
			height: 100%; 
		}

		.swiper-slide canvas {
			width: 100% !important; 
			height: auto !important; 
		}

		@media (max-width: 768px) {
			.swiper-container {
				height: 200px; 
			}
		}

		@media (max-width: 576px) {
			.swiper-container {
				height: 150px; 
			}
		}
	</style>
</head>

<body>
	<div class="wrapper">
	<nav id="sidebar" class="sidebar js-sidebar" style="padding-top: 20px;">
			<div class="sidebar-content js-simplebar">
				<a class="sidebar-brand" href="index.php">
			<br>
			<br>
          <span class="align-middle">INET-READY /<span style="font-weight: normal;">/ Admin</span></span>
        </a>

				<ul class="sidebar-nav">
					<li class="sidebar-header">
						Pages
					</li>

					<li class="sidebar-item">
						<a class="sidebar-link" href="index.php">
              <i class="align-middle" data-feather="sliders"></i> <span class="align-middle">Dashboard</span>
            </a>
					</li>

					<li class="sidebar-item">
						<a class="sidebar-link" href="weatherDatabase.php">
              <i class="align-middle" data-feather="sun"></i> <span class="align-middle">Weather Database</span>
            </a>
					</li>

					<li class="sidebar-item">
						<a class="sidebar-link" href="weatherHistory.php">
              <i class="align-middle" data-feather="book-open"></i> <span class="align-middle">Weather History</span>
            </a>
					</li>

					<li class="sidebar-item">
						<a class="sidebar-link" href="resolvedFeedback.php">
              <i class="align-middle" data-feather="user-check"></i> <span class="align-middle">Resolved Feedback</span>
            </a>
					</li>

					<li class="sidebar-header">
						Manage 
					</li>

					<li class="sidebar-item">
						<a class="sidebar-link" href="ehr.php">
              <i class="align-middle" data-feather="activity"></i> <span class="align-middle">Electronic Health Record</span>
            </a>
					</li>

					<li class="sidebar-item active">
						<a class="sidebar-link" href="userManagement.php">
              <i class="align-middle" data-feather="users"></i> <span class="align-middle">User Management</span>
            </a>
					</li>

                    <li class="sidebar-item">
						<a class="sidebar-link" href="userAdminFeedback.php">
              <i class="align-middle" data-feather="user-plus"></i> <span class="align-middle">User/Admin Feedback</span>
            </a>
					</li>

					<li class="sidebar-header">
						Account
					</li>

					<li class="sidebar-item">
						<a class="sidebar-link" href="pages-profile.html">
              <i class="align-middle" data-feather="user"></i> <span class="align-middle">Profile</span>
            </a>
					</li>

					<li class="sidebar-item">
						<a class="sidebar-link" href="pages-profile.html">
              <i class="align-middle" data-feather="settings"></i> <span class="align-middle">Settings</span>
            </a>
					</li>

					<li class="sidebar-item">
						<a class="sidebar-link" href="pages-sign-out.html">
              <i class="align-middle" data-feather="log-out"></i> <span class="align-middle">Log Out</span>
            </a>
					</li>

				</ul>
			</div>
		</nav>

		<div class="main">
			<nav class="navbar navbar-expand navbar-light navbar-bg">
				<a class="sidebar-toggle js-sidebar-toggle">
          <i class="hamburger align-self-center"></i>
        </a>

		<div class="navbar-collapse collapse">
					<ul class="navbar-nav navbar-align">
						</li>
					
						<li class="nav-item dropdown">
              </a>

							<a class="nav-link d-none d-sm-inline-block" href="#" data-bs-toggle="dropdown">
                			<span class="text-dark">Charles Rool - <strong>Admin</strong></span>
              </a>
						</li>
					</ul>
				</div>
			</nav>

			<main class="content">
				<div class="container-fluid p-0">
					
                <div class="row">
                    <div class="col">
                        <h1 class="h3 mb-3"><strong>User</strong> Management</h1>
                    </div>
                    <div class="col">
                        <form method="POST" action="" class="ms-3 d-flex justify-content-end">
                            <a href="#" onclick="this.closest('form').submit(); return false;" style="padding-left: 2px; padding-right: 2px;" class="btn btn-link">
                                <i class="align-middle" data-feather="refresh-cw" style="width: 24px; height: 24px;"></i>
                            </a>
                        </form>
                    </div>
                </div>
				<div class="row">
                    <div class="col-12 col-lg-8 col-xxl-5 d-flex"> 
                    <div class="card flex-fill" style="padding: 0px 10px 0px 10px;">
                            <div class="card-header d-flex justify-content-between" style="padding: 15px 15px 0px 10px;">
                                <h5 class="card-title mb-0">User Master List</h5>
                                <form method="POST" action="unlockUser.php" class="ms-3 d-flex align-items-right">
                                    <a href="unlockUser.php" style="padding-left: 0px; padding-right: 0px; padding-bottom: 10px;" class="btn btn-link">
                                        <i class="align-middle" data-feather="unlock" style="width: 20px; height: 20px;"></i>
                                    </a>
                                </form>
                            </div>
                            <table id="userMasterListTable" class="table table-hover my-0">
                                <thead>
                                    <tr>
                                        <th>Modify</th>
                                        <th>ID</th>
                                        <th>Username</th>
                                        <th>Password</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <?php if (!empty($userData)): ?>
                                        <?php foreach ($userData as $data): ?>
                                            <tr data-user-id="<?= htmlspecialchars($data['user_id']) ?>">
                                                <td style="padding-left: 0px; padding-right: 0px;">
                                                <div class="d-flex">
                                                    <form method="POST" action="" class="ms-3 d-flex justify-content-left">
                                                        <a onclick="" style="padding-left: 0px; padding-right: 0px;" class="btn btn-link lock-user">
                                                            <i class="align-left" data-feather="lock" style="width: 20px; height: 20px;"></i>
                                                        </a>
                                                    </form>
                                                    <form method="POST" action="" class="ms-3 d-flex justify-content-left">
                                                        <a onclick="" style="padding-left: 0px; padding-right: 0px;" class="btn btn-link delete-user">
                                                            <i class="align-left" data-feather="x-square" style="width: 20px; height: 20px;"></i>
                                                        </a>
                                                    </form>
                                                </div>
                                                </td>
                                                <td><?= htmlspecialchars($data['user_id']) ?></td>
												<td style="word-break: break-all;"><?= htmlspecialchars(hash('sha256', $data['username'])) ?></td>
												<td style="word-break: break-all;"><?= htmlspecialchars(hash('sha256', $data['password'])) ?></td>
                                            </tr>
                                        <?php endforeach; ?>
                                    <?php else: ?>
                                        <tr>
                                            <td colspan="4">No user data available.</td>
                                        </tr>
                                    <?php endif; ?>
                                </tbody>
                            </table>
                        </div>
                    </div>
					<div class="col-12 col-lg-8 col-xxl-7 d-flex">
						<div class="card flex-fill" id="user-details">
							<div class="card-header">
								<h5 class="card-title">User's Personal Data</h5>
							</div>
							<br>
							<br>
							<span class="text-muted text-center">Click a row from the master list to display data.</span>
							<!-- User details tables will be dynamically inserted here -->
						</div>
					</div>
				</div>
				</div>
			</main>

			<footer class="footer">
				<div class="container-fluid">
					<div class="row text-muted">
						<div class="col-6 text-start">
							<p class="mb-0">
								<a class="text-muted" href="https://INET-READY.io/" target="_blank"><strong>INET-READY</strong></a>								&copy;
							</p>
						</div>
						<div class="col-6 text-end">
							<ul class="list-inline">
								<li class="list-inline-item">
									<a class="text-muted" href="https://INET-READY.io/" target="_blank">Support</a>
								</li>
								<li class="list-inline-item">
									<a class="text-muted" href="https://INET-READY.io/" target="_blank">Help Center</a>
								</li>
								<li class="list-inline-item">
									<a class="text-muted" href="https://INET-READY.io/" target="_blank">Privacy</a>
								</li>
								<li class="list-inline-item">
									<a class="text-muted" href="https://INET-READY.io/" target="_blank">Terms</a>
								</li>
							</ul>
						</div>
					</div>
				</div>
			</footer>
		</div>
	</div>

	<script src="js/app.js"></script>
	<!-- JavaScript to toggle tables -->
	<script src="https://code.jquery.com/jquery-3.5.1.min.js"></script>
    <script src="https://cdn.datatables.net/1.10.21/js/jquery.dataTables.min.js"></script>
    <script>
        $(document).ready(function() {
            $('#userMasterListTable').DataTable({
                "bAutoWidth": false,
                "error": function(settings, helpPage, message) {
                    console.log(message); // Log the error message to the console instead of showing the alert
                }
            });
        });
    </script>
	<script>
		document.addEventListener('DOMContentLoaded', function() {
			const rows = document.querySelectorAll('tr[data-user-id]');
			rows.forEach(row => {
				row.addEventListener('click', function() {
					const userId = this.getAttribute('data-user-id');
					fetchUserData(userId);
				});
			});
		});

		function fetchUserData(userId) {
			// Filter data for the selected user
			const user = <?= json_encode($userData) ?>.find(user => user.user_id == userId);
			const userProfile = <?= json_encode($userProfileData) ?>.find(data => data.user_id == userId);
			const userPreferences = <?= json_encode($userPreferencesData) ?>.find(data => data.user_id == userId);
			const userDevice = <?= json_encode($userDeviceData) ?>.find(data => data.user_id == userId);
			const userActivityLog = <?= json_encode($userActivityLogData) ?>.find(data => data.user_id == userId);

			displayUserData({ user, userProfile, userPreferences, userDevice, userActivityLog});
		}

		function displayUserData(data) {
			const userDetails = document.getElementById('user-details');
			userDetails.innerHTML = `
				<div class="card-header">
					<h5 class="card-title">User's Personal Data</h5>
				</div>
				<div class="card-header">
					<h5 class="card-title">User Profile</h5>
				</div>
				<table class="table table-hover my-0">
					<thead>
						<tr>
							<th>Phone Number</th>
                            <th>Date of Birth</th>
							<th>Gender</th>
                            <th>Address</th>
                            <th>City</th>
                            <th>State</th>
                            <th>Country</th>
                            <th>Postal Code</th>
						</tr>
					</thead>
					<tbody>
						<tr>
							<td>${data.userProfile.phone_number}</td>
							<td>${data.userProfile.date_of_birth}</td>
                            <td>${data.userProfile.gender}</td>
                            <td>${data.userProfile.address}</td>
                            <td>${data.userProfile.city}</td>
                            <td>${data.userProfile.state}</td>
                            <td>${data.userProfile.country}</td>
                            <td>${data.userProfile.postal_code}</td>
						</tr>
					</tbody>
				</table>
				<div class="card-header">
					<h5 class="card-title">User Preferences</h5>
				</div>
				<table class="table table-hover my-0">
					<thead>
						<tr>
							<th>Timezone</th>
							<th>Language</th>
                            <th>Notification Enabled</th>
						</tr>
					</thead>
					<tbody>
                        <tr>
							<td>${data.userPreferences.timezone}</td>
							<td>${data.userPreferences.language}</td>
                            <td>${data.userPreferences.notification_enabled ? 'Yes' : 'No'}</td>
						</tr>
					</tbody>
				</table>
				<div class="card-header">
					<h5 class="card-title">User Device</h5>
				</div>
				<table class="table table-hover my-0">
					<thead>
						<tr>
							<th>Device ID</th>
							<th>Device Type</th>
							<th>Device Model</th>
							<th>OS Version</th>
							<th>App Version</th>
							<th>Last Login</th>
						</tr>
					</thead>
					<tbody>
						<tr>
							<td>${data.userDevice.device_id}</td>
							<td>${data.userDevice.device_type}</td>
							<td>${data.userDevice.device_model}</td>
							<td>${data.userDevice.os_version}</td>
							<td>${data.userDevice.app_version}</td>
							<td>${data.userDevice.last_login}</td>
						</tr>
					</tbody>
				</table>
				<div class="card-header">
					<h5 class="card-title">Activity Log</h5>
				</div>
				<table class="table table-hover my-0">
					<thead>
						<tr>
							<th>Activity Type</th>
							<th>Activity Timestamp</th>
							<th>Activity Details</th>
						</tr>
					</thead>
					<tbody>
						<tr>
							<td>${data.userActivityLog.activity_type}</td>
							<td>${data.userActivityLog.activity_timestamp}</td>
							<td>${data.userActivityLog.activity_details}</td>
						</tr>
					</tbody>
				</table>
			`;
		}
	</script>
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            document.querySelectorAll('.lock-user').forEach(function(lockButton) {
                lockButton.addEventListener('click', function() {
                    var userId = this.closest('tr').getAttribute('data-user-id');
                    if (userId) {
                        if (confirm('Warning: Are you sure you want to lock this user?')) {
                            var xhr = new XMLHttpRequest();
                            xhr.open('POST', 'lockUserProcess.php', true);
                            xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
                            xhr.onreadystatechange = function() {
                                if (xhr.readyState === 4 && xhr.status === 200) {
                                    location.reload();
                                }
                            };
                            xhr.send('user_id=' + userId);
                        }
                    }
                });
            });

            document.querySelectorAll('.delete-user').forEach(function(deleteButton) {
                deleteButton.addEventListener('click', function() {
                    var userId = this.closest('tr').getAttribute('data-user-id');
                    if (userId) {
                        if (confirm('Warning: Are you sure you want to delete this user? This action cannot be undone.')) {
                            var xhr = new XMLHttpRequest();
                            xhr.open('POST', 'deleteUserProcess.php', true);
                            xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
                            xhr.onreadystatechange = function() {
                                if (xhr.readyState === 4 && xhr.status === 200) {
                                    location.reload();
                                }
                            };
                            xhr.send('user_id=' + userId);
                        }
                    }
                });
            });
        });
    </script>
   
</body>

</html>