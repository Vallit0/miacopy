import React, { useState } from 'react';
import './Components.css'

function LoginLine() {
    const [inputValue, setInputValue] = useState('');

    const handleInputChange = (event) => {
        setInputValue(event.target.value);
    };

    const handleButtonClick = () => {
        console.log(`Input value: ${inputValue}`);
        // Do something with the input value here
    };

    return (
        <div className="barline">
            <input type="text" value={inputValue} onChange={handleInputChange} />
            <button onClick={handleButtonClick}>Login</button>
        </div>
    );
}

export default LoginLine;
