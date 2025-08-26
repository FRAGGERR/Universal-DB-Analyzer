const express = require('express');
const Analysis = require('../models/Analysis');
const User = require('../models/User');
const { authMiddleware } = require('../middleware/auth');

const router = express.Router();

// @route   GET /api/dashboard/stats
// @desc    Get user dashboard statistics
// @access  Private
router.get('/stats', authMiddleware, async (req, res) => {
  try {
    const userId = req.user._id;

    // Get analysis statistics
    const totalAnalyses = await Analysis.countDocuments({ user: userId });
    const completedAnalyses = await Analysis.countDocuments({ 
      user: userId, 
      status: 'completed' 
    });
    const pendingAnalyses = await Analysis.countDocuments({ 
      user: userId, 
      status: { $in: ['pending', 'processing'] } 
    });
    const failedAnalyses = await Analysis.countDocuments({ 
      user: userId, 
      status: 'failed' 
    });

    // Get file type distribution
    const fileTypeStats = await Analysis.aggregate([
      { $match: { user: userId } },
      { $group: { _id: '$fileType', count: { $sum: 1 } } },
      { $sort: { count: -1 } }
    ]);

    // Get recent analyses
    const recentAnalyses = await Analysis.find({ user: userId })
      .sort({ createdAt: -1 })
      .limit(5)
      .select('originalName status createdAt fileType');

    // Get processing time statistics
    const processingStats = await Analysis.aggregate([
      { $match: { user: userId, status: 'completed', processingTime: { $gt: 0 } } },
      {
        $group: {
          _id: null,
          avgProcessingTime: { $avg: '$processingTime' },
          minProcessingTime: { $min: '$processingTime' },
          maxProcessingTime: { $max: '$processingTime' },
          totalProcessingTime: { $sum: '$processingTime' }
        }
      }
    ]);

    // Get business domain distribution
    const domainStats = await Analysis.aggregate([
      { $match: { user: userId, status: 'completed' } },
      { $group: { _id: '$analysisData.businessDomain.primaryDomain', count: { $sum: 1 } } },
      { $sort: { count: -1 } }
    ]);

    // Get monthly analysis trend
    const monthlyTrend = await Analysis.aggregate([
      { $match: { user: userId } },
      {
        $group: {
          _id: {
            year: { $year: '$createdAt' },
            month: { $month: '$createdAt' }
          },
          count: { $sum: 1 }
        }
      },
      { $sort: { '_id.year': 1, '_id.month': 1 } },
      { $limit: 12 }
    ]);

    res.json({
      success: true,
      stats: {
        totalAnalyses,
        completedAnalyses,
        pendingAnalyses,
        failedAnalyses,
        successRate: totalAnalyses > 0 ? Math.round((completedAnalyses / totalAnalyses) * 100) : 0,
        fileTypeDistribution: fileTypeStats,
        processingStats: processingStats[0] || {
          avgProcessingTime: 0,
          minProcessingTime: 0,
          maxProcessingTime: 0,
          totalProcessingTime: 0
        },
        domainDistribution: domainStats,
        monthlyTrend,
        recentAnalyses
      }
    });

  } catch (error) {
    console.error('Dashboard stats error:', error);
    res.status(500).json({
      success: false,
      message: 'Internal server error while fetching dashboard statistics'
    });
  }
});

// @route   GET /api/dashboard/analytics
// @desc    Get detailed analytics data
// @access  Private
router.get('/analytics', authMiddleware, async (req, res) => {
  try {
    const userId = req.user._id;
    const { timeframe = '30d' } = req.query;

    // Calculate date range
    const now = new Date();
    let startDate;
    
    switch (timeframe) {
      case '7d':
        startDate = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
        break;
      case '30d':
        startDate = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
        break;
      case '90d':
        startDate = new Date(now.getTime() - 90 * 24 * 60 * 60 * 1000);
        break;
      case '1y':
        startDate = new Date(now.getTime() - 365 * 24 * 60 * 60 * 1000);
        break;
      default:
        startDate = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
    }

    // Get analyses within timeframe
    const analyses = await Analysis.find({
      user: userId,
      createdAt: { $gte: startDate }
    }).select('createdAt status fileType processingTime analysisData');

    // Process analytics data
    const analytics = {
      totalFiles: analyses.length,
      fileTypeBreakdown: {},
      statusBreakdown: {},
      processingTimeDistribution: {
        fast: 0,    // < 1 minute
        medium: 0,  // 1-5 minutes
        slow: 0     // > 5 minutes
      },
      businessDomainBreakdown: {},
      averageProcessingTime: 0,
      peakUsageHours: {},
      dailyActivity: {}
    };

    let totalProcessingTime = 0;
    let completedCount = 0;

    analyses.forEach(analysis => {
      // File type breakdown
      analytics.fileTypeBreakdown[analysis.fileType] = 
        (analytics.fileTypeBreakdown[analysis.fileType] || 0) + 1;

      // Status breakdown
      analytics.statusBreakdown[analysis.status] = 
        (analytics.statusBreakdown[analysis.status] || 0) + 1;

      // Processing time analysis
      if (analysis.status === 'completed' && analysis.processingTime) {
        totalProcessingTime += analysis.processingTime;
        completedCount++;

        if (analysis.processingTime < 60) {
          analytics.processingTimeDistribution.fast++;
        } else if (analysis.processingTime < 300) {
          analytics.processingTimeDistribution.medium++;
        } else {
          analytics.processingTimeDistribution.slow++;
        }
      }

      // Business domain breakdown
      if (analysis.analysisData?.businessDomain?.primaryDomain) {
        const domain = analysis.analysisData.businessDomain.primaryDomain;
        analytics.businessDomainBreakdown[domain] = 
          (analytics.businessDomainBreakdown[domain] || 0) + 1;
      }

      // Peak usage hours
      const hour = analysis.createdAt.getHours();
      analytics.peakUsageHours[hour] = (analytics.peakUsageHours[hour] || 0) + 1;

      // Daily activity
      const date = analysis.createdAt.toISOString().split('T')[0];
      analytics.dailyActivity[date] = (analytics.dailyActivity[date] || 0) + 1;
    });

    // Calculate averages
    if (completedCount > 0) {
      analytics.averageProcessingTime = Math.round(totalProcessingTime / completedCount);
    }

    // Convert daily activity to sorted array
    analytics.dailyActivity = Object.entries(analytics.dailyActivity)
      .map(([date, count]) => ({ date, count }))
      .sort((a, b) => new Date(a.date) - new Date(b.date));

    // Convert peak usage hours to sorted array
    analytics.peakUsageHours = Object.entries(analytics.peakUsageHours)
      .map(([hour, count]) => ({ hour: parseInt(hour), count }))
      .sort((a, b) => a.hour - b.hour);

    res.json({
      success: true,
      analytics,
      timeframe,
      startDate,
      endDate: now
    });

  } catch (error) {
    console.error('Dashboard analytics error:', error);
    res.status(500).json({
      success: false,
      message: 'Internal server error while fetching analytics data'
    });
  }
});

// @route   GET /api/dashboard/public
// @desc    Get public analyses for discovery
// @access  Public (optional auth)
router.get('/public', async (req, res) => {
  try {
    const { page = 1, limit = 10, domain, fileType, sortBy = 'createdAt' } = req.query;

    const query = { isPublic: true, status: 'completed' };
    
    // Add filters
    if (domain) {
      query['analysisData.businessDomain.primaryDomain'] = { 
        $regex: domain, 
        $options: 'i' 
      };
    }
    if (fileType) query.fileType = fileType;

    // Build sort object
    const sort = {};
    sort[sortBy] = -1;

    const options = {
      page: parseInt(page),
      limit: parseInt(limit),
      sort,
      populate: { path: 'user', select: 'username firstName lastName' }
    };

    const publicAnalyses = await Analysis.paginate(query, options);

    res.json({
      success: true,
      analyses: publicAnalyses.docs,
      pagination: {
        page: publicAnalyses.page,
        limit: publicAnalyses.limit,
        totalPages: publicAnalyses.totalPages,
        totalDocs: publicAnalyses.totalDocs,
        hasNextPage: publicAnalyses.hasNextPage,
        hasPrevPage: publicAnalyses.hasPrevPage
      }
    });

  } catch (error) {
    console.error('Public analyses error:', error);
    res.status(500).json({
      success: false,
      message: 'Internal server error while fetching public analyses'
    });
  }
});

// @route   GET /api/dashboard/insights
// @desc    Get AI-generated insights and recommendations
// @access  Private
router.get('/insights', authMiddleware, async (req, res) => {
  try {
    const userId = req.user._id;

    // Get user's analysis patterns
    const analyses = await Analysis.find({ 
      user: userId, 
      status: 'completed' 
    }).select('fileType analysisData createdAt');

    // Generate insights based on patterns
    const insights = {
      fileTypePreference: null,
      commonDomains: [],
      performanceTrends: [],
      recommendations: [],
      learningPath: []
    };

    if (analyses.length > 0) {
      // File type preference
      const fileTypeCounts = {};
      analyses.forEach(analysis => {
        fileTypeCounts[analysis.fileType] = (fileTypeCounts[analysis.fileType] || 0) + 1;
      });
      
      const preferredType = Object.entries(fileTypeCounts)
        .sort(([,a], [,b]) => b - a)[0];
      
      insights.fileTypePreference = {
        type: preferredType[0],
        count: preferredType[1],
        percentage: Math.round((preferredType[1] / analyses.length) * 100)
      };

      // Common business domains
      const domainCounts = {};
      analyses.forEach(analysis => {
        if (analysis.analysisData?.businessDomain?.primaryDomain) {
          const domain = analysis.analysisData.businessDomain.primaryDomain;
          domainCounts[domain] = (domainCounts[domain] || 0) + 1;
        }
      });

      insights.commonDomains = Object.entries(domainCounts)
        .sort(([,a], [,b]) => b - a)
        .slice(0, 5)
        .map(([domain, count]) => ({ domain, count }));

      // Generate recommendations
      if (insights.fileTypePreference.percentage > 70) {
        insights.recommendations.push({
          type: 'diversification',
          message: `You primarily analyze ${insights.fileTypePreference.type} files. Consider exploring other file types for broader insights.`,
          priority: 'medium'
        });
      }

      if (analyses.length < 5) {
        insights.recommendations.push({
          type: 'experience',
          message: 'You\'re just getting started! Try analyzing different types of databases to build your expertise.',
          priority: 'high'
        });
      }

      // Learning path suggestions
      insights.learningPath = [
        'Start with simple databases to understand basic patterns',
        'Move to more complex relational databases',
        'Explore different business domains',
        'Analyze performance and optimization opportunities'
      ];
    }

    res.json({
      success: true,
      insights
    });

  } catch (error) {
    console.error('Dashboard insights error:', error);
    res.status(500).json({
      success: false,
      message: 'Internal server error while generating insights'
    });
  }
});

module.exports = router;
