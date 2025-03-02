import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import ButtonAppBar from './components/ButtonAppBar';
import { Snackbar, Alert } from '@mui/material';
import { AuthProvider } from './auth';
import Login from './pages/Login';
import Register from './pages/Register';
import LinkList from './pages/LinkList';
import CategoryList from './pages/CategoryList';
import RequireAuth from './components/RequireAuth';

function App() {
  const [alertInfo, setAlertInfo] = useState({
    open: false,
    message: '',
    severity: 'info',
  });

  return (
    <AuthProvider>
      <Router>
        <div className="App">
          <ButtonAppBar setAlertInfo={setAlertInfo} />
          
          {/* ...existing Routes code... */}
          
          <Snackbar 
            open={alertInfo.open} 
            autoHideDuration={6000} 
            onClose={() => setAlertInfo({...alertInfo, open: false})}
          >
            <Alert 
              onClose={() => setAlertInfo({...alertInfo, open: false})} 
              severity={alertInfo.severity}
              sx={{ width: '100%' }}
            >
              {alertInfo.message}
            </Alert>
          </Snackbar>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;
