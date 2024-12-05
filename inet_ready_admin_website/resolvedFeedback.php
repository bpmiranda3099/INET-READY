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
    'dbname_two' => DB_DATABASE_FOUR
];

try {
    // Create connection
    $conn = new PDO("mysql:host={$dbConfig['host']};dbname={$dbConfig['dbname']}", $dbConfig['username'], $dbConfig['password']);
    $conn->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

    // Connect to secondary database
    $connTwo = new PDO("mysql:host={$dbConfig['host']};dbname={$dbConfig['dbname_two']}", $dbConfig['username'], $dbConfig['password']);
    $connTwo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

    // Fetch data from userfeedback table
    $userFeedbackQuery = "SELECT * FROM resolveduserfeedback";
    $userFeedbackStmt = $conn->prepare($userFeedbackQuery);
    $userFeedbackStmt->execute();
    $userFeedbackData = $userFeedbackStmt->fetchAll(PDO::FETCH_ASSOC);

    // Fetch data from adminfeedback table
    $adminFeedbackQuery = "SELECT * FROM resolvedadminfeedback";
    $adminFeedbackStmt = $connTwo->prepare($adminFeedbackQuery);
    $adminFeedbackStmt->execute();
    $adminFeedbackData = $adminFeedbackStmt->fetchAll(PDO::FETCH_ASSOC);

    if ($_SERVER['REQUEST_METHOD'] === 'POST') {
        $data = json_decode(file_get_contents('php://input'), true);
        $action = $data['action'];
        $feedbackId = $data['feedbackId'];
        $tableType = $data['tableType'];

        if ($action === 'resolve') {
            if ($tableType === 'userFeedbackTable') {
                $stmt = $conn->prepare("INSERT INTO resolveduserfeedback (feedback_id, user_id, title, category, feedback_message, date_added, time_added) SELECT feedback_id, user_id, title, category, feedback_message, date_added, time_added FROM userfeedback WHERE feedback_id = :feedbackId");
                $stmt->bindParam(':feedbackId', $feedbackId);
                $stmt->execute();

                $stmt = $conn->prepare("DELETE FROM userfeedback WHERE feedback_id = :feedbackId");
                $stmt->bindParam(':feedbackId', $feedbackId);
                $stmt->execute();
            } elseif ($tableType === 'adminFeedbackTable') {
				$stmt = $connTwo->prepare("INSERT INTO resolvedadminfeedback (feedback_id, admin_id, title, category, feedback_message, date_added, time_added) SELECT feedback_id, admin_id, title, category, feedback_message, date_added, time_added FROM adminfeedback WHERE feedback_id = :feedbackId");
                $stmt->bindParam(':feedbackId', $feedbackId);
                $stmt->execute();

                $stmt = $connTwo->prepare("DELETE FROM adminfeedback WHERE feedback_id = :feedbackId");
                $stmt->bindParam(':feedbackId', $feedbackId);
                $stmt->execute();
            }
        } elseif ($action === 'delete') {
            if ($tableType === 'userFeedbackTable') {
                $stmt = $conn->prepare("DELETE FROM userfeedback WHERE feedback_id = :feedbackId");
                $stmt->bindParam(':feedbackId', $feedbackId);
                $stmt->execute();
            } elseif ($tableType === 'adminFeedbackTable') {
                $stmt = $connTwo->prepare("DELETE FROM adminfeedback WHERE feedback_id = :feedbackId");
                $stmt->bindParam(':feedbackId', $feedbackId);
                $stmt->execute();
            }
        }

        echo json_encode(['success' => true]);
        exit;
    }

} catch (PDOException $e) {
    $error = $e->getMessage();
}

$conn = null;
$connTwo = null;
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

					<li class="sidebar-item active">
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

					<li class="sidebar-item">
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
							<h1 class="h3 mb-3"><strong>Resolved User and Administrator</strong> Feedback </h1>
						</div>
						<div class="col">
							<form method="POST" action="" class="ms-3 d-flex justify-content-end">
								<a href="#" onclick="location.reload()" style="padding-left: 2px; padding-right: 2px;" class="btn btn-link">
									<i class="align-middle" data-feather="refresh-cw" style="width: 24px; height: 24px;"></i>
								</a>
								<a href="#" onclick="downloadTableAsCSV()" style="padding-left: 2px; padding-right: 2px;" class="btn btn-link">
									<i class="align-middle" data-feather="download" style="width: 24px; height: 24px;"></i>
								</a>
							</form>
						</div>
					</div>
					<div class="row">
                        <div class="col-12 col-lg-8 col-xxl-12 d-flex"> 
                            <div class="card flex-fill">
                                <div class="card-header">
                                    <select id="tableSelect" class="form-control" onchange="showSelectedTable()">
										<option value="NULL">Select Table</option>
                                        <option value="userFeedbackTable">Resolved User Feedback</option>
                                        <option value="adminFeedbackTable">Resolved Admin Feedback</option>
                                    </select>
                                </div>
                                <div style="max-height: 1500px; auto; border: 1px solid #ddd; padding: 0px 10px 0px 10px;">
                                    <table id="userFeedbackTable" class="table table-hover my-0" style="display: none;">
                                        <thead>
                                            <tr>
                                                <th>Feedback ID</th>
                                                <th>User ID</th>
                                                <th>Title</th>
                                                <th>Category</th>
                                                <th>Feedback Message</th>
                                                <th>Date Added</th>
                                                <th>Time Added</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            <?php if (!empty($userFeedbackData)): ?>
                                                <?php foreach ($userFeedbackData as $data): ?>
                                                    <tr>
                                                        <td class="feedback-id"><?= htmlspecialchars($data['feedback_id']) ?></td>
                                                        <td><?= htmlspecialchars($data['user_id']) ?></td>
                                                        <td><?= htmlspecialchars($data['title']) ?></td>
                                                        <td><?= htmlspecialchars($data['category']) ?></td>
                                                        <td><?= htmlspecialchars($data['feedback_message']) ?></td>
                                                        <td><?= htmlspecialchars($data['date_added']) ?></td>
                                                        <td><?= htmlspecialchars($data['time_added']) ?></td>
                                                    </tr>
                                                <?php endforeach; ?>
                                            <?php else: ?>
                                                <tr>
                                                    <td colspan="8">No user feedback available.</td>
                                                </tr>
                                            <?php endif; ?>
                                        </tbody>
                                    </table>
                                    <table id="adminFeedbackTable" class="table table-hover my-0" style="display: none;">
                                        <thead>
                                            <tr>
                                                <th>Feedback ID</th>
                                                <th>Admin ID</th>
                                                <th>Title</th>
                                                <th>Category</th>
                                                <th>Feedback Message</th>
                                                <th>Date Added</th>
                                                <th>Time Added</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            <?php if (!empty($adminFeedbackData)): ?>
                                                <?php foreach ($adminFeedbackData as $data): ?>
                                                    <tr>
                                                        <td class="feedback-id"><?= htmlspecialchars($data['feedback_id']) ?></td>
                                                        <td><?= htmlspecialchars($data['admin_id']) ?></td>
                                                        <td><?= htmlspecialchars($data['title']) ?></td>
                                                        <td><?= htmlspecialchars($data['category']) ?></td>
                                                        <td><?= htmlspecialchars($data['feedback_message']) ?></td>
                                                        <td><?= htmlspecialchars($data['date_added']) ?></td>
                                                        <td><?= htmlspecialchars($data['time_added']) ?></td>
                                                    </tr>
                                                <?php endforeach; ?>
                                            <?php else: ?>
                                                <tr>
                                                    <td colspan="8">No admin feedback available.</td>
                                                </tr>
                                            <?php endif; ?>
                                        </tbody>
                                    </table>
                                </div>
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
			// Track which table is currently initialized
			let currentTable = null;

			// Function to initialize a DataTable
			function initializeTable(tableId) {
				$('#' + tableId).DataTable({
                    "bAutoWidth": false,
					"pageLength": 10,
					"lengthMenu": [10, 15, 25],
					"columnDefs": tableId === 'userFeedbackTable' ? [
						{
							"targets": '_all',
							"orderable": true
						},
						{
							"targets": '_all',
							"orderable": false
						}
					] : []
				});
			}

			// Listen for table selection changes
			$('#tableSelect').on('change', function() {
				var selectedTable = $(this).val();

				// Destroy the DataTable of the currently active table
				if (currentTable) {
					$('#' + currentTable).DataTable().destroy();
					$('#' + currentTable).hide();
				}

				// Show the selected table and initialize it
				$('#' + selectedTable).show();
				initializeTable(selectedTable);

				// Update the currentTable reference
				currentTable = selectedTable;
			});

			// Hide all tables by default
			$('#userFeedbackTable, #adminFeedbackTable').hide();
		});
	</script>
	<!-- JavaScript to toggle tables -->
	<script>
	function showSelectedTable() {
		var selectedTable = document.getElementById("tableSelect").value;

		// Hide all tables
		document.getElementById("userFeedbackTable").style.display = "none";
		document.getElementById("adminFeedbackTable").style.display = "none";

		// Show the selected table
		document.getElementById(selectedTable).style.display = "table";
	}
	</script>
	<script>
		function downloadTableAsCSV() {
			const selectedTableId = document.getElementById("tableSelect").value;
			if (!selectedTableId || selectedTableId === "NULL") {
				alert("Please select a table to download.");
				return;
			}

			const table = document.getElementById(selectedTableId);
			if (!table || table.style.display === "none") {
				alert("The selected table is not available or visible.");
				return;
			}

			let csvContent = "";
			const rows = table.querySelectorAll("tr");

			rows.forEach((row) => {
				const cols = row.querySelectorAll("th, td");
				const rowContent = Array.from(cols)
					.map(col => `"${col.textContent.trim().replace(/"/g, '""')}"`) // Escape double quotes
					.join(",");
				csvContent += rowContent + "\n";
			});

			const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
			const link = document.createElement("a");
			const fileName = `${selectedTableId}.csv`;

			if (navigator.msSaveBlob) { // For IE 10+
				navigator.msSaveBlob(blob, fileName);
			} else {
				link.href = URL.createObjectURL(blob);
				link.download = fileName;
				link.style.display = "none";
				document.body.appendChild(link);
				link.click();
				document.body.removeChild(link);
			}
		}
	</script>
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            document.querySelectorAll('.check-square').forEach(function(button) {
                button.addEventListener('click', function(event) {
                    event.preventDefault();
                    if (confirm('Are you sure you want to resolve this feedback?')) {
                        const feedbackId = button.getAttribute('data-id');
                        const tableType = button.getAttribute('data-table');

                        fetch('', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json'
                            },
                            body: JSON.stringify({
                                action: 'resolve',
                                feedbackId: feedbackId,
                                tableType: tableType
                            })
                        }).then(response => response.json()).then(data => {
                            if (data.success) {
                                location.reload();
                            } else {
                                alert('Error resolving feedback');
                            }
                        });
                    }
                });
            });

            document.querySelectorAll('.x-square').forEach(function(button) {
                button.addEventListener('click', function(event) {
                    event.preventDefault();
                    if (confirm('Are you sure you want to delete this feedback?')) {
                        const feedbackId = button.getAttribute('data-id');
                        const tableType = button.getAttribute('data-table');

                        fetch('', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json'
                            },
                            body: JSON.stringify({
                                action: 'delete',
                                feedbackId: feedbackId,
                                tableType: tableType
                            })
                        }).then(response => response.json()).then(data => {
                            if (data.success) {
                                location.reload();
                            } else {
                                alert('Error deleting feedback');
                            }
                        });
                    }
                });
            });
        });
        </script>
</body>

</html>