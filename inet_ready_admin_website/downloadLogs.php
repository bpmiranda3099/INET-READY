<?php
// Set the path to the logs directory
$directoryPath = 'C:/xampp/htdocs/Projects/INET-READY/src/script/logs/';

// Check if the directory exists
if (is_dir($directoryPath)) {
    // Create a temporary zip file
    $zip = new ZipArchive();
    $zipFile = 'logs_' . time() . '.zip'; // Unique filename with timestamp
    $zipFilePath = $directoryPath . $zipFile;

    if ($zip->open($zipFilePath, ZipArchive::CREATE) === TRUE) {
        // Open the directory and add all files to the zip
        $files = scandir($directoryPath);
        foreach ($files as $file) {
            // Skip . and .. directory entries
            if ($file != '.' && $file != '..') {
                $filePath = $directoryPath . $file;
                if (is_file($filePath)) {
                    $zip->addFile($filePath, $file); // Add the file to the zip
                }
            }
        }
        $zip->close();

        // Check if the zip file was created successfully
        if (file_exists($zipFilePath)) {
            // Set headers to force a file download
            header('Content-Type: application/zip');
            header('Content-Disposition: attachment; filename="' . basename($zipFilePath) . '"');
            header('Content-Length: ' . filesize($zipFilePath));

            // Output the file content for download
            readfile($zipFilePath);

            // Delete the temporary zip file after download
            unlink($zipFilePath);
            exit;
        } else {
            echo 'Error creating zip file.';
        }
    } else {
        echo 'Failed to create zip file.';
    }
} else {
    echo 'Logs directory not found.';
}
?>
