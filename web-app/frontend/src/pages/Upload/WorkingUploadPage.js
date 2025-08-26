import React, { useState } from 'react';
import { 
  Box, 
  Typography, 
  Paper, 
  Button, 
  Alert,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
  CircularProgress,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions
} from '@mui/material';
import { 
  CloudUpload as UploadIcon, 
  CheckCircle as CheckIcon,
  Description as FileIcon,
  Key as KeyIcon,
  Login as LoginIcon
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';

const WorkingUploadPage = () => {
  const [files, setFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState(null);
  const [apiKeyDialog, setApiKeyDialog] = useState(false);
  const [apiKey, setApiKey] = useState('');
  const navigate = useNavigate();

  // Check for stored API key on component mount
  React.useEffect(() => {
    const storedKey = localStorage.getItem('gemini_api_key');
    if (storedKey) {
      setApiKey(storedKey);
    }
  }, []);

  // Check if user is authenticated
  const isAuthenticated = () => {
    return !!localStorage.getItem('token');
  };

  const handleFileSelect = (event) => {
    const selectedFiles = Array.from(event.target.files);
    
    const newFiles = selectedFiles.map(file => ({
      file,
      id: Math.random().toString(36).substr(2, 9),
      status: 'pending',
      progress: 0,
      error: null
    }));
    
    // Validate file size (max 100MB)
    const validFiles = newFiles.filter(fileItem => {
      if (fileItem.file.size > 100 * 1024 * 1024) {
        fileItem.error = 'File size exceeds 100MB limit';
        return false;
      }
      return true;
    });

    if (validFiles.length !== newFiles.length) {
      setUploadStatus({ 
        type: 'warning', 
        message: `${newFiles.length - validFiles.length} file(s) were rejected due to size limits` 
      });
    }

    setFiles(prev => [...prev, ...validFiles]);
    
    if (validFiles.length > 0) {
      setUploadStatus({ 
        type: 'success', 
        message: `Added ${validFiles.length} file(s) for analysis` 
      });
    }
  };

  const handleUpload = async () => {
    if (files.length === 0) return;
    
    // Check if user is authenticated
    if (!isAuthenticated()) {
      setUploadStatus({ 
        type: 'error', 
        message: 'Please log in first to analyze files. Click the Login button above.' 
      });
      return;
    }
    
    // Check if API key is available
    const currentApiKey = localStorage.getItem('gemini_api_key');
    if (!currentApiKey) {
      setApiKeyDialog(true);
      return;
    }
    
    setUploading(true);
    setUploadStatus({ type: 'info', message: 'Starting analysis...' });

    try {
      // Process each file with backend API
      for (let i = 0; i < files.length; i++) {
        const file = files[i];
        
        // Update status to analyzing
        setFiles(prev => prev.map(f => 
          f.id === file.id ? { ...f, status: 'analyzing', progress: 0 } : f
        ));

        try {
          // Create FormData for file upload
          const formData = new FormData();
          formData.append('file', file.file);
          formData.append('description', `Analysis of ${file.file.name}`);
          formData.append('tags', 'web_upload,database_analysis');

          // Step 1: Upload file to backend (25% progress)
          setFiles(prev => prev.map(f => 
            f.id === file.id ? { ...f, progress: 25 } : f
          ));
          
          const uploadResponse = await fetch('http://localhost:5001/api/analysis/upload', {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${localStorage.getItem('token')}`,
            },
            body: formData
          });

          if (!uploadResponse.ok) {
            throw new Error(`Upload failed: ${uploadResponse.statusText}`);
          }

          const uploadResult = await uploadResponse.json();
          
          if (!uploadResult.success) {
            throw new Error(uploadResult.message || 'Upload failed');
          }

          // Step 2: Monitor analysis progress (50% progress)
          setFiles(prev => prev.map(f => 
            f.id === file.id ? { ...f, progress: 50 } : f
          ));

          // Poll for analysis completion
          const analysisId = uploadResult.analysis.id;
          let analysisComplete = false;
          let attempts = 0;
          const maxAttempts = 60; // 5 minutes max

          while (!analysisComplete && attempts < maxAttempts) {
            await new Promise(resolve => setTimeout(resolve, 5000)); // Wait 5 seconds
            
            try {
              const statusResponse = await fetch(`http://localhost:5001/api/analysis/${analysisId}`, {
                headers: {
                  'Authorization': `Bearer ${localStorage.getItem('token')}`,
                }
              });

              if (statusResponse.ok) {
                const statusResult = await statusResponse.json();
                const analysis = statusResult.analysis;

                if (analysis.status === 'completed') {
                  analysisComplete = true;
                  // Step 3: Complete analysis (100% progress)
                  setFiles(prev => prev.map(f => 
                    f.id === file.id ? { ...f, progress: 100, status: 'completed' } : f
                  ));
                  
                  // Store results for display
                  localStorage.setItem('lastAnalysis', JSON.stringify(analysis));
                  break;
                } else if (analysis.status === 'failed') {
                  throw new Error(analysis.errorMessage || 'Analysis failed');
                }
                // Continue polling if still processing
              }
            } catch (error) {
              console.error('Status check error:', error);
            }
            
            attempts++;
          }

          if (!analysisComplete) {
            throw new Error('Analysis timed out');
          }
          
        } catch (error) {
          console.error(`Analysis failed for ${file.file.name}:`, error);
          setFiles(prev => prev.map(f => 
            f.id === file.id ? { ...f, status: 'error', error: error.message } : f
          ));
        }
      }

      // Check if any files were successfully analyzed
      const successfulFiles = files.filter(f => f.status === 'completed');
      
      if (successfulFiles.length > 0) {
        setUploadStatus({ 
          type: 'success', 
          message: `Successfully analyzed ${successfulFiles.length} file(s)! Redirecting to results...` 
        });

        // Auto-redirect to results page after 2 seconds
        setTimeout(() => {
          window.location.href = '/results';
        }, 2000);
      } else {
        setUploadStatus({ 
          type: 'error', 
          message: 'All file analyses failed. Please check your API key and try again.' 
        });
      }

    } catch (error) {
      console.error('Analysis error:', error);
      setUploadStatus({ 
        type: 'error', 
        message: `Analysis failed: ${error.message}` 
      });
    } finally {
      setUploading(false);
    }
  };

  const handleApiKeySubmit = () => {
    if (apiKey.trim()) {
      localStorage.setItem('gemini_api_key', apiKey.trim());
      setApiKeyDialog(false);
      setUploadStatus({ 
        type: 'success', 
        message: 'API key saved! You can now analyze your database files.' 
      });
    }
  };

  const removeFile = (fileId) => {
    setFiles(prev => prev.filter(f => f.id !== fileId));
  };

  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        Upload Database Files
      </Typography>
      
      {/* Authentication Status */}
      {!isAuthenticated() && (
        <Alert severity="warning" sx={{ mb: 3 }}>
          <Typography variant="body2">
            <strong>Authentication Required:</strong> You need to log in to analyze database files.
            <Button 
              size="small" 
              sx={{ ml: 2 }} 
              onClick={() => navigate('/login')}
              startIcon={<LoginIcon />}
            >
              Login
            </Button>
            <Button 
              size="small" 
              sx={{ ml: 1 }} 
              onClick={() => navigate('/register')}
              variant="outlined"
            >
              Register
            </Button>
          </Typography>
        </Alert>
      )}

      {/* API Key Status */}
      {isAuthenticated() && !localStorage.getItem('gemini_api_key') && (
        <Alert severity="warning" sx={{ mb: 3 }}>
          <Typography variant="body2">
            <strong>Gemini API Key Required:</strong> You need to provide your Google Gemini API key to analyze database files.
            <Button 
              size="small" 
              sx={{ ml: 2 }} 
              onClick={() => setApiKeyDialog(true)}
            >
              Add API Key
            </Button>
          </Typography>
        </Alert>
      )}

      {/* Test API Key Button */}
      {isAuthenticated() && localStorage.getItem('gemini_api_key') && (
        <Alert severity="info" sx={{ mb: 3 }}>
          <Typography variant="body2">
            <strong>API Key Found:</strong> Your Gemini API key is configured.
            <Button 
              size="small" 
              sx={{ ml: 2 }} 
              onClick={async () => {
                try {
                  setUploadStatus({ type: 'info', message: 'Testing API key...' });
                  const testResponse = await fetch('http://localhost:5001/api/health');
                  if (testResponse.ok) {
                    setUploadStatus({ type: 'success', message: 'Backend connection successful! API key is configured.' });
                  } else {
                    throw new Error('Backend not responding');
                  }
                } catch (error) {
                  setUploadStatus({ type: 'error', message: `Connection test failed: ${error.message}. Make sure the backend is running.` });
                }
              }}
            >
              Test Connection
            </Button>
          </Typography>
        </Alert>
      )}
      
      {/* File Selection */}
      <Paper elevation={2} sx={{ p: 4, mb: 3, textAlign: 'center' }}>
        <UploadIcon sx={{ fontSize: 60, color: 'primary.main', mb: 2 }} />
        <Typography variant="h6" gutterBottom>
          Select Database Files for Analysis
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
          Supported formats: .db, .sqlite, .csv, .xlsx, .json
        </Typography>
        
        <input
          accept=".db,.sqlite,.sqlite3,.csv,.xlsx,.json"
          style={{ display: 'none' }}
          id="file-input"
          multiple
          type="file"
          onChange={handleFileSelect}
        />
        <label htmlFor="file-input">
          <Button variant="contained" component="span" size="large">
            Select Files
          </Button>
        </label>
        
        {files.length > 0 && (
          <Typography variant="body2" color="primary" sx={{ mt: 2, fontWeight: 'bold' }}>
            {files.length} file(s) selected
          </Typography>
        )}
      </Paper>

      {/* Status Messages */}
      {uploadStatus && (
        <Alert severity={uploadStatus.type} sx={{ mb: 3 }}>
          {uploadStatus.message}
        </Alert>
      )}

      {/* File List */}
      {files.length > 0 && (
        <Paper elevation={2} sx={{ p: 3, mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            Selected Files ({files.length})
          </Typography>
          <List>
            {files.map((fileItem) => (
              <ListItem key={fileItem.id} divider>
                <ListItemIcon>
                  <FileIcon color="primary" />
                </ListItemIcon>
                <ListItemText
                  primary={fileItem.file.name}
                  secondary={`${(fileItem.file.size / 1024 / 1024).toFixed(2)} MB`}
                />
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  {fileItem.status === 'pending' && (
                    <Chip label="Pending" color="default" size="small" />
                  )}
                  {fileItem.status === 'analyzing' && (
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, minWidth: 120 }}>
                      <CircularProgress size={20} />
                      <Typography variant="body2">{fileItem.progress}%</Typography>
                    </Box>
                  )}
                  {fileItem.status === 'completed' && (
                    <Chip 
                      icon={<CheckIcon />} 
                      label="Completed" 
                      color="success" 
                      size="small" 
                    />
                  )}
                  {fileItem.status === 'error' && (
                    <Chip 
                      label={fileItem.error || 'Error'} 
                      color="error" 
                      size="small" 
                    />
                  )}
                  <Button 
                    size="small" 
                    color="error" 
                    onClick={() => removeFile(fileItem.id)}
                  >
                    Remove
                  </Button>
                </Box>
              </ListItem>
            ))}
          </List>
        </Paper>
      )}

      {/* Upload Button */}
      {files.length > 0 && (
        <Box sx={{ textAlign: 'center' }}>
          <Button
            variant="contained"
            size="large"
            onClick={handleUpload}
            disabled={uploading || !isAuthenticated() || !localStorage.getItem('gemini_api_key')}
            startIcon={uploading ? <CircularProgress size={20} /> : <UploadIcon />}
          >
            {uploading ? 'Analyzing...' : `Analyze ${files.length} File(s)`}
          </Button>
          
          {!isAuthenticated() && (
            <Typography variant="body2" color="error" sx={{ mt: 1 }}>
              Please log in to analyze files
            </Typography>
          )}
          
          {isAuthenticated() && !localStorage.getItem('gemini_api_key') && (
            <Typography variant="body2" color="error" sx={{ mt: 1 }}>
              API key required to analyze files
            </Typography>
          )}
        </Box>
      )}

      {/* API Key Dialog */}
      <Dialog open={apiKeyDialog} onClose={() => setApiKeyDialog(false)}>
        <DialogTitle>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <KeyIcon color="primary" />
            Enter Gemini API Key
          </Box>
        </DialogTitle>
        <DialogContent>
          <Typography variant="body2" sx={{ mb: 2 }}>
            To analyze your database files, you need a Google Gemini API key. 
            Get one from <a href="https://makersuite.google.com/app/apikey" target="_blank" rel="noopener noreferrer">Google AI Studio</a>.
          </Typography>
          <TextField
            autoFocus
            margin="dense"
            label="API Key"
            type="password"
            fullWidth
            variant="outlined"
            value={apiKey}
            onChange={(e) => setApiKey(e.target.value)}
            placeholder="Enter your Gemini API key"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setApiKeyDialog(false)}>Cancel</Button>
          <Button onClick={handleApiKeySubmit} variant="contained">
            Save & Continue
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default WorkingUploadPage;
