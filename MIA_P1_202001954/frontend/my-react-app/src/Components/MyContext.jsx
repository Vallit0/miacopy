import React, { createContext, useContext, useReducer } from 'react';

// Define your context
const MyContext = createContext();

// Define your initial state and reducer function (if needed)
const initialState = {
  // Your initial state values go here
};

const reducer = (state, action) => {
  // Handle state updates based on the action type
  switch (action.type) {
    // Handle different action types here
    default:
      return state;
  }
};

// Define your custom provider component
export function MyContextProvider({ children }) {
  const [state, dispatch] = useReducer(reducer, initialState);

  return (
    <MyContext.Provider value={{ state, dispatch }}>
      {children}
    </MyContext.Provider>
  );
}

// Define a custom hook to access the context
export function useMyContext() {
  return useContext(MyContext);
}
