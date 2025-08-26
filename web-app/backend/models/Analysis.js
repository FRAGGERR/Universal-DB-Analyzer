const mongoose = require('mongoose');

const analysisSchema = new mongoose.Schema({
  user: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
  fileName: {
    type: String,
    required: true,
    trim: true
  },
  originalName: {
    type: String,
    required: true,
    trim: true
  },
  fileType: {
    type: String,
    required: true,
    enum: ['db', 'sqlite', 'sqlite3', 'csv', 'xlsx', 'json']
  },
  fileSize: {
    type: Number,
    required: true
  },
  filePath: {
    type: String,
    required: true
  },
  status: {
    type: String,
    required: true,
    enum: ['pending', 'processing', 'completed', 'failed'],
    default: 'pending'
  },
  progress: {
    type: Number,
    min: 0,
    max: 100,
    default: 0
  },
  analysisData: {
    businessDomain: {
      primaryDomain: String,
      confidenceScore: Number,
      subDomains: [String],
      businessProcesses: [String]
    },
    architecture: {
      designPattern: String,
      architecturalStyle: String,
      normalizationLevel: String,
      flexibilityScore: Number
    },
    entities: [{
      tableName: String,
      entityName: String,
      businessPurpose: String,
      dataVolume: String,
      rowCount: Number,
      columnCount: Number
    }],
    relationships: [{
      parentEntity: String,
      childEntity: String,
      relationshipType: String,
      businessMeaning: String
    }],
    dataQuality: {
      referentialIntegrity: String,
      dataConsistency: String,
      completenessScore: Number,
      accuracyIndicators: [String]
    },
    performance: {
      queryPatterns: [String],
      bottlenecks: [String],
      optimizationOpportunities: [String]
    },
    useCases: {
      primaryUseCases: [{
        useCase: String,
        description: String,
        businessValue: String
      }],
      analyticsOpportunities: [String]
    },
    migration: {
      complexityAssessment: String,
      migrationEffort: String,
      recommendations: [String]
    }
  },
  generatedFiles: {
    report: String,
    graphs: [String],
    jsonData: String,
    htmlReport: String
  },
  processingTime: {
    type: Number, // in seconds
    default: 0
  },
  errorMessage: {
    type: String,
    default: null
  },
  metadata: {
    tableCount: Number,
    totalRows: Number,
    totalColumns: Number,
    hasForeignKeys: Boolean,
    hasIndexes: Boolean
  },
  tags: [{
    type: String,
    trim: true
  }],
  isPublic: {
    type: Boolean,
    default: false
  },
  views: {
    type: Number,
    default: 0
  },
  downloads: {
    type: Number,
    default: 0
  }
}, {
  timestamps: true,
  toJSON: { virtuals: true },
  toObject: { virtuals: true }
});

// Virtual for analysis duration
analysisSchema.virtual('duration').get(function() {
  if (this.processingTime) {
    const minutes = Math.floor(this.processingTime / 60);
    const seconds = this.processingTime % 60;
    return minutes > 0 ? `${minutes}m ${seconds}s` : `${seconds}s`;
  }
  return 'N/A';
});

// Virtual for file size in human readable format
analysisSchema.virtual('fileSizeFormatted').get(function() {
  if (this.fileSize < 1024) return `${this.fileSize} B`;
  if (this.fileSize < 1024 * 1024) return `${(this.fileSize / 1024).toFixed(1)} KB`;
  if (this.fileSize < 1024 * 1024 * 1024) return `${(this.fileSize / (1024 * 1024)).toFixed(1)} MB`;
  return `${(this.fileSize / (1024 * 1024 * 1024)).toFixed(1)} GB`;
});

// Indexes for better query performance
analysisSchema.index({ user: 1, createdAt: -1 });
analysisSchema.index({ status: 1 });
analysisSchema.index({ fileType: 1 });
analysisSchema.index({ 'analysisData.businessDomain.primaryDomain': 1 });
analysisSchema.index({ tags: 1 });
analysisSchema.index({ isPublic: 1, createdAt: -1 });

// Pre-save middleware to update user stats
analysisSchema.pre('save', async function(next) {
  if (this.isModified('status') && this.status === 'completed' && this.processingTime > 0) {
    try {
      await this.model('User').findByIdAndUpdate(
        this.user,
        {
          $inc: { analysisCount: 1, totalAnalysisTime: this.processingTime }
        }
      );
    } catch (error) {
      console.error('Error updating user stats:', error);
    }
  }
  next();
});

// Static method to find public analyses
analysisSchema.statics.findPublic = function() {
  return this.find({ isPublic: true, status: 'completed' })
    .populate('user', 'username firstName lastName')
    .sort({ createdAt: -1 });
};

// Static method to find by user
analysisSchema.statics.findByUser = function(userId) {
  return this.find({ user: userId })
    .sort({ createdAt: -1 });
};

// Static method to find by status
analysisSchema.statics.findByStatus = function(status) {
  return this.find({ status: status })
    .populate('user', 'username firstName lastName')
    .sort({ createdAt: -1 });
};

// Method to increment views
analysisSchema.methods.incrementViews = function() {
  this.views += 1;
  return this.save();
};

// Method to increment downloads
analysisSchema.methods.incrementDownloads = function() {
  this.downloads += 1;
  return this.save();
};

// Method to add tag
analysisSchema.methods.addTag = function(tag) {
  if (!this.tags.includes(tag)) {
    this.tags.push(tag);
  }
  return this.save();
};

// Method to remove tag
analysisSchema.methods.removeTag = function(tag) {
  this.tags = this.tags.filter(t => t !== tag);
  return this.save();
};

module.exports = mongoose.model('Analysis', analysisSchema);
