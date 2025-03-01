<?php
$uploadDir = 'uploads/';
if (!is_dir($uploadDir)) {
    mkdir($uploadDir, 0777, true);
}

$response = [];

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    if (isset($_FILES['file']) && $_FILES['file']['error'] === UPLOAD_ERR_OK) {
        $fileName = basename($_FILES['file']['name']);
        $uploadFilePath = $uploadDir . $fileName;

        if (move_uploaded_file($_FILES['file']['tmp_name'], $uploadFilePath)) {
            $operation = $_POST['operation']; // 'compress' or 'decompress'
            $outputFile = $uploadDir . ($operation === 'compress' ? 'compressed.bin' : 'decompressed.txt');

            // Call Python script
            $command = "python huffman_compression.py $operation $uploadFilePath $outputFile 2>&1";
            exec($command, $output, $returnCode);

            if ($returnCode === 0) {
                // Extract file sizes from Python script output
                $originalSize = 0;
                $processedSize = 0;
                foreach ($output as $line) {
                    if (strpos($line, 'Original file size:') !== false) {
                        $originalSize = (int)trim(str_replace('Original file size:', '', $line));
                    } elseif (strpos($line, 'Compressed file size:') !== false) {
                        $processedSize = (int)trim(str_replace('Compressed file size:', '', $line));
                    } elseif (strpos($line, 'Decompressed file size:') !== false) {
                        $processedSize = (int)trim(str_replace('Decompressed file size:', '', $line));
                    }
                }

                $response['success'] = true;
                $response['message'] = "File processed successfully.";
                $response['downloadLink'] = $outputFile;
                $response['originalSize'] = $originalSize;
                $response['processedSize'] = $processedSize;
            } else {
                $response['success'] = false;
                $response['message'] = "Error processing file: " . implode("\n", $output);
            }
        } else {
            $response['success'] = false;
            $response['message'] = "Error uploading file.";
        }
    } else {
        $response['success'] = false;
        $response['message'] = "No file uploaded or an error occurred.";
    }
} else {
    $response['success'] = false;
    $response['message'] = "Invalid request method.";
}

header('Content-Type: application/json');
echo json_encode($response);
?>