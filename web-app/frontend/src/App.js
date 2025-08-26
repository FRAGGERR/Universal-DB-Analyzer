import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';

// Working components
import WorkingUploadPage from './pages/Upload/WorkingUploadPage';
import SimpleAnalysisResultsPage from './pages/Analysis/SimpleAnalysisResultsPage';
import LoginPage from './pages/Auth/LoginPage';
import RegisterPage from './pages/Auth/RegisterPage';

// Create theme
const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Routes>
          <Route path="/" element={<WorkingUploadPage />} />
          <Route path="/upload" element={<WorkingUploadPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/results" element={<SimpleAnalysisResultsPage />} />
          <Route path="/debug" element={<WorkingUploadPage />} />
        </Routes>
      </Router>
    </ThemeProvider>
  );
}

export default App;