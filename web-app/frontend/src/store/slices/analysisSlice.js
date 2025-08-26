import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import analysisService from '../../services/analysisService';

// Async thunks
export const uploadFile = createAsyncThunk(
  'analysis/uploadFile',
  async (fileData, thunkAPI) => {
    try {
      const response = await analysisService.uploadFile(fileData);
      return response.data;
    } catch (error) {
      return thunkAPI.rejectWithValue(
        error.response?.data?.message || 'File upload failed'
      );
    }
  }
);

export const getAnalyses = createAsyncThunk(
  'analysis/getAnalyses',
  async (params, thunkAPI) => {
    try {
      const response = await analysisService.getAnalyses(params);
      return response.data;
    } catch (error) {
      return thunkAPI.rejectWithValue(
        error.response?.data?.message || 'Failed to fetch analyses'
      );
    }
  }
);

export const getAnalysisById = createAsyncThunk(
  'analysis/getAnalysisById',
  async (id, thunkAPI) => {
    try {
      const response = await analysisService.getAnalysisById(id);
      return response.data;
    } catch (error) {
      return thunkAPI.rejectWithValue(
        error.response?.data?.message || 'Failed to fetch analysis'
      );
    }
  }
);

export const updateAnalysis = createAsyncThunk(
  'analysis/updateAnalysis',
  async ({ id, updateData }, thunkAPI) => {
    try {
      const response = await analysisService.updateAnalysis(id, updateData);
      return response.data;
    } catch (error) {
      return thunkAPI.rejectWithValue(
        error.response?.data?.message || 'Failed to update analysis'
      );
    }
  }
);

export const deleteAnalysis = createAsyncThunk(
  'analysis/deleteAnalysis',
  async (id, thunkAPI) => {
    try {
      await analysisService.deleteAnalysis(id);
      return id;
    } catch (error) {
      return thunkAPI.rejectWithValue(
        error.response?.data?.message || 'Failed to delete analysis'
      );
    }
  }
);

export const downloadReport = createAsyncThunk(
  'analysis/downloadReport',
  async ({ id, format }, thunkAPI) => {
    try {
      const response = await analysisService.downloadReport(id, format);
      return response.data;
    } catch (error) {
      return thunkAPI.rejectWithValue(
        error.response?.data?.message || 'Failed to download report'
      );
    }
  }
);

// Initial state
const initialState = {
  analyses: [],
  currentAnalysis: null,
  isLoading: false,
  isUploading: false,
  error: null,
  pagination: {
    page: 1,
    limit: 10,
    totalPages: 0,
    totalDocs: 0,
    hasNextPage: false,
    hasPrevPage: false,
  },
  filters: {
    status: '',
    fileType: '',
    search: '',
    sortBy: 'createdAt',
    sortOrder: 'desc',
  },
  uploadProgress: 0,
};

// Slice
const analysisSlice = createSlice({
  name: 'analysis',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
    clearCurrentAnalysis: (state) => {
      state.currentAnalysis = null;
    },
    setFilters: (state, action) => {
      state.filters = { ...state.filters, ...action.payload };
      state.pagination.page = 1; // Reset to first page when filters change
    },
    setPage: (state, action) => {
      state.pagination.page = action.payload;
    },
    setUploadProgress: (state, action) => {
      state.uploadProgress = action.payload;
    },
    resetUploadProgress: (state) => {
      state.uploadProgress = 0;
    },
    addAnalysis: (state, action) => {
      state.analyses.unshift(action.payload);
    },
    updateAnalysisInList: (state, action) => {
      const index = state.analyses.findIndex(a => a._id === action.payload._id);
      if (index !== -1) {
        state.analyses[index] = action.payload;
      }
    },
    removeAnalysisFromList: (state, action) => {
      state.analyses = state.analyses.filter(a => a._id !== action.payload);
    },
  },
  extraReducers: (builder) => {
    builder
      // Upload File
      .addCase(uploadFile.pending, (state) => {
        state.isUploading = true;
        state.error = null;
        state.uploadProgress = 0;
      })
      .addCase(uploadFile.fulfilled, (state, action) => {
        state.isUploading = false;
        state.uploadProgress = 100;
        state.analyses.unshift(action.payload.analysis);
      })
      .addCase(uploadFile.rejected, (state, action) => {
        state.isUploading = false;
        state.error = action.payload;
        state.uploadProgress = 0;
      })
      
      // Get Analyses
      .addCase(getAnalyses.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(getAnalyses.fulfilled, (state, action) => {
        state.isLoading = false;
        state.analyses = action.payload.analyses;
        state.pagination = action.payload.pagination;
      })
      .addCase(getAnalyses.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload;
      })
      
      // Get Analysis by ID
      .addCase(getAnalysisById.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(getAnalysisById.fulfilled, (state, action) => {
        state.isLoading = false;
        state.currentAnalysis = action.payload.analysis;
      })
      .addCase(getAnalysisById.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload;
      })
      
      // Update Analysis
      .addCase(updateAnalysis.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(updateAnalysis.fulfilled, (state, action) => {
        state.isLoading = false;
        state.currentAnalysis = action.payload.analysis;
        // Update in list as well
        const index = state.analyses.findIndex(a => a._id === action.payload.analysis._id);
        if (index !== -1) {
          state.analyses[index] = action.payload.analysis;
        }
      })
      .addCase(updateAnalysis.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload;
      })
      
      // Delete Analysis
      .addCase(deleteAnalysis.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(deleteAnalysis.fulfilled, (state, action) => {
        state.isLoading = false;
        // Remove from list
        state.analyses = state.analyses.filter(a => a._id !== action.payload);
        // Clear current analysis if it was the deleted one
        if (state.currentAnalysis && state.currentAnalysis._id === action.payload) {
          state.currentAnalysis = null;
        }
      })
      .addCase(deleteAnalysis.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload;
      })
      
      // Download Report
      .addCase(downloadReport.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(downloadReport.fulfilled, (state) => {
        state.isLoading = false;
      })
      .addCase(downloadReport.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload;
      });
  },
});

export const {
  clearError,
  clearCurrentAnalysis,
  setFilters,
  setPage,
  setUploadProgress,
  resetUploadProgress,
  addAnalysis,
  updateAnalysisInList,
  removeAnalysisFromList,
} = analysisSlice.actions;

export default analysisSlice.reducer;
