import React, { useState } from "react";

function Login() {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [id, setId] = useState("");
    const [showPopup, setShowPopup] = useState(false);

    const handleLogin = () => {
        const loginString = `login -user=${username} -pass=${password} -id=${id}`;
        fetch("your-endpoint-url", {
            method: "POST",
            body: JSON.stringify({ loginString }),
            headers: {
                "Content-Type": "application/json"
            }
        })
            .then(response => response.json())
            .then(data => {
                if (data.response === "true") {
                    // Navigate to next page
                } else {
                    setShowPopup(true);
                }
            });
    };
    const handleConsola = () => {
        const loginString = `login -user=${username} -pass=${password} -id=${id}`;
        fetch("your-endpoint-url", {
            method: "POST",
            body: JSON.stringify({ loginString }),
            headers: {
                "Content-Type": "application/json"
            }
        })
            .then(response => response.json())
            .then(data => {
                if (data.response === "true") {
                    // Navigate to next page
                } else {
                    setShowPopup(true);
                }
            });
    };

    return (
        <div>
            <h1>Login</h1>
            <button onClick={handleConsola}>Consola</button>
            <label>
                Username:
                <input
                    type="text"
                    value={username}
                    onChange={e => setUsername(e.target.value)}
                />
            </label>
            <label>
                Password:
                <input
                    type="password"
                    value={password}
                    onChange={e => setPassword(e.target.value)}
                />
            </label>
            <label>
                ID:
                <input
                    type="text"
                    value={id}
                    onChange={e => setId(e.target.value)}
                />
            </label>
            <button onClick={handleLogin}>Try Login</button>
            {showPopup && (
                <div>
                    <p>Wrong credentials. Please try again.</p>
                    <button onClick={() => setShowPopup(false)}>Close</button>
                </div>
            )}
        </div>
    );
}

export default Login;
