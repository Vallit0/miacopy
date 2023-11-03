import React, { useState } from 'react';
import './Reports.css';

const Reports = () => {
  const [selectedImagePath, setSelectedImagePath] = useState('');

  const handleButtonClick = (imagePath) => {
    setSelectedImagePath(imagePath);
  };

  return (
    <div className="report-container">
      <div className="buttons-container">
        <button onClick={() => handleButtonClick('/path/to/image1.jpg')}>
          Image 1
        </button>
        <button onClick={() => handleButtonClick('/path/to/image2.jpg')}>
          Image 2
        </button>
        <button onClick={() => handleButtonClick('/path/to/image3.jpg')}>
          Image 3
        </button>
      </div>
      <div className="image-container">
        {selectedImagePath && (
          <img src={selectedImagePath} alt="Selected" />
        )}
      </div>
    </div>
  );
};

export default Reports;
