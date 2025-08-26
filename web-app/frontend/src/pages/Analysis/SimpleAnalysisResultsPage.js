import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Button, 
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
  Alert,
  Accordion,
  AccordionSummary,
  AccordionDetails
} from '@mui/material';
import { 
  Storage as DatabaseIcon,
  Insights as InsightsIcon,
  Assessment as AssessmentIcon,
  Download as DownloadIcon,
  Share as ShareIcon,
  ExpandMore as ExpandMoreIcon,
  Business as BusinessIcon,
  Architecture as ArchitectureIcon
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';

const SimpleAnalysisResultsPage = () => {
  const navigate = useNavigate();
  const [analysisData, setAnalysisData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Get analysis data from localStorage
    const storedAnalysis = localStorage.getItem('lastAnalysis');
    if (storedAnalysis) {
      try {
        const parsed = JSON.parse(storedAnalysis);
        setAnalysisData(parsed);
      } catch (error) {
        console.error('Error parsing stored analysis:', error);
      }
    }
    setLoading(false);
  }, []);

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
  const metadata = analysis.metadata || {};

  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        AI-Powered Database Analysis Results
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
              <Chip 
                label={`AI Analysis`} 
                color="success" 
                size="small" 
                icon={<InsightsIcon />}
              />
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
              avatar={<BusinessIcon color="primary" />}
            />
            <CardContent>
              <Typography variant="h6" color="primary" gutterBottom>
                {analysis.businessDomain || 'Unknown'}
              </Typography>
              {metadata.subDomains && metadata.subDomains.length > 0 && (
                <Box sx={{ mt: 2 }}>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    Sub-domains:
                  </Typography>
                  <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                    {metadata.subDomains.map((domain, index) => (
                      <Chip key={index} label={domain} size="small" variant="outlined" />
                    ))}
                  </Box>
                </Box>
              )}
              {metadata.confidenceScore > 0 && (
                <Box sx={{ mt: 2 }}>
                  <Typography variant="body2" color="text.secondary">
                    Confidence: {metadata.confidenceScore}%
                  </Typography>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Data Architecture */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader
              title="Data Architecture"
              avatar={<ArchitectureIcon color="primary" />}
            />
            <CardContent>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                Design Pattern:
              </Typography>
              <Typography variant="body1" gutterBottom>
                {metadata.designPattern || 'Unknown'}
              </Typography>
              
              <Typography variant="body2" color="text.secondary" gutterBottom>
                Normalization Level:
              </Typography>
              <Typography variant="body1" gutterBottom>
                {metadata.normalizationLevel || 'Unknown'}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Key Insights */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader
              title="Key Insights"
              avatar={<InsightsIcon color="primary" />}
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
        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader
              title="AI Recommendations"
              avatar={<AssessmentIcon color="primary" />}
            />
            <CardContent>
              <List dense>
                {(analysis.recommendations || []).map((rec, index) => (
                  <ListItem key={index} sx={{ px: 0 }}>
                    <ListItemIcon sx={{ minWidth: 32 }}>
                      <Chip label="💡" size="small" color="info" />
                    </ListItemIcon>
                    <ListItemText primary={rec} />
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>

        {/* Detailed Analysis */}
        <Grid item xs={12}>
          <Card>
            <CardHeader title="Detailed Analysis" />
            <CardContent>
              <Accordion>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Typography variant="h6">Table Purposes & Relationships</Typography>
                </AccordionSummary>
                <AccordionDetails>
                  {metadata.tablePurposes && Object.keys(metadata.tablePurposes).length > 0 ? (
                    <Grid container spacing={2}>
                      {Object.entries(metadata.tablePurposes).map(([tableName, purpose]) => (
                        <Grid item xs={12} md={6} key={tableName}>
                          <Paper elevation={1} sx={{ p: 2, bgcolor: 'grey.50' }}>
                            <Typography variant="subtitle2" color="primary" gutterBottom>
                              {tableName}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                              {purpose}
                            </Typography>
                          </Paper>
                        </Grid>
                      ))}
                    </Grid>
                  ) : (
                    <Typography variant="body2" color="text.secondary">
                      Table purpose analysis not available
                    </Typography>
                  )}
                </AccordionDetails>
              </Accordion>

              <Accordion>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Typography variant="h6">Column Semantics</Typography>
                </AccordionSummary>
                <AccordionDetails>
                  {metadata.columnSemantics && Object.keys(metadata.columnSemantics).length > 0 ? (
                    <Grid container spacing={2}>
                      {Object.entries(metadata.columnSemantics).map(([columnName, semantics]) => (
                        <Grid item xs={12} md={6} key={columnName}>
                          <Paper elevation={1} sx={{ p: 2, bgcolor: 'grey.50' }}>
                            <Typography variant="subtitle2" color="primary" gutterBottom>
                              {columnName}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                              {semantics}
                            </Typography>
                          </Paper>
                        </Grid>
                      ))}
                    </Grid>
                  ) : (
                    <Typography variant="body2" color="text.secondary">
                      Column semantics analysis not available
                    </Typography>
                  )}
                </AccordionDetails>
              </Accordion>

              <Accordion>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Typography variant="h6">Business Rules</Typography>
                </AccordionSummary>
                <AccordionDetails>
                  {metadata.businessRules && metadata.businessRules.length > 0 ? (
                    <List dense>
                      {metadata.businessRules.map((rule, index) => (
                        <ListItem key={index} sx={{ px: 0 }}>
                          <ListItemIcon sx={{ minWidth: 32 }}>
                            <Chip label="📋" size="small" color="warning" />
                          </ListItemIcon>
                          <ListItemText primary={rule} />
                        </ListItem>
                      ))}
                    </List>
                  ) : (
                    <Typography variant="body2" color="text.secondary">
                      Business rules analysis not available
                    </Typography>
                  )}
                </AccordionDetails>
              </Accordion>
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
                    {metadata.analysisType || 'Unknown'}
                  </Typography>
                </Grid>
                <Grid item xs={6} md={3}>
                  <Typography variant="body2" color="text.secondary">
                    File Type
                  </Typography>
                  <Typography variant="body1">
                    {metadata.fileType || fileType}
                  </Typography>
                </Grid>
                <Grid item xs={6} md={3}>
                  <Typography variant="body2" color="text.secondary">
                    File Size
                  </Typography>
                  <Typography variant="body1">
                    {metadata.fileSize || fileSize} bytes
                  </Typography>
                </Grid>
                <Grid item xs={6} md={3}>
                  <Typography variant="body2" color="text.secondary">
                    Status
                  </Typography>
                  <Chip 
                    label="AI Analysis Complete" 
                    color="success" 
                    size="small" 
                  />
                </Grid>
              </Grid>
              
              {metadata.note && (
                <Alert severity="info" sx={{ mt: 2 }}>
                  {metadata.note}
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

export default SimpleAnalysisResultsPage;
