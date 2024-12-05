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

	// Query to fetch the average heat index today
	$stmtAverage = $conn->prepare("SELECT heat_index FROM weatherdata");
	$stmtAverage->execute();
	$averageHeatIndex = $stmtAverage->fetch(PDO::FETCH_ASSOC);
	$heatIndexes = $stmtAverage->fetchAll(PDO::FETCH_COLUMN);
	$averageHeatIndex = array_sum($heatIndexes) / count($heatIndexes);

    // Query to fetch the city with the lowest heat index
    $stmtLow = $conn->prepare("SELECT city, heat_index FROM weatherdata ORDER BY heat_index ASC LIMIT 1");
    $stmtLow->execute();
    $lowestCity = $stmtLow->fetch(PDO::FETCH_ASSOC);

    // Query to fetch the city with the highest heat index
    $stmtHigh = $conn->prepare("SELECT city, heat_index FROM weatherdata ORDER BY heat_index DESC LIMIT 1");
    $stmtHigh->execute();
    $highestCity = $stmtHigh->fetch(PDO::FETCH_ASSOC);

    // Query to fetch weather data for forecast (keep this query as is)
    $stmt = $conn->prepare("SELECT city, 
        hi_day_one, hi_day_two, hi_day_three, hi_day_four, 
        hi_day_five, hi_day_six, hi_day_seven 
        FROM weatherdataforecast");
    $stmt->execute();

    // Fetch results
    $weatherData = $stmt->fetchAll(PDO::FETCH_ASSOC);

	// Query to fetch prediction ratings for today and yesterday
	$stmtRatingsToday = $conn->prepare("SELECT city, prediction_rating, date_added 
										FROM predictedhimetrics 
										WHERE date_added = CURDATE()");
	$stmtRatingsToday->execute();
	$ratingsDataToday = $stmtRatingsToday->fetchAll(PDO::FETCH_ASSOC);

	$stmtRatingsYesterday = $conn->prepare("SELECT city, prediction_rating, date_added 
											FROM predictedhimetricshistory 
											WHERE date_added = CURDATE() - INTERVAL 1 DAY");
	$stmtRatingsYesterday->execute();
	$ratingsDataYesterday = $stmtRatingsYesterday->fetchAll(PDO::FETCH_ASSOC);

	// Helper function to convert prediction ratings to numeric values
	function ratingToNumber($rating) {
		switch ($rating) {
			case 'poor': return 1;
			case 'fair': return 2;
			case 'good': return 3;
			case 'excellent': return 4;
			default: return 0;
		}
	}

	// Calculate today's average rating
	$todaySum = 0;
	$todayCount = 0;

	foreach ($ratingsDataToday as $data) {
		$ratingValue = ratingToNumber($data['prediction_rating']);
		$todaySum += $ratingValue;
		$todayCount++;
	}

	// Calculate today's average
	$todayAverage = ($todayCount > 0) ? $todaySum / $todayCount : 0;

	// Calculate yesterday's average rating
	$yesterdaySum = 0;
	$yesterdayCount = 0;

	foreach ($ratingsDataYesterday as $data) {
		$ratingValue = ratingToNumber($data['prediction_rating']);
		$yesterdaySum += $ratingValue;
		$yesterdayCount++;
	}

	// Calculate yesterday's average
	$yesterdayAverage = ($yesterdayCount > 0) ? $yesterdaySum / $yesterdayCount : 0;

	// Convert average rating to a string based on the numeric value
	function averageToRating($average) {
		if ($average <= 1.5) return 'Poor';
		if ($average <= 2.5) return 'Fair';
		if ($average <= 3.5) return 'Good';
		return 'Excellent';
	}

	// Convert today's and yesterday's average to their corresponding rating labels
	$todayRating = averageToRating($todayAverage);
	$yesterdayRating = averageToRating($yesterdayAverage);

	// Connect to secondary database
    $connTwo = new PDO("mysql:host={$dbConfig['host']};dbname={$dbConfig['dbname_two']}", $dbConfig['username'], $dbConfig['password']);
    $connTwo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

    // Fetch user activity log
    $stmtActivityLog = $connTwo->prepare("SELECT user_id, activity_type, activity_timestamp, activity_details FROM UserActivityLog ORDER BY activity_timestamp DESC");
    $stmtActivityLog->execute();
    $userActivityLogs = $stmtActivityLog->fetchAll(PDO::FETCH_ASSOC);

} catch (PDOException $e) {
	$weatherData = [];
	$ratingsData = [];
	$userActivityLogs = [];
	$error = $e->getMessage();
}

$conn = null;
$connTwo = null;

// Directory path to the logs
$logDirectory = __DIR__ . '/../src/script/logs/';

// Get all .log files in the specified directory
$logFiles = glob($logDirectory . '*.log');

$logContent = '';

// Check if a log file is selected from the dropdown
if (isset($_POST['logFile'])) {
    $selectedLog = $_POST['logFile'];
    
    // Check if the selected file exists
    if (file_exists($selectedLog)) {
        // Read the content of the selected log file
        $logContent = file_get_contents($selectedLog);
        
        // Split the content into lines and reverse them to show the latest logs first
        $logLines = explode("\n", $logContent);
        $logLines = array_reverse($logLines); // Reverse the array to get the latest logs first
        
        // Join the reversed lines back into a single string
        $logContent = implode("\n", $logLines);
    } else {
        $logContent = 'The selected log file does not exist.';
    }
}

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

	<!-- Swiper.js -->
	<link rel="stylesheet" href="https://unpkg.com/swiper/swiper-bundle.min.css">
	<script src="https://unpkg.com/swiper/swiper-bundle.min.js"></script>

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
				<a class="sidebar-brand" href="index.html">
			<br>
			<br>
          <span class="align-middle">INET-READY /<span style="font-weight: normal;">/ Admin</span></span>
        </a>

				<ul class="sidebar-nav">
					<li class="sidebar-header">
						Pages
					</li>

					<li class="sidebar-item active">
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
							<h1 class="h3 mb-3"><strong>System Monitoring</strong> Dashboard </h1>
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
					<div class="col-xl-6 col-xxl-5 d-flex">
							<div class="w-100">
								<div class="row">
									<div class="col-sm-6">
									<div class="card">
											<div class="card-body">
												<div class="row">
													<div class="col mt-0">
														<h5 class="card-title">Average Heat Index</h5>
													</div>

													<div class="col-auto">
														<div class="stat text-primary">
															<i class="align-middle" data-feather="sun"></i>
														</div>
													</div>
												</div>
												<h1 class="mt-1 mb-3"><?= number_format($averageHeatIndex, 2) ?>°C</h1>
												<div class="mb-0">
													<span class="text-info"> <i class="mdi mdi-arrow-bottom-right"></i> <?= date('Y-m-d') ?> </span>
													<span class="text-muted">today</span>
												</div>
											</div>
										</div>
										<div class="card">
											<div class="card-body">
												<div class="row">
													<div class="col mt-0">
														<h5 class="card-title">Today's Lowest</h5>
													</div>
													<div class="col-auto">
														<div class="stat text-primary">
															<i class="align-middle" data-feather="arrow-down"></i>
														</div>
													</div>
												</div>
												<h1 class="mt-1 mb-3"><?= htmlspecialchars($lowestCity['city']); ?></h1>
												<div class="mb-0">
													<span class="text-success"> 
														<i class="mdi mdi-arrow-bottom-right"></i> <?= htmlspecialchars($lowestCity['heat_index']); ?> °C
													</span>
													<span class="text-muted">Heat Index</span>
												</div>
											</div>
										</div>
									</div>
									<div class="col-sm-6">
									<div class="card">
											<div class="card-body">
												<div class="row">
													<div class="col mt-0">
														<h5 class="card-title">Prediction Rating</h5>
													</div>

													<div class="col-auto">
														<div class="stat text-primary">
															<i class="align-middle" data-feather="trending-up"></i>
														</div>
													</div>
												</div>
												<h1 class="mt-1 mb-3"><?= $todayRating ?> (<?= number_format($todayAverage, 2) ?>)</h1>
												<div class="mb-0">
													<span class="text-info"> <i class="mdi mdi-arrow-bottom-right"></i><?= $yesterdayRating ?> (<?= number_format($yesterdayAverage, 2) ?>)</span>
													<span class="text-muted">Since yesterday</span>
												</div>
											</div>
										</div>
										<div class="card">
											<div class="card-body">
												<div class="row">
													<div class="col mt-0">
														<h5 class="card-title">Today's Highest</h5>
													</div>
													<div class="col-auto">
														<div class="stat text-primary">
															<i class="align-middle" data-feather="arrow-up"></i>
														</div>
													</div>
												</div>
												<h1 class="mt-1 mb-3"><?= htmlspecialchars($highestCity['city']); ?></h1>
												<div class="mb-0">
													<span class="text-danger"> 
														<i class="mdi mdi-arrow-bottom-right"></i> <?= htmlspecialchars($highestCity['heat_index']); ?> °C
													</span>
													<span class="text-muted">Heat Index</span>
												</div>
											</div>
										</div>
									</div>
								</div>
							</div>
						</div>
					<div class="col-xl-6 col-xxl-7">
						<div class="card flex-fill w-100">
							<div class="card-header d-flex justify-content-between" style="padding-bottom: 5px;">
								<h5 class="card-title mb-0">Heat Index Predictions (°C)</h5>
								<a href="downloadChartsFolder.php" style="padding-top: 0px; padding-left: 2px; padding-right: 2px;" class="btn btn-link ml-auto">
									<i class="align-middle" data-feather="download" style="width: 20px; height: 20px;"></i>
								</a>
							</div>
							<div class="card-body py-3">
								<div class="swiper-container" style="padding-top: 0px;">
									<div class="swiper-wrapper">
										<?php if (!empty($weatherData)): ?>
											<?php foreach ($weatherData as $city): ?>
												<div class="swiper-slide">
													<div class="card-body">
														<h5 class="card-title text-center"><?= htmlspecialchars($city['city']) ?></h5>
														<div class="chart-container" style="position: relative; height:205px; width:100%;">
															<canvas id="chart-<?= htmlspecialchars($city['city']) ?>"></canvas>
														</div>
													</div>
												</div>
											<?php endforeach; ?>
										<?php else: ?>
											<p class="text-danger">Failed to load weather data. Please try again later.</p>
										<?php endif; ?>
									</div>
								</div>
							</div>
							</div>
						</div>
					</div>
					<div class="row">
						<div class="col-12 col-lg-8 col-xxl-7 d-flex">
							<div class="card flex-fill">
								<div class="card-header">
									<h5 class="card-title mb-0">Recent User Activity</h5>
								</div>
								<div style="max-height: 500px; overflow-y: auto; border: 1px solid #ddd; padding: 10px;">
									<table class="table table-hover my-0">
										<thead>
											<tr>
												<th>User ID</th>
												<th>Activity Type</th>
												<th>Timestamp</th>
												<th>Details</th>
											</tr>
										</thead>
										<tbody>
											<?php if (!empty($userActivityLogs)): ?>
												<?php foreach ($userActivityLogs as $log): ?>
													<tr>
														<td><?= htmlspecialchars($log['user_id']) ?></td>
														<td><?= htmlspecialchars($log['activity_type']) ?></td>
														<td><?= htmlspecialchars($log['activity_timestamp']) ?></td>
														<td><?= htmlspecialchars($log['activity_details']) ?></td>
													</tr>
												<?php endforeach; ?>
											<?php else: ?>
												<tr>
													<td colspan="4">No activity logs available.</td>
												</tr>
											<?php endif; ?>
										</tbody>
									</table>
								</div>
							</div>
						</div>
						<div class="col-12 col-lg-4 col-xxl-5 d-flex">
							<div class="card flex-fill w-100">
								<div class="card-header d-flex justify-content-between">
									<h5 class="card-title mb-0">System Logs</h5>
									<a href="downloadLogs.php" style="padding-top: 0px; padding-bottom: 0px; padding-left: 2px; padding-right: 2px;" class="btn btn-link ml-auto">
										<i class="align-middle" data-feather="download" style="width: 20px; height: 20px;"></i>
									</a>
								</div>
								<div class="card-body d-flex w-100" style="padding-top: 0px;">
									<div class="w-100">
										<!-- Dropdown to select log file -->
										<form method="POST" action="">
											<select name="logFile" class="form-select" onchange="this.form.submit()">
												<?php foreach ($logFiles as $logFile): ?>
													<option value="<?= htmlspecialchars($logFile) ?>" <?= isset($selectedLog) && $selectedLog == $logFile ? 'selected' : '' ?>>
														<?= basename($logFile) ?>
													</option>
												<?php endforeach; ?>
											</select>
										</form>
										
										<!-- Display log file content with a scrollable area -->
										<?php if ($logContent): ?>
											<div style="max-height: 465px; overflow-y: auto; border: 1px solid #ddd; padding: 10px;">
												<pre style="white-space: pre-wrap; word-wrap: break-word;"><?= htmlspecialchars($logContent) ?></pre>
											</div>
										<?php endif; ?>
									</div>
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
	<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

	<script>
    document.addEventListener("DOMContentLoaded", function () {
        // Initialize Swiper for single slide visibility and autoplay
        const swiper = new Swiper('.swiper-container', {
            slidesPerView: 1, // Show one slide at a time
            spaceBetween: 0, // No spacing between slides
            loop: true, // Enable infinite looping
            autoplay: {
                delay: 5000, // seconds per slide
                disableOnInteraction: false,
            },
        });

        // Generate charts using Chart.js
        const weatherData = <?php echo json_encode($weatherData); ?>;
			weatherData.forEach(city => {
				const ctx = document.getElementById(`chart-${city.city}`).getContext('2d');
				new Chart(ctx, {
					type: 'line',
					data: {
						labels: [
							new Date(Date.now() + 1 * 24 * 60 * 60 * 1000).toLocaleDateString(),
							new Date(Date.now() + 2 * 24 * 60 * 60 * 1000).toLocaleDateString(),
							new Date(Date.now() + 3 * 24 * 60 * 60 * 1000).toLocaleDateString(),
							new Date(Date.now() + 4 * 24 * 60 * 60 * 1000).toLocaleDateString(),
							new Date(Date.now() + 5 * 24 * 60 * 60 * 1000).toLocaleDateString(),
							new Date(Date.now() + 6 * 24 * 60 * 60 * 1000).toLocaleDateString(),
							new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toLocaleDateString()
						],
						datasets: [{
							label: "Heat Index (°C)",
							fill: true,
							data: [
								city.hi_day_one,
								city.hi_day_two,
								city.hi_day_three,
								city.hi_day_four,
								city.hi_day_five,
								city.hi_day_six,
								city.hi_day_seven
							],
							backgroundColor: 'rgba(75, 192, 192, 0.2)',
							borderColor: 'rgba(75, 192, 192, 1)',
							borderWidth: 2
						}]
					},
					options: {
						responsive: true,
						maintainAspectRatio: false,
						scales: {
							x: {
								grid: { display: false },
							},
							y: {
								ticks: {
									min: 10,
									max: 50,
									stepSize: 4
								}
							}
						},
						plugins: {
							legend: { display: false }
						}
					}
				});
			});
		});
	</script>
</body>

</html>