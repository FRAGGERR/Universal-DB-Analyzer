import React from 'react';
import { Box, Typography, Paper } from '@mui/material';

const ExplorePage = () => {
  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        Explore
      </Typography>
      <Paper elevation={2} sx={{ p: 3 }}>
        <Typography variant="body1" color="text.secondary">
          Explore functionality coming soon...
        </Typography>
      </Paper>
    </Box>
  );
};

export default ExplorePage;
