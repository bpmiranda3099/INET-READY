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
    $userQuery = "SELECT * FROM lockeduser";  
    $userStmt = $conn->prepare($userQuery);
    $userStmt->execute();
    $userData = $userStmt->fetchAll(PDO::FETCH_ASSOC);

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
                    <div class="col-12 col-lg-8 col-xxl-12 d-flex"> 
                        <div class="card flex-fill" style="padding: 0px 10px 0px 10px;">
                            <div class="card-header d-flex justify-content-between" style="padding: 15px 15px 0px 10px;">
                                <h5 class="card-title mb-0">Locked User Master List</h5>
                                <form method="POST" action="userManagement.php" class="ms-3 d-flex align-items-right">
                                    <a href="userManagement.php" style="padding-left: 0px; padding-right: 0px; padding-bottom: 10px;" class="btn btn-link">
                                        <i class="align-middle" data-feather="corner-down-left" style="width: 20px; height: 20px;"></i>
                                    </a>
                                </form>
                            </div>
                            <table id="userMasterListTable" class="table table-hover my-0">
                                <thead>
                                    <tr>
                                        <th>Unlock</th>
                                        <th>ID</th>
                                        <th>Username</th>
                                        <th>Password</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <?php if (!empty($userData)): ?>
                                        <?php foreach ($userData as $data): ?>
                                            <tr data-user-id="<?= htmlspecialchars($data['user_id']) ?>">
                                                <td>
                                                    <form method="POST" action="" class="ms-3 d-flex justify-content-left">
                                                        <a onclick="" style="padding-left: 2px; padding-right: 2px;" class="btn btn-link">
                                                            <i class="align-left" data-feather="unlock" style="width: 24px; height: 24px;"></i>
                                                        </a>
                                                    </form>
                                                </td>
                                                <td><?= htmlspecialchars($data['user_id']) ?></td>
                                                <td><?= htmlspecialchars($data['username']) ?></td>
                                                <td><?= htmlspecialchars($data['password']) ?></td> <!-- Ensure this column exists -->
                                            </tr>
                                        <?php endforeach; ?>
                                    <?php endif; ?>
                                </tbody>
                            </table>
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
            document.querySelectorAll('.btn-link').forEach(function(lockButton) {
                lockButton.addEventListener('click', function() {
                    var userId = this.closest('tr').getAttribute('data-user-id');
                    if (userId) {
                        if (confirm('Are you sure you want to unlock this user?')) {
                            var xhr = new XMLHttpRequest();
                            xhr.open('POST', 'unlockUserProcess.php', true);
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