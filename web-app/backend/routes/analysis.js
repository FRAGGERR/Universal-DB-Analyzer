const express = require('express');
const multer = require('multer');
const path = require('path');
const fs = require('fs-extra');
const { v4: uuidv4 } = require('uuid');
const { PythonShell } = require('python-shell');
const Analysis = require('../models/Analysis');
const { authMiddleware } = require('../middleware/auth');

const router = express.Router();

// Configure multer for file uploads
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    const uploadDir = path.join(__dirname, '../uploads');
    fs.ensureDirSync(uploadDir);
    cb(null, uploadDir);
  },
  filename: (req, file, cb) => {
    const uniqueName = `${uuidv4()}-${file.originalname}`;
    cb(null, uniqueName);
  }
});

const fileFilter = (req, file, cb) => {
  const allowedTypes = [
    'db', 'sqlite', 'sqlite3', 'csv', 'xlsx', 'json'
  ];
  
  const fileExtension = path.extname(file.originalname).toLowerCase().substring(1);
  
  if (allowedTypes.includes(fileExtension)) {
    cb(null, true);
  } else {
    cb(new Error(`File type .${fileExtension} is not supported. Allowed types: ${allowedTypes.join(', ')}`), false);
  }
};

const upload = multer({
  storage: storage,
  fileFilter: fileFilter,
  limits: {
    fileSize: 50 * 1024 * 1024, // 50MB limit
    files: 1
  }
});

// @route   POST /api/analysis/upload
// @desc    Upload and analyze a database file
// @access  Private
router.post('/upload', authMiddleware, upload.single('file'), async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({
        success: false,
        message: 'No file uploaded'
      });
    }

    const { description, tags } = req.body;
    const fileExtension = path.extname(req.file.originalname).toLowerCase().substring(1);
    
    // Create analysis record
    const analysis = new Analysis({
      user: req.user._id,
      fileName: req.file.filename,
      originalName: req.file.originalname,
      fileType: fileExtension,
      fileSize: req.file.size,
      filePath: req.file.path,
      tags: tags ? tags.split(',').map(tag => tag.trim()) : [],
      status: 'pending'
    });

    await analysis.save();

    // Start analysis in background
    processAnalysis(analysis._id, req.file.path, fileExtension, description);

    res.status(201).json({
      success: true,
      message: 'File uploaded successfully. Analysis started.',
      analysis: {
        id: analysis._id,
        fileName: analysis.fileName,
        originalName: analysis.originalName,
        fileType: analysis.fileType,
        fileSize: analysis.fileSize,
        status: analysis.status,
        progress: analysis.progress,
        createdAt: analysis.createdAt
      }
    });

  } catch (error) {
    console.error('Upload error:', error);
    
    // Clean up uploaded file if analysis creation failed
    if (req.file) {
      await fs.remove(req.file.path);
    }

    res.status(500).json({
      success: false,
      message: error.message || 'Internal server error during upload'
    });
  }
});

// @route   GET /api/analysis/:id
// @desc    Get analysis results by ID
// @access  Private
router.get('/:id', authMiddleware, async (req, res) => {
  try {
    const analysis = await Analysis.findById(req.params.id)
      .populate('user', 'username firstName lastName');

    if (!analysis) {
      return res.status(404).json({
        success: false,
        message: 'Analysis not found'
      });
    }

    // Check if user owns the analysis or if it's public
    if (analysis.user._id.toString() !== req.user._id.toString() && !analysis.isPublic) {
      return res.status(403).json({
        success: false,
        message: 'Access denied. You can only view your own analyses.'
      });
    }

    // Increment views
    await analysis.incrementViews();

    res.json({
      success: true,
      analysis
    });

  } catch (error) {
    console.error('Get analysis error:', error);
    res.status(500).json({
      success: false,
      message: 'Internal server error while fetching analysis'
    });
  }
});

// @route   GET /api/analysis
// @desc    Get user's analyses with pagination and filters
// @access  Private
router.get('/', authMiddleware, async (req, res) => {
  try {
    const { page = 1, limit = 10, status, fileType, search, sortBy = 'createdAt', sortOrder = 'desc' } = req.query;

    const query = { user: req.user._id };
    
    // Add filters
    if (status) query.status = status;
    if (fileType) query.fileType = fileType;
    if (search) {
      query.$or = [
        { originalName: { $regex: search, $options: 'i' } },
        { tags: { $in: [new RegExp(search, 'i')] } }
      ];
    }

    // Build sort object
    const sort = {};
    sort[sortBy] = sortOrder === 'desc' ? -1 : 1;

    const options = {
      page: parseInt(page),
      limit: parseInt(limit),
      sort,
      populate: { path: 'user', select: 'username firstName lastName' }
    };

    const analyses = await Analysis.paginate(query, options);

    res.json({
      success: true,
      analyses: analyses.docs,
      pagination: {
        page: analyses.page,
        limit: analyses.limit,
        totalPages: analyses.totalPages,
        totalDocs: analyses.totalDocs,
        hasNextPage: analyses.hasNextPage,
        hasPrevPage: analyses.hasPrevPage
      }
    });

  } catch (error) {
    console.error('Get analyses error:', error);
    res.status(500).json({
      success: false,
      message: 'Internal server error while fetching analyses'
    });
  }
});

// @route   PUT /api/analysis/:id
// @desc    Update analysis (tags, public status, etc.)
// @access  Private
router.put('/:id', authMiddleware, async (req, res) => {
  try {
    const { tags, isPublic, description } = req.body;
    
    const analysis = await Analysis.findById(req.params.id);
    
    if (!analysis) {
      return res.status(404).json({
        success: false,
        message: 'Analysis not found'
      });
    }

    // Check ownership
    if (analysis.user.toString() !== req.user._id.toString()) {
      return res.status(403).json({
        success: false,
        message: 'Access denied. You can only update your own analyses.'
      });
    }

    // Update fields
    if (tags !== undefined) {
      analysis.tags = Array.isArray(tags) ? tags : tags.split(',').map(tag => tag.trim());
    }
    if (isPublic !== undefined) analysis.isPublic = isPublic;

    await analysis.save();

    res.json({
      success: true,
      message: 'Analysis updated successfully',
      analysis
    });

  } catch (error) {
    console.error('Update analysis error:', error);
    res.status(500).json({
      success: false,
      message: 'Internal server error while updating analysis'
    });
  }
});

// @route   DELETE /api/analysis/:id
// @desc    Delete analysis and associated files
// @access  Private
router.delete('/:id', authMiddleware, async (req, res) => {
  try {
    const analysis = await Analysis.findById(req.params.id);
    
    if (!analysis) {
      return res.status(404).json({
        success: false,
        message: 'Analysis not found'
      });
    }

    // Check ownership
    if (analysis.user.toString() !== req.user._id.toString()) {
      return res.status(403).json({
        success: false,
        message: 'Access denied. You can only delete your own analyses.'
      });
    }

    // Remove files
    if (analysis.filePath && await fs.pathExists(analysis.filePath)) {
      await fs.remove(analysis.filePath);
    }

    // Remove generated files
    if (analysis.generatedFiles) {
      const filesToRemove = [
        analysis.generatedFiles.report,
        analysis.generatedFiles.jsonData,
        analysis.generatedFiles.htmlReport,
        ...(analysis.generatedFiles.graphs || [])
      ].filter(Boolean);

      for (const file of filesToRemove) {
        if (await fs.pathExists(file)) {
          await fs.remove(file);
        }
      }
    }

    // Delete analysis record
    await Analysis.findByIdAndDelete(req.params.id);

    res.json({
      success: true,
      message: 'Analysis deleted successfully'
    });

  } catch (error) {
    console.error('Delete analysis error:', error);
    res.status(500).json({
      success: false,
      message: 'Internal server error while deleting analysis'
    });
  }
});

// @route   GET /api/analysis/:id/download
// @desc    Download analysis report
// @access  Private
router.get('/:id/download', authMiddleware, async (req, res) => {
  try {
    const analysis = await Analysis.findById(req.params.id);
    
    if (!analysis) {
      return res.status(404).json({
        success: false,
        message: 'Analysis not found'
      });
    }

    // Check ownership
    if (analysis.user.toString() !== req.user._id.toString() && !analysis.isPublic) {
      return res.status(403).json({
        success: false,
        message: 'Access denied. You can only download your own analyses.'
      });
    }

    if (analysis.status !== 'completed') {
      return res.status(400).json({
        success: false,
        message: 'Analysis is not completed yet'
      });
    }

    // Increment downloads
    await analysis.incrementDownloads();

    // Determine which file to download
    let filePath = analysis.generatedFiles.report;
    let fileName = `${analysis.originalName}_analysis.md`;

    if (req.query.format === 'json' && analysis.generatedFiles.jsonData) {
      filePath = analysis.generatedFiles.jsonData;
      fileName = `${analysis.originalName}_analysis.json`;
    }

    if (!filePath || !await fs.pathExists(filePath)) {
      return res.status(404).json({
        success: false,
        message: 'Report file not found'
      });
    }

    res.download(filePath, fileName);

  } catch (error) {
    console.error('Download error:', error);
    res.status(500).json({
      success: false,
      message: 'Internal server error while downloading report'
    });
  }
});

// Background processing function
async function processAnalysis(analysisId, filePath, fileType, description) {
  try {
    console.log(`Starting analysis for file: ${filePath}, analysis: ${analysisId}, fileType: ${fileType}`);
    
    // Update status to processing
    await Analysis.findByIdAndUpdate(analysisId, {
      status: 'processing',
      progress: 10
    });

    // Use our new Python analysis service with absolute path
    const scriptPath = path.resolve(__dirname, '..', 'services', 'pythonAnalysisService.py');
    const scriptArgs = [filePath, analysisId, 'web_user']; // For now, use 'web_user' as default

    // Check if Python script exists
    if (!require('fs').existsSync(scriptPath)) {
      throw new Error(`Python analysis script not found at: ${scriptPath}`);
    }

    console.log('Python script path:', scriptPath);
    console.log('Script arguments:', scriptArgs);

    // Update progress
    await Analysis.findByIdAndUpdate(analysisId, { progress: 30 });

    // Run Python analysis with JSON output
    const options = {
      mode: 'json',
      pythonPath: process.env.PYTHON_PATH || 'python3',
      pythonOptions: ['-u'], // unbuffered output
      scriptPath: path.dirname(scriptPath),
      args: scriptArgs
    };

    console.log('Running Python analysis with options:', options);

    // Run the Python script
    const results = await new Promise((resolve, reject) => {
      PythonShell.run(path.basename(scriptPath), options, (err, results) => {
        if (err) {
          console.error('Python analysis error:', err);
          reject(err);
          return;
        }
        
        if (results && results.length > 0) {
          try {
            // Get the last result (should be the final output)
            const result = results[results.length - 1];
            console.log('Raw Python result:', result);
            resolve(result);
          } catch (parseError) {
            console.error('Error parsing Python results:', parseError);
            reject(new Error('Invalid analysis results format'));
          }
        } else {
          reject(new Error('No results from Python analysis'));
        }
      });
    });

    console.log('Python analysis results:', results);

    // Update progress
    await Analysis.findByIdAndUpdate(analysisId, { progress: 70 });

    // Process results and update analysis
    const analysisData = processAnalysisResults(results, fileType);
    
    // Update progress
    await Analysis.findByIdAndUpdate(analysisId, { progress: 90 });

    // Update analysis with results
    await Analysis.findByIdAndUpdate(analysisId, {
      status: 'completed',
      progress: 100,
      analysisData: results.results || results,
      generatedFiles: results.results?.files_generated || [],
      processingTime: Math.floor((Date.now() - new Date().getTime()) / 1000),
      metadata: {
        businessDomain: results.results?.summary?.business_domain,
        totalTables: results.results?.summary?.total_tables,
        confidenceScore: results.results?.summary?.confidence_score,
        analysisType: results.results?.analysis_type || 'database',
        tableCount: analysisData.entities?.length || 0,
        totalRows: analysisData.entities?.reduce((sum, entity) => sum + (entity.rowCount || 0), 0) || 0,
        totalColumns: analysisData.entities?.reduce((sum, entity) => sum + (entity.columnCount || 0), 0) || 0,
        hasForeignKeys: analysisData.relationships?.length > 0,
        hasIndexes: true // Default assumption
      }
    });

    console.log(`Analysis ${analysisId} completed successfully`);

  } catch (error) {
    console.error('Analysis processing error:', error);
    
    // Update analysis with error
    await Analysis.findByIdAndUpdate(analysisId, {
      status: 'failed',
      errorMessage: error.message || 'Unknown error during analysis'
    });
  }
}

// Helper function to process analysis results
function processAnalysisResults(results, fileType) {
  // This is a simplified version - you'll need to implement proper parsing
  // based on your Python script output format
  
  try {
    // Parse the results and extract relevant information
    // This is a placeholder implementation
    return {
      businessDomain: {
        primaryDomain: 'Database Analysis',
        confidenceScore: 85,
        subDomains: ['Data Management'],
        businessProcesses: ['Data Analysis', 'Reporting']
      },
      architecture: {
        designPattern: 'Relational',
        architecturalStyle: 'Traditional',
        normalizationLevel: '3NF',
        flexibilityScore: 75
      },
      entities: [],
      relationships: [],
      dataQuality: {
        referentialIntegrity: 'Good',
        dataConsistency: 'High',
        completenessScore: 80,
        accuracyIndicators: ['Valid data types', 'Constraints']
      },
      performance: {
        queryPatterns: ['SELECT queries', 'JOIN operations'],
        bottlenecks: ['Large table scans'],
        optimizationOpportunities: ['Add indexes', 'Optimize queries']
      },
      useCases: {
        primaryUseCases: [
          {
            useCase: 'Data Analysis',
            description: 'Analyze database structure and relationships',
            businessValue: 'Improved understanding of data architecture'
          }
        ],
        analyticsOpportunities: ['Performance optimization', 'Data modeling']
      },
      migration: {
        complexityAssessment: 'Medium',
        migrationEffort: '2-4 weeks',
        recommendations: ['Optimize queries', 'Add indexes']
      }
    };
  } catch (error) {
    console.error('Error processing analysis results:', error);
    return {
      businessDomain: { primaryDomain: 'Unknown', confidenceScore: 0 },
      architecture: { designPattern: 'Unknown', flexibilityScore: 0 },
      entities: [],
      relationships: [],
      dataQuality: { completenessScore: 0 },
      performance: { queryPatterns: [], bottlenecks: [], optimizationOpportunities: [] },
      useCases: { primaryUseCases: [], analyticsOpportunities: [] },
      migration: { complexityAssessment: 'Unknown', migrationEffort: 'Unknown' }
    };
  }
}

module.exports = router;
