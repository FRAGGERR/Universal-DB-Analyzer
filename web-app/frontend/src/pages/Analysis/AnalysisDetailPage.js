import React from 'react';
import { Box, Typography, Paper } from '@mui/material';

const AnalysisDetailPage = () => {
  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        Analysis Details
      </Typography>
      <Paper elevation={2} sx={{ p: 3 }}>
        <Typography variant="body1" color="text.secondary">
          Analysis detail functionality coming soon...
        </Typography>
      </Paper>
    </Box>
  );
};

export default AnalysisDetailPage;
