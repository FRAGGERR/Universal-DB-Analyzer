import React, { useState } from 'react';
import { 
  Box, 
  Typography, 
  Paper, 
  Button, 
  Alert,
  CircularProgress,
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
import { useDropzone } from 'react-dropzone';

const UploadPage = () => {
  const [files, setFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState(null);

  const onDrop = (acceptedFiles) => {
    const newFiles = acceptedFiles.map(file => ({
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
        message: `Added ${validFiles.length} file(s) for upload` 
      });
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/x-sqlite3': ['.db', '.sqlite', '.sqlite3'],
      'application/vnd.sqlite3': ['.db', '.sqlite', '.sqlite3'],
      'text/csv': ['.csv'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'application/json': ['.json']
    },
    multiple: true
  });

  const handleUpload = async () => {
    if (files.length === 0) return;
    
    setUploading(true);
    setUploadStatus({ type: 'info', message: 'Starting upload and analysis...' });

    try {
      let successfulUploads = [];
      
      // Upload and analyze each file
      for (let i = 0; i < files.length; i++) {
        const file = files[i];
        
        // Update status to uploading
        setFiles(prev => prev.map(f => 
          f.id === file.id ? { ...f, status: 'uploading', progress: 0 } : f
        ));

        // Create FormData for upload
        const formData = new FormData();
        formData.append('file', file.file);
        formData.append('description', `Analysis of ${file.file.name}`);

        try {
          // Upload file to backend (Vercel API)
          const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData,
            headers: {
              'x-file-name': file.file.name
            }
          });

          if (!response.ok) {
            throw new Error(`Upload failed: ${response.statusText}`);
          }

          const result = await response.json();
          
          if (result.success) {
            // For Vercel, analysis is completed immediately
            setFiles(prev => prev.map(f => 
              f.id === file.id ? { ...f, status: 'completed', progress: 100, analysisId: result.analysis.id } : f
            ));

            // Store successful upload
            successfulUploads.push(result.analysis);

            // Update status message
            setUploadStatus({ 
              type: 'success', 
              message: `Successfully analyzed ${file.file.name}!` 
            });
          } else {
            throw new Error(result.message || 'Upload failed');
          }

        } catch (error) {
          console.error(`Error processing ${file.file.name}:`, error);
          setFiles(prev => prev.map(f => 
            f.id === file.id ? { ...f, status: 'error', progress: 0, error: error.message } : f
          ));
        }
      }

      // Check if any files were successful
      if (successfulUploads.length > 0) {
        // Store the first successful analysis for results page
        localStorage.setItem('lastAnalysis', JSON.stringify(successfulUploads[0]));
        
        setUploadStatus({ 
          type: 'success', 
          message: `Successfully processed ${successfulUploads.length} file(s)! Redirecting to results...` 
        });

        // Auto-redirect to results page after 2 seconds
        setTimeout(() => {
          window.location.href = '/results';
        }, 2000);
      } else {
        setUploadStatus({ 
          type: 'error', 
          message: 'All file uploads failed. Please try again.' 
        });
      }

    } catch (error) {
      console.error('Upload error:', error);
      setUploadStatus({ 
        type: 'error', 
        message: `Upload failed: ${error.message}` 
      });
    } finally {
      setUploading(false);
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
      
      {/* Upload Area */}
      <Paper 
        elevation={2} 
        sx={{ 
          p: 4, 
          mb: 3, 
          border: '2px dashed',
          borderColor: isDragActive ? 'primary.main' : 'grey.300',
          bgcolor: isDragActive ? 'primary.50' : 'grey.50',
          transition: 'all 0.2s ease',
          cursor: 'pointer'
        }}
        {...getRootProps()}
      >
        <input {...getInputProps()} />
        <Box sx={{ textAlign: 'center' }}>
          <UploadIcon sx={{ fontSize: 60, color: 'primary.main', mb: 2 }} />
          <Typography variant="h6" gutterBottom>
            {isDragActive ? 'Drop files here' : 'Drag & drop files here, or click to select'}
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Supported formats: .db, .sqlite, .csv, .xlsx, .json
          </Typography>
          <Typography variant="body2" color="primary" sx={{ mb: 2, fontWeight: 'bold' }}>
            {files.length > 0 ? `${files.length} file(s) selected` : 'No files selected'}
          </Typography>
          <Button variant="outlined" color="primary">
            Select Files
          </Button>
        </Box>
      </Paper>

      {/* Status Messages */}
      {uploadStatus && (
        <Alert severity={uploadStatus.type} sx={{ mb: 3 }}>
          {uploadStatus.message}
        </Alert>
      )}

      {/* Upload Progress Summary */}
      {files.length > 0 && (
        <Paper elevation={1} sx={{ p: 2, mb: 3, bgcolor: 'grey.50' }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant="body2" color="text.secondary">
              Total Files: {files.length}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Completed: {files.filter(f => f.status === 'completed').length}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Pending: {files.filter(f => f.status === 'pending').length}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Uploading: {files.filter(f => f.status === 'uploading').length}
            </Typography>
          </Box>
        </Paper>
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
                  {fileItem.status === 'uploading' && (
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
            disabled={uploading}
            startIcon={uploading ? <CircularProgress size={20} /> : <UploadIcon />}
          >
            {uploading ? 'Processing...' : `Upload & Analyze ${files.length} File(s)`}
          </Button>
        </Box>
      )}
    </Box>
  );
};

export default UploadPage;
