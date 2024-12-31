def get_layout() -> str:
    """
    Layout for the login page
    """
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@mantine/core@latest/lib/index.min.css">
        <style>
            body {
                background-color: #242424;
                color: #fff;
                font-family: 'Inter', sans-serif;
                display: flex;
                align-items: center;
                justify-content: center;
                height: 100vh;
                margin: 0;
            }
            .form-container {
                max-width: 400px;
                background: #333;
                padding: 30px;
                border-radius: 8px;
                box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3);
            }
            .form-container label {
                display: block;
                font-size: 14px;
                margin-bottom: 8px;
            }
            .form-container input {
                width: 100%;
                padding: 10px;
                margin-bottom: 20px;
                border: 1px solid #444;
                border-radius: 5px;
                background: #222;
                color: #fff;
            }
            .form-container button {
                width: 100%;
                padding: 12px;
                border: none;
                border-radius: 5px;
                background: linear-gradient(90deg, #119460, #369d3d, #5da618);
                color: white;
                font-size: 16px;
                font-weight: bold;
                cursor: pointer;
                transition: background 0.3s;
            }
            .form-container button:hover {
                background: linear-gradient(90deg, #119460, #369d3d, #5da618);
            }
        </style>
    </head>
    <body>
        <div class="form-container">
            <form method="post">
                <label for="username">Username</label>
                <input type="text" name="username" id="username" placeholder="">
                <label for="password">Password</label>
                <input type="password" name="password" id="password" placeholder="">
                <button type="submit">Login</button>
            </form>
        </div>
    </body>
    </html>
    """
