import React, { useState } from 'react';
import { Box, Typography, Button, Alert } from '@mui/material';

const DebugUploadPage = () => {
  const [status, setStatus] = useState('ready');

  const handleTestUpload = () => {
    setStatus('testing');
    
    // Simulate a simple upload
    setTimeout(() => {
      const mockResults = {
        fileName: 'test_database.db',
        fileType: 'db',
        fileSize: 1024 * 1024,
        createdAt: new Date().toISOString(),
        analysisData: {
          businessDomain: 'Test Database',
          insights: ['Test insight 1', 'Test insight 2'],
          recommendations: ['Test recommendation 1'],
          metadata: {
            analysisType: 'test',
            note: 'This is a test analysis'
          }
        }
      };
      
      localStorage.setItem('lastAnalysis', JSON.stringify(mockResults));
      setStatus('success');
      
      // Redirect after 2 seconds
      setTimeout(() => {
        window.location.href = '/results';
      }, 2000);
    }, 1000);
  };

  return (
    <Box sx={{ p: 4, textAlign: 'center' }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Debug Upload Page
      </Typography>
      
      <Typography variant="body1" sx={{ mb: 3 }}>
        This is a minimal test version to debug the upload flow.
      </Typography>
      
      {status === 'ready' && (
        <Button 
          variant="contained" 
          size="large"
          onClick={handleTestUpload}
        >
          Test Upload & Analysis
        </Button>
      )}
      
      {status === 'testing' && (
        <Alert severity="info">
          Testing upload flow... Please wait.
        </Alert>
      )}
      
      {status === 'success' && (
        <Alert severity="success">
          Test completed! Redirecting to results page...
        </Alert>
      )}
      
      <Box sx={{ mt: 4, textAlign: 'left' }}>
        <Typography variant="h6" gutterBottom>
          Debug Info:
        </Typography>
        <Typography variant="body2" component="pre" sx={{ bgcolor: 'grey.100', p: 2, borderRadius: 1 }}>
          Status: {status}
          <br />
          localStorage: {localStorage.getItem('lastAnalysis') ? 'Has data' : 'Empty'}
        </Typography>
      </Box>
    </Box>
  );
};

export default DebugUploadPage;
