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
    'dbname' => DB_DATABASE_THREE,
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

    // Fetch data from demographics table
    $demographicsQuery = "SELECT * FROM demographics";
    $demographicsStmt = $conn->prepare($demographicsQuery);
    $demographicsStmt->execute();
    $demographicsData = $demographicsStmt->fetchAll(PDO::FETCH_ASSOC);

    // Fetch data from biometrics table
    $biometricsQuery = "SELECT * FROM biometrics";
    $biometricsStmt = $conn->prepare($biometricsQuery);
    $biometricsStmt->execute();
    $biometricsData = $biometricsStmt->fetchAll(PDO::FETCH_ASSOC);

    // Fetch data from medical conditions table
    $medicalConditionsQuery = "SELECT * FROM medicalconditions";
    $medicalConditionsStmt = $conn->prepare($medicalConditionsQuery);
    $medicalConditionsStmt->execute();
    $medicalConditionsData = $medicalConditionsStmt->fetchAll(PDO::FETCH_ASSOC);

    // Fetch data from medications table
    $medicationsQuery = "SELECT * FROM medications";
    $medicationsStmt = $conn->prepare($medicationsQuery);
    $medicationsStmt->execute();
    $medicationsData = $medicationsStmt->fetchAll(PDO::FETCH_ASSOC);

    // Fetch data from fluid intake table
    $fluidIntakeQuery = "SELECT * FROM fluidintake";
    $fluidIntakeStmt = $conn->prepare($fluidIntakeQuery);
    $fluidIntakeStmt->execute();
    $fluidIntakeData = $fluidIntakeStmt->fetchAll(PDO::FETCH_ASSOC);

    // Fetch data from heat conditions table
    $heatConditionsQuery = "SELECT * FROM heatconditions";
    $heatConditionsStmt = $conn->prepare($heatConditionsQuery);
    $heatConditionsStmt->execute();
    $heatConditionsData = $heatConditionsStmt->fetchAll(PDO::FETCH_ASSOC);

    // Fetch data from activity table
    $activityQuery = "SELECT * FROM activity";
    $activityStmt = $conn->prepare($activityQuery);
    $activityStmt->execute();
    $activityData = $activityStmt->fetchAll(PDO::FETCH_ASSOC);

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

					<li class="sidebar-item active">
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
                        <h1 class="h3 mb-3"><strong>Electronic Health Record</strong> Database</h1>
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
					<div class="col-12 col-lg-8 col-xxl-4 d-flex"> 
						<div class="card flex-fill">
							<div class="card-header">
								<h5 class="card-title">User Master List</h5>
							</div>
							<table id="userMasterListTable" class="table table-hover my-0">
								<thead>
									<tr>
										<th>ID</th>
										<th>Username</th>
										<th>Location</th>
									</tr>
								</thead>
								<tbody>
									<?php if (!empty($userData)): ?>
										<?php foreach ($userData as $data): ?>
												<tr data-user-id="<?= htmlspecialchars($data['user_id']) ?>">
												<td><?= htmlspecialchars($data['user_id']) ?></td>
												<td style="word-break: break-all;"><?= htmlspecialchars(hash('sha256', $data['username'])) ?></td>
												<td><?= htmlspecialchars($data['location']) ?></td>
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
					<div class="col-12 col-lg-8 col-xxl-8 d-flex">
						<div class="card flex-fill" id="user-details">
							<div class="card-header">
								<h5 class="card-title">User's Electronic Health Record</h5>
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
			const demographics = <?= json_encode($demographicsData) ?>.find(data => data.user_id == userId);
			const biometrics = <?= json_encode($biometricsData) ?>.find(data => data.user_id == userId);
			const medicalConditions = <?= json_encode($medicalConditionsData) ?>.find(data => data.user_id == userId);
			const medications = <?= json_encode($medicationsData) ?>.find(data => data.user_id == userId);
			const fluidIntake = <?= json_encode($fluidIntakeData) ?>.find(data => data.user_id == userId);
			const heatConditions = <?= json_encode($heatConditionsData) ?>.find(data => data.user_id == userId);
			const activity = <?= json_encode($activityData) ?>.find(data => data.user_id == userId);

			displayUserData({ user, demographics, biometrics, medicalConditions, medications, fluidIntake, heatConditions, activity });
		}

		function displayUserData(data) {
			const userDetails = document.getElementById('user-details');
			userDetails.innerHTML = `
				<div class="card-header">
					<h5 class="card-title">User's Electronic Health Record</h5>
				</div>
				<div class="card-header">
					<h5 class="card-title">User Demographics</h5>
				</div>
				<table class="table table-hover my-0">
					<thead>
						<tr>
							<th>Age</th>
							<th>Gender</th>
						</tr>
					</thead>
					<tbody>
						<tr>
							<td>${data.demographics.age}</td>
							<td>${data.demographics.gender}</td>
						</tr>
					</tbody>
				</table>
				<div class="card-header">
					<h5 class="card-title">User Biometrics</h5>
				</div>
				<table class="table table-hover my-0">
					<thead>
						<tr>
							<th>Height (m)</th>
							<th>Weight (kg)</th>
						</tr>
					</thead>
					<tbody>
						<tr>
							<td>${data.biometrics.height}</td>
							<td>${data.biometrics.weight}</td>
						</tr>
					</tbody>
				</table>
				<div class="card-header">
					<h5 class="card-title">User Medical Conditions</h5>
				</div>
				<table class="table table-hover my-0">
					<thead>
						<tr>
							<th>Cardiovascular Disease</th>
							<th>Diabetes</th>
							<th>Respiratory Issues</th>
							<th>Heat Sensitivity</th>
							<th>Kidney Disease</th>
							<th>Neurological Disorders</th>
							<th>Other Condition</th>
						</tr>
					</thead>
					<tbody>
						<tr>
							<td>${data.medicalConditions.cardiovascular_disease ? 'Yes' : 'No'}</td>
							<td>${data.medicalConditions.diabetes ? 'Yes' : 'No'}</td>
							<td>${data.medicalConditions.respiratory_issues ? 'Yes' : 'No'}</td>
							<td>${data.medicalConditions.heat_sensitivity ? 'Yes' : 'No'}</td>
							<td>${data.medicalConditions.kidney_disease ? 'Yes' : 'No'}</td>
							<td>${data.medicalConditions.neurological_disorders ? 'Yes' : 'No'}</td>
							<td>${data.medicalConditions.other_condition}</td>
						</tr>
					</tbody>
				</table>
				<div class="card-header">
					<h5 class="card-title">User Medications</h5>
				</div>
				<table class="table table-hover my-0">
					<thead>
						<tr>
							<th>Diuretics</th>
							<th>Blood Pressure Medications</th>
							<th>Antihistamines</th>
							<th>Antidepressants</th>
							<th>Antipsychotics</th>
							<th>Other Medication</th>
						</tr>
					</thead>
					<tbody>
						<tr>
							<td>${data.medications.diuretics ? 'Yes' : 'No'}</td>
							<td>${data.medications.blood_pressure_medications ? 'Yes' : 'No'}</td>
							<td>${data.medications.antihistamines ? 'Yes' : 'No'}</td>
							<td>${data.medications.antidepressants ? 'Yes' : 'No'}</td>
							<td>${data.medications.antipsychotics ? 'Yes' : 'No'}</td>
							<td>${data.medications.other_medication}</td>
						</tr>
					</tbody>
				</table>
				<div class="card-header">
					<h5 class="card-title">User Fluid Intake</h5>
				</div>
				<table class="table table-hover my-0">
					<thead>
						<tr>
							<th>Water</th>
							<th>Electrolyte Drinks</th>
							<th>Coconut Water</th>
							<th>Fruit Juice</th>
							<th>Iced Tea</th>
							<th>Soda</th>
							<th>Milk Tea</th>
							<th>Coffee</th>
							<th>Herbal Tea</th>
							<th>Other Fluid</th>
							<th>Other Fluid Amount</th>
						</tr>
					</thead>
					<tbody>
						<tr>
							<td>${data.fluidIntake.water_amount}</td>
							<td>${data.fluidIntake.electrolyte_drinks_amount}</td>
							<td>${data.fluidIntake.coconut_water_amount}</td>
							<td>${data.fluidIntake.fruit_juice_amount}</td>
							<td>${data.fluidIntake.iced_tea_amount}</td>
							<td>${data.fluidIntake.soda_amount}</td>
							<td>${data.fluidIntake.milk_tea_amount}</td>
							<td>${data.fluidIntake.coffee_amount}</td>
							<td>${data.fluidIntake.herbal_tea_amount}</td>
							<td>${data.fluidIntake.other_fluid}</td>
							<td>${data.fluidIntake.other_fluid_amount}</td>
						</tr>
					</tbody>
				</table>
				<div class="card-header">
					<h5 class="card-title">User Heat Conditions</h5>
				</div>
				<table class="table table-hover my-0">
					<thead>
						<tr>
							<th>Mild Dehydration</th>
							<th>Heat Rash</th>
							<th>Heat Stroke</th>
							<th>Muscle Fatigue</th>
							<th>Heat Syncope</th>
							<th>Heat Edema</th>
						</tr>
					</thead>
					<tbody>
						<tr>
							<td>${data.heatConditions.mild_dehydration ? 'Yes' : 'No'}</td>
							<td>${data.heatConditions.heat_rash ? 'Yes' : 'No'}</td>
							<td>${data.heatConditions.heat_stroke ? 'Yes' : 'No'}</td>
							<td>${data.heatConditions.muscle_fatigue ? 'Yes' : 'No'}</td>
							<td>${data.heatConditions.heat_syncope ? 'Yes' : 'No'}</td>
							<td>${data.heatConditions.heat_edema ? 'Yes' : 'No'}</td>
						</tr>
					</tbody>
				</table>
				<div class="card-header">
					<h5 class="card-title">User Activity</h5>
				</div>
				<table class="table table-hover my-0">
					<thead>
						<tr>
							<th>Previous Heat Issues</th>
							<th>Heat Issues Details</th>
							<th>Outdoor Activity</th>
							<th>Activity Level</th>
							<th>Activity Duration</th>
						</tr>
					</thead>
					<tbody>
						<tr>
							<td>${data.activity.previous_heat_issues ? 'Yes' : 'No'}</td>
							<td>${data.activity.heat_issues_details}</td>
							<td>${data.activity.outdoor_activity ? 'Yes' : 'No'}</td>
							<td>${data.activity.activity_level}</td>
							<td>${data.activity.activity_duration}</td>
						</tr>
					</tbody>
				</table>
			`;
		}
	</script>
</body>

</html>