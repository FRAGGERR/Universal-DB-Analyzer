import React, { useState } from 'react';
import { 
  Box, 
  Typography, 
  Paper, 
  Button, 
  Alert
} from '@mui/material';

const TestPage = () => {
  const [testResult, setTestResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const testAPI = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/upload', {
        method: 'POST',
        headers: {
          'x-file-name': 'test_database.db'
        }
      });

      const result = await response.json();
      setTestResult(result);
    } catch (error) {
      setTestResult({ error: error.message });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        API Test Page
      </Typography>
      
      <Paper elevation={2} sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Test the Upload API
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          This page tests if the API endpoint is working correctly.
        </Typography>
        
        <Button 
          variant="contained" 
          onClick={testAPI}
          disabled={loading}
        >
          {loading ? 'Testing...' : 'Test API'}
        </Button>
      </Paper>

      {testResult && (
        <Paper elevation={2} sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Test Result
          </Typography>
          
          {testResult.error ? (
            <Alert severity="error" sx={{ mb: 2 }}>
              {testResult.error}
            </Alert>
          ) : (
            <Alert severity="success" sx={{ mb: 2 }}>
              API test successful!
            </Alert>
          )}
          
          <Typography variant="body2" component="pre" sx={{ 
            bgcolor: 'grey.100', 
            p: 2, 
            borderRadius: 1,
            overflow: 'auto'
          }}>
            {JSON.stringify(testResult, null, 2)}
          </Typography>
        </Paper>
      )}
    </Box>
  );
};

export default TestPage;
