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
    'dbname' => DB_DATABASE,
    'dbname_two' => DB_DATABASE_TWO 
];

try {
    // Create connection
    $conn = new PDO("mysql:host={$dbConfig['host']};dbname={$dbConfig['dbname']}", $dbConfig['username'], $dbConfig['password']);
    $conn->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

    // Connect to secondary database
    $connTwo = new PDO("mysql:host={$dbConfig['host']};dbname={$dbConfig['dbname_two']}", $dbConfig['username'], $dbConfig['password']);
    $connTwo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

    // Fetch data from weatherdata table
    $weatherQuery = "SELECT * FROM weatherdata";
    $weatherStmt = $conn->prepare($weatherQuery);
    $weatherStmt->execute();
    $weatherData = $weatherStmt->fetchAll(PDO::FETCH_ASSOC);

    // Fetch data from weatherdataforecast table
    $forecastQuery = "SELECT city, hi_day_one, hi_day_two, hi_day_three, hi_day_four, hi_day_five, hi_day_six, hi_day_seven, date_added, time_added FROM weatherdataforecast";
    $forecastStmt = $conn->prepare($forecastQuery);
    $forecastStmt->execute();
    $forecastData = $forecastStmt->fetchAll(PDO::FETCH_ASSOC);

    // Fetch data from predictedhimetrics table
    $predictedQuery = "SELECT * FROM predictedhimetrics";
    $predictedStmt = $conn->prepare($predictedQuery);
    $predictedStmt->execute();
    $predictedData = $predictedStmt->fetchAll(PDO::FETCH_ASSOC);

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
	<!-- DataTables JS -->
	<script type="text/javascript" charset="utf8" src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
	<script type="text/javascript" charset="utf8" src="https://cdn.datatables.net/1.13.4/js/jquery.dataTables.min.js"></script>

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

					<li class="sidebar-item active">
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
							<h1 class="h3 mb-3"><strong>Weather</strong> Database </h1>
						</div>
						<div class="col">
							<form method="POST" action="" class="ms-3 d-flex justify-content-end">
								<a href="#" onclick="this.closest('form').submit(); return false;" style="padding-left: 2px; padding-right: 2px;" class="btn btn-link">
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
										<option value=NULL>Select Table</option>
										<option value="weatherDataTable">Weather Data</option>
										<option value="forecastDataTable">Heat Index Prediction</option>
										<option value="predictedDataTable">Predicted Heat Index Metrics</option>
									</select>
								</div>
								<div style="max-height: 1500px; auto; border: 1px solid #ddd; padding: 0px 10px 0px 10px;">
								<table id="weatherDataTable" class="table table-hover my-0" style="display: none;">
									<thead>
										<tr>
											<th>City</th>
											<th>Temperature</th>
											<th>Humidity</th>
											<th>Heat Index</th>
											<th>Heat Level</th>
											<th>Date Added</th>
											<th>Time Added</th>
										</tr>
									</thead>
									<tbody>
										<?php if (!empty($weatherData)): ?>
											<?php foreach ($weatherData as $data): ?>
												<tr>
													<td><?= htmlspecialchars($data['city']) ?></td>
													<td><?= htmlspecialchars($data['temperature']) ?></td>
													<td><?= htmlspecialchars($data['humidity']) ?></td>
													<td><?= htmlspecialchars($data['heat_index']) ?></td>
													<td><?= htmlspecialchars($data['heat_level']) ?></td>
													<td><?= htmlspecialchars($data['date_added']) ?></td>
													<td><?= htmlspecialchars($data['time_added']) ?></td>
												</tr>
											<?php endforeach; ?>
										<?php else: ?>
											<tr>
												<td colspan="7">No weather data available.</td>
											</tr>
										<?php endif; ?>
									</tbody>
								</table>
								<table id="forecastDataTable" class="table table-hover my-0" style="display: none;">
									<thead>
										<tr>
											<th>City</th>
											<th><?php echo date('Y-m-d', strtotime('+1 day')); ?></th>
											<th><?php echo date('Y-m-d', strtotime('+2 day')); ?></th>
											<th><?php echo date('Y-m-d', strtotime('+3 day')); ?></th>
											<th><?php echo date('Y-m-d', strtotime('+4 day')); ?></th>
											<th><?php echo date('Y-m-d', strtotime('+5 day')); ?></th>
											<th><?php echo date('Y-m-d', strtotime('+6 day')); ?></th>
											<th><?php echo date('Y-m-d', strtotime('+7 day')); ?></th>
											<th>Date Added</th>
											<th>Time Added</th>
										</tr>
									</thead>
									<tbody>
										<?php if (!empty($forecastData)): ?>
											<?php foreach ($forecastData as $data): ?>
												<tr>
													<td><?= htmlspecialchars($data['city']) ?></td>
													<td><?= htmlspecialchars($data['hi_day_one']) ?></td>
													<td><?= htmlspecialchars($data['hi_day_two']) ?></td>
													<td><?= htmlspecialchars($data['hi_day_three']) ?></td>
													<td><?= htmlspecialchars($data['hi_day_four']) ?></td>
													<td><?= htmlspecialchars($data['hi_day_five']) ?></td>
													<td><?= htmlspecialchars($data['hi_day_six']) ?></td>
													<td><?= htmlspecialchars($data['hi_day_seven']) ?></td>
													<td><?= htmlspecialchars($data['date_added']) ?></td>
													<td><?= htmlspecialchars($data['time_added']) ?></td>
												</tr>
											<?php endforeach; ?>
										<?php else: ?>
											<tr>
												<td colspan="17">No weather data forecast available.</td>
											</tr>
										<?php endif; ?>
									</tbody>
								</table>
								<table id="predictedDataTable" class="table table-hover my-0" style="display: none;">
									<thead>
										<tr>
											<th>City</th>
											<th>Mean Absolute Error</th>
											<th>Mean Squared Error</th>
											<th>R Squared</th>
											<th>Prediction Rating</th>
											<th>Date Added</th>
											<th>Time Added</th>
										</tr>
									</thead>
									<tbody>
										<?php if (!empty($predictedData)): ?>
											<?php foreach ($predictedData as $data): ?>
												<tr>
													<td><?= htmlspecialchars($data['city']) ?></td>
													<td><?= htmlspecialchars($data['mean_absolute_error']) ?></td>
													<td><?= htmlspecialchars($data['mean_squared_error']) ?></td>
													<td><?= htmlspecialchars($data['r_squared']) ?></td>
													<td><?= htmlspecialchars($data['prediction_rating']) ?></td>
													<td><?= htmlspecialchars($data['date_added']) ?></td>
													<td><?= htmlspecialchars($data['time_added']) ?></td>
												</tr>
											<?php endforeach; ?>
										<?php else: ?>
											<tr>
												<td colspan="7">No predicted heat metrics available.</td>
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
	<script>
		$(document).ready(function() {
			// Track which table is currently initialized
			let currentTable = null;

			// Function to initialize a DataTable
			function initializeTable(tableId) {
				$('#' + tableId).DataTable({
					"pageLength": 10,
					"lengthMenu": [10, 15, 25],
					"columnDefs": tableId === 'weatherDataTable' ? [
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
			$('#weatherDataTable, #forecastDataTable, #predictedDataTable').hide();
		});
	</script>
	<!-- JavaScript to toggle tables -->
	<script>
	function showSelectedTable() {
		var selectedTable = document.getElementById("tableSelect").value;

		// Hide all tables
		document.getElementById("weatherDataTable").style.display = "none";
		document.getElementById("forecastDataTable").style.display = "none";
		document.getElementById("predictedDataTable").style.display = "none";

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
</body>

</html>