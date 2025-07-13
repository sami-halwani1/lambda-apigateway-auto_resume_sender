<?php
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    header('Content-Type: application/json');

    $input = json_decode(file_get_contents('php://input'), true);

    if (!$input || !isset($input['name']) || !isset($input['email']) || !isset($input['phone']) ||  !isset($input['message'])) {
        http_response_code(400);
        echo json_encode(['success' => false, 'message' => 'Invalid input']);
        exit;
    }

    $api_url = 'https://your-api-endpoint.execute-api.us-east-1.amazonaws.com/prod/resume'; // Replace with your actual API Gateway endpoint
    $api_key = 'your-api-key'; // Secure - not visible to client

    $response = file_get_contents($api_url, false, stream_context_create([
        'http' => [
            'method' => 'POST',
            'header' => "Content-Type: application/json\r\n" .
                        "x-api-key: $api_key\r\n",
            'content' => json_encode([
                'name' => htmlspecialchars($input['name']),
                'email' => htmlspecialchars($input['email']),
                'phone' => htmlspecialchars($input['phone']),
                'message' => htmlspecialchars($input['message'])
            ])
        ]
    ]));

    echo json_encode(['success' => true, 'response' => $response]);
    exit;
}
?>

<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test API Gateway Contact </title>

    <style>
        .form-container {
            display: flex;
            flex-direction: column;
            max-width: 640px;
            padding: 20px;
            margin: auto;
            border: 2px solid #9f9f9f;
            border-radius: 8px;
        }

        .form-container label {
            font-weight: bold;
            margin-top: 2.5px;
            margin-bottom: 2.5px;
            color: #010101;
        }

        .form-container input,
        textarea {
            padding: 10px;
            margin: 5px 0;
            border: 1px solid #ccc;
            border-radius: 4px;
            color: #333;
        }

        .form-container button {
            padding: 10px;
            background-color: #007bff;
            color: white;
            border: none;
            border-radius: 4px;
            width: 25%;
            max-width: 250px;
            cursor: pointer;
            display: block;
            margin: 10px auto 0;
        }
    </style>
</head>

<body>




    <form class="form-container" id="contactForm">
        <label for="input">Full Name</label>
        <input type="text" name="name" placeholder="Your Name" required />
        <label for="input">Email</label>
        <input type="email" name="email" placeholder="Your Email" required />
        <label for="input">Phone</label>
        <input type="tel" name="phone" placeholder="Your Phone Number" pattern="[0-9]{10}" required />
        <label for="input">Tell Me More!</label>
        <textarea name="message" placeholder="Your Message" required></textarea>
        <button type="submit">Send</button>
    </form>

    <script>
        document.getElementById('contactForm').addEventListener('submit', async function(e) {
            e.preventDefault();

            const form = e.target;
            const formData = {
                name: form.name.value,
                email: form.email.value,
                phone: form.phone.value,
                message: form.message.value
            };

            try {
                const response = await fetch('local-test.php', { // <-- your PHP file endpoint
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(formData)
                });

                const result = await response.json();

                if (result.success) {
                    const message = typeof result.response === 'string' ?
                        result.response :
                        JSON.stringify(result.response, null, 2);

                    alert("✅ Message sent successfully!\n\nServer Response:\n" + message);
                } else {
                    alert("❌ Failed to send message.\n\nError:\n" + (result.message || "Unknown error."));
                }
            } catch (err) {
                console.error(err);
                alert("❌ Request failed. Check the console for details.");
            }
        });
    </script>


</body>

</html>