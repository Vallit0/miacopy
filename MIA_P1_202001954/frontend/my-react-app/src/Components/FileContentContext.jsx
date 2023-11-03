// FileContentContext.js
import React, { createContext, useContext, useState } from 'react';

const FileContentContext = createContext();

export const useFileContent = () => {
  return useContext(FileContentContext);
};

export const FileContentProvider = ({ children }) => {
  const [fileContent, setFileContent] = useState('');

  return (
    <FileContentContext.Provider value={{ fileContent, setFileContent }}>
      {children}
    </FileContentContext.Provider>
  );
};
