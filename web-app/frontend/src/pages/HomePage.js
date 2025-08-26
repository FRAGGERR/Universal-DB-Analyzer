import React from 'react';
import { Box, Typography, Button, Paper, Grid } from '@mui/material';
import { Upload as UploadIcon, Analytics as AnalyticsIcon, Storage as StorageIcon } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';

const HomePage = () => {
  const navigate = useNavigate();

  return (
    <Box>
      {/* Hero Section */}
      <Paper elevation={3} sx={{ p: 4, mb: 4, textAlign: 'center', bgcolor: 'primary.light', color: 'white' }}>
        <Typography variant="h2" component="h1" gutterBottom>
          Database Analysis Tool
        </Typography>
        <Typography variant="h5" component="h2" gutterBottom>
          AI-Powered Database Reverse Engineering Analysis
        </Typography>
        <Typography variant="body1" sx={{ mb: 3 }}>
          Upload your database files and get instant insights about structure, business domain, and optimization opportunities.
        </Typography>
        <Button 
          variant="contained" 
          size="large" 
          startIcon={<UploadIcon />}
          onClick={() => navigate('/upload')}
        >
          Start Analysis
        </Button>
      </Paper>

      {/* Features Section */}
      <Grid container spacing={4}>
        <Grid item xs={12} md={4}>
          <Paper elevation={2} sx={{ p: 3, textAlign: 'center', height: '100%' }}>
            <UploadIcon sx={{ fontSize: 60, color: 'primary.main', mb: 2 }} />
            <Typography variant="h5" component="h3" gutterBottom>
              Easy Upload
            </Typography>
            <Typography variant="body1">
              Support for multiple file formats: .db, .sqlite, .csv, .xlsx, .json
            </Typography>
          </Paper>
        </Grid>
        
        <Grid item xs={12} md={4}>
          <Paper elevation={2} sx={{ p: 3, textAlign: 'center', height: '100%' }}>
            <AnalyticsIcon sx={{ fontSize: 60, color: 'primary.main', mb: 2 }} />
            <Typography variant="h5" component="h3" gutterBottom>
              AI Analysis
            </Typography>
            <Typography variant="body1">
              Get intelligent insights about business domain, architecture, and performance
            </Typography>
          </Paper>
        </Grid>
        
        <Grid item xs={12} md={4}>
          <Paper elevation={2} sx={{ p: 3, textAlign: 'center', height: '100%' }}>
            <StorageIcon sx={{ fontSize: 60, color: 'primary.main', mb: 2 }} />
            <Typography variant="h5" component="h3" gutterBottom>
              Comprehensive Reports
            </Typography>
            <Typography variant="body1">
              Download detailed reports with visualizations and recommendations
            </Typography>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default HomePage;
