import React, { useState } from 'react';
import { useFileContent } from './FileContentContext.jsx';

const Controlador = () => {
  const [response, setResponse] = useState(null);
  const { fileContent, setFileContent } = useFileContent();

  const handleTextareaChange = (e) => {
    setFileContent(e.target.value);
  };

  const handleEjecutarClick = () => {
    // Realiza una solicitud HTTP POST para enviar el contenido al endpoint
    fetch('http://localhost:8080', { // Reemplaza localhost:8080 con la URL correcta de tu servidor
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ content: fileContent }),
    })
      .then((response) => response.json())
      .then((data) => {
        // Actualiza el segundo textarea con los datos recibos de la API
        setResponse(data);
      })
      .catch((error) => {
        console.error('Error:', error);
      });
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column' }}>
      <textarea
        style={{
          width: '100%',
          height: '200px',
          padding: '10px',
          resize: 'both',
          overflowY: 'scroll',
          overflowX: 'scroll',
        }}
        value={fileContent}
        onChange={handleTextareaChange}
      ></textarea>
      <button onClick={handleEjecutarClick}>Ejecutar</button>
      <textarea
        style={{
          width: '100%',
          height: '200px',
          padding: '10px',
          resize: 'both',
          overflowY: 'scroll',
          overflowX: 'scroll',
        }}
        value={response} // Actualiza el valor con la respuesta de la API
        readOnly
      ></textarea>
    </div>
  );
};

export default Controlador;
