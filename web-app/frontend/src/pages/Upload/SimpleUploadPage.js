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
  Chip
} from '@mui/material';
import { 
  CloudUpload as UploadIcon, 
  CheckCircle as CheckIcon,
  Description as FileIcon
} from '@mui/icons-material';

const SimpleUploadPage = () => {
  const [files, setFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState(null);

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
    
    setUploading(true);
    setUploadStatus({ type: 'info', message: 'Starting analysis...' });

    try {
      // Simulate analysis process
      for (let i = 0; i < files.length; i++) {
        const file = files[i];
        
        // Update status to analyzing
        setFiles(prev => prev.map(f => 
          f.id === file.id ? { ...f, status: 'analyzing', progress: 0 } : f
        ));

        // Simulate analysis progress
        for (let progress = 0; progress <= 100; progress += 10) {
          await new Promise(resolve => setTimeout(resolve, 100));
          setFiles(prev => prev.map(f => 
            f.id === file.id ? { ...f, progress } : f
          ));
        }

        // Mark as completed
        setFiles(prev => prev.map(f => 
          f.id === file.id ? { ...f, status: 'completed', progress: 100 } : f
        ));
      }

      // Generate analysis results
      const analysisResults = generateAnalysisResults(files);
      
      // Store results for display
      localStorage.setItem('lastAnalysis', JSON.stringify(analysisResults));
      
      setUploadStatus({ 
        type: 'success', 
        message: `Successfully analyzed ${files.length} file(s)! Redirecting to results...` 
      });

      // Auto-redirect to results page after 2 seconds
      setTimeout(() => {
        window.location.href = '/results';
      }, 2000);

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

  const generateAnalysisResults = (files) => {
    // Generate simulated analysis results
    const results = {
      analysisData: {
        businessDomain: 'Database Analysis',
        insights: [
          'Database structure detected',
          'Table relationships identified',
          'Data quality assessment completed',
          'Performance recommendations generated'
        ],
        recommendations: [
          'Consider indexing frequently queried columns',
          'Optimize table joins for better performance',
          'Implement data archiving for large tables',
          'Regular maintenance of database statistics'
        ],
        metadata: {
          fileType: files[0]?.file.name.split('.').pop() || 'db',
          fileSize: files[0]?.file.size || 0,
          analysisType: 'simulated',
          note: 'This is a simulated analysis. For real AI-powered analysis, integrate with external services.'
        }
      },
      fileName: files[0]?.file.name || 'Unknown',
      fileType: files[0]?.file.name.split('.').pop() || 'db',
      fileSize: files[0]?.file.size || 0,
      createdAt: new Date().toISOString()
    };

    return results;
  };

  const removeFile = (fileId) => {
    setFiles(prev => prev.filter(f => f.id !== fileId));
  };

  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        Upload Database Files
      </Typography>
      
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
                    <Chip label={`${fileItem.progress}%`} color="primary" size="small" />
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
            disabled={uploading}
            startIcon={uploading ? <UploadIcon /> : <UploadIcon />}
          >
            {uploading ? 'Analyzing...' : `Analyze ${files.length} File(s)`}
          </Button>
        </Box>
      )}
    </Box>
  );
};

export default SimpleUploadPage;
