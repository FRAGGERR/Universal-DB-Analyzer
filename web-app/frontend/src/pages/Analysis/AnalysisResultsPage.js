import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Paper, 
  Grid, 
  Card, 
  CardContent, 
  CardHeader,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Button,
  Alert
} from '@mui/material';
import { 
  Database as DatabaseIcon,
  Insights as InsightsIcon,
  Assessment as AssessmentIcon,
  Download as DownloadIcon,
  Share as ShareIcon
} from '@mui/icons-material';
import { useLocation, useNavigate } from 'react-router-dom';

const AnalysisResultsPage = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const [analysisData, setAnalysisData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Get analysis data from location state or localStorage
    if (location.state?.analysis) {
      setAnalysisData(location.state.analysis);
      setLoading(false);
    } else {
      // Try to get from localStorage
      const storedAnalysis = localStorage.getItem('lastAnalysis');
      if (storedAnalysis) {
        try {
          setAnalysisData(JSON.parse(storedAnalysis));
        } catch (error) {
          console.error('Error parsing stored analysis:', error);
        }
      }
      setLoading(false);
    }
  }, [location]);

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '60vh' }}>
        <Typography variant="h6">Loading analysis results...</Typography>
      </Box>
    );
  }

  if (!analysisData) {
    return (
      <Box sx={{ textAlign: 'center', py: 4 }}>
        <Typography variant="h5" gutterBottom>
          No Analysis Results Found
        </Typography>
        <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
          Please upload a database file to see analysis results.
        </Typography>
        <Button 
          variant="contained" 
          onClick={() => navigate('/upload')}
        >
          Upload Database
        </Button>
      </Box>
    );
  }

  // Extract data safely with fallbacks
  const analysis = analysisData.analysisData || {};
  const fileName = analysisData.fileName || 'Unknown File';
  const fileType = analysisData.fileType || 'unknown';
  const fileSize = analysisData.fileSize || 0;
  const createdAt = analysisData.createdAt || new Date().toISOString();

  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        Analysis Results
      </Typography>

      {/* File Information */}
      <Paper elevation={2} sx={{ p: 3, mb: 3 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item>
            <DatabaseIcon sx={{ fontSize: 40, color: 'primary.main' }} />
          </Grid>
          <Grid item xs>
            <Typography variant="h6" gutterBottom>
              {fileName}
            </Typography>
            <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
              <Chip label={fileType.toUpperCase()} color="primary" size="small" />
              <Chip label={`${(fileSize / 1024 / 1024).toFixed(2)} MB`} variant="outlined" size="small" />
              <Chip label={new Date(createdAt).toLocaleDateString()} variant="outlined" size="small" />
            </Box>
          </Grid>
          <Grid item>
            <Box sx={{ display: 'flex', gap: 1 }}>
              <Button variant="outlined" startIcon={<DownloadIcon />}>
                Download Report
              </Button>
              <Button variant="outlined" startIcon={<ShareIcon />}>
                Share
              </Button>
            </Box>
          </Grid>
        </Grid>
      </Paper>

      {/* Analysis Results Grid */}
      <Grid container spacing={3}>
        {/* Business Domain */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader
              title="Business Domain"
              avatar={<InsightsIcon color="primary" />}
            />
            <CardContent>
              <Typography variant="h6" color="primary" gutterBottom>
                {analysis.businessDomain || 'Unknown'}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                The detected business domain for this database.
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Key Insights */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader
              title="Key Insights"
              avatar={<AssessmentIcon color="primary" />}
            />
            <CardContent>
              <List dense>
                {(analysis.insights || []).map((insight, index) => (
                  <ListItem key={index} sx={{ px: 0 }}>
                    <ListItemIcon sx={{ minWidth: 32 }}>
                      <Chip label="✓" size="small" color="success" />
                    </ListItemIcon>
                    <ListItemText primary={insight} />
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>

        {/* Recommendations */}
        <Grid item xs={12}>
          <Card>
            <CardHeader title="Recommendations" />
            <CardContent>
              <Grid container spacing={2}>
                {(analysis.recommendations || []).map((rec, index) => (
                  <Grid item xs={12} md={4} key={index}>
                    <Paper elevation={1} sx={{ p: 2, bgcolor: 'grey.50' }}>
                      <Typography variant="body2" color="text.secondary">
                        {rec}
                      </Typography>
                    </Paper>
                  </Grid>
                ))}
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Metadata */}
        <Grid item xs={12}>
          <Card>
            <CardHeader title="Analysis Metadata" />
            <CardContent>
              <Grid container spacing={2}>
                <Grid item xs={6} md={3}>
                  <Typography variant="body2" color="text.secondary">
                    Analysis Type
                  </Typography>
                  <Typography variant="body1">
                    {analysis.metadata?.analysisType || 'Unknown'}
                  </Typography>
                </Grid>
                <Grid item xs={6} md={3}>
                  <Typography variant="body2" color="text.secondary">
                    File Type
                  </Typography>
                  <Typography variant="body1">
                    {analysis.metadata?.fileType || fileType}
                  </Typography>
                </Grid>
                <Grid item xs={6} md={3}>
                  <Typography variant="body2" color="text.secondary">
                    File Size
                  </Typography>
                  <Typography variant="body1">
                    {analysis.metadata?.fileSize || fileSize} bytes
                  </Typography>
                </Grid>
                <Grid item xs={6} md={3}>
                  <Typography variant="body2" color="text.secondary">
                    Status
                  </Typography>
                  <Chip 
                    label="Completed" 
                    color="success" 
                    size="small" 
                  />
                </Grid>
              </Grid>
              
              {analysis.metadata?.note && (
                <Alert severity="info" sx={{ mt: 2 }}>
                  {analysis.metadata.note}
                </Alert>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Action Buttons */}
      <Box sx={{ textAlign: 'center', mt: 4 }}>
        <Button 
          variant="contained" 
          onClick={() => navigate('/upload')}
          sx={{ mr: 2 }}
        >
          Analyze Another File
        </Button>
        <Button 
          variant="outlined" 
          onClick={() => navigate('/')}
        >
          Back to Home
        </Button>
      </Box>
    </Box>
  );
};

export default AnalysisResultsPage;
