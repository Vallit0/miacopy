import React, { useState } from 'react';
import { useFileContent } from './FileContentContext.jsx';


const FileUploader = () => {
  const { setFileContent } = useFileContent();


  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file && file.name.endsWith('.adsj')) {
      //setSelectedFile(file);

      // Lee el contenido del archivo y guárdalo en una variable
      const reader = new FileReader();
      reader.onload = (e) => {
        const fileContent = e.target.result;
        setFileContent(fileContent);
        console.log(fileContent)
      };
      reader.readAsText(file);
    } else {
      // Aquí puedes mostrar un mensaje de error o tomar la acción que desees
      alert('Por favor, selecciona un archivo con extensión .adsj');
    }
  };

  return (
    <div style={{ display: 'flex', alignItems: 'center', width: '100%' }}>
      <input
        style={{ width: '100%' }}
        type="file"
        onChange={handleFileChange}
      />
      <div style={{ display: 'flex', justifyContent: 'flex-end', width: '31%' }}>
      </div>
    </div>
  );
};


export default FileUploader


/*
[X] Verificar que sea un archivo con una extension .adsj 15 minutes 
[X] Mostrar el archivo en el controlador 1   20 minutes 
    [X] Edicion del contenido en vivo 
[X] mandar todo el texto a la API 
   [ ] Escuchar el Post general 
[ ] mostrar las respuestas de la API en la consola 20 minutes
 
[ ] hacer front del login con Request  1 hora 
[ ] mostrar reportes al hacer el login  1 hora 

MAXIMO TIEMPO A TARDAR -> 3 horas y media -> terminado a las 9 de la noche 
MONTADO Y TESTING -> 11 de la noche (Pero todo terminado)

*/
