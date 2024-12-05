<?php
// Path to the directory
$dir = 'C:/xampp/htdocs/Projects/INET-READY/src/script/charts/predicted_heat_index';

// Get all subdirectories
$subdirs = array_filter(glob($dir . '/*'), 'is_dir');

// Find the latest directory based on the last modified time
$latestDir = '';
$latestTime = 0;
foreach ($subdirs as $subdir) {
    $subdirTime = filemtime($subdir);
    if ($subdirTime > $latestTime) {
        $latestDir = $subdir;
        $latestTime = $subdirTime;
    }
}

// Create a ZIP archive of the latest directory
$zip = new ZipArchive();
$zipFile = tempnam(sys_get_temp_dir(), 'latest_folder_') . '.zip';
if ($zip->open($zipFile, ZipArchive::CREATE) === TRUE) {
    $files = new RecursiveIteratorIterator(
        new RecursiveDirectoryIterator($latestDir),
        RecursiveIteratorIterator::LEAVES_ONLY
    );

    foreach ($files as $name => $file) {
        if (!$file->isDir()) {
            $zip->addFile($file, substr($name, strlen($latestDir) + 1));
        }
    }
    $zip->close();

    // Send the ZIP file to the browser for download
    header('Content-Type: application/zip');
    header('Content-Disposition: attachment; filename="' . date('Y-m-d') . ' - Prediction Charts.zip"');
    header('Content-Length: ' . filesize($zipFile));
    readfile($zipFile);
    unlink($zipFile);  // Delete the temporary file
} else {
    echo "Failed to create the ZIP file.";
}
?>
