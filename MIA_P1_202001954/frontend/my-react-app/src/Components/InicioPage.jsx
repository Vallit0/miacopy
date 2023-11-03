import React from 'react';
import LoginLine from './LoginLine.jsx';
import Controlador from './Controlador.jsx';
import FileUploader from './FileUploader.jsx';
import './Components.css'
import { FileContentProvider } from './FileContentContext.jsx';

function InicioPage() {

  return (
    <>
    <FileContentProvider>
    <div className="fondito">
      <LoginLine></LoginLine>
      <FileUploader ></FileUploader>
      <Controlador></Controlador>
    </div>
    </FileContentProvider>
    </>
  );
}

export default InicioPage;
