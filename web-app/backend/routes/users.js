const express = require('express');
const { body, validationResult } = require('express-validator');
const User = require('../models/User');
const Analysis = require('../models/Analysis');
const { authMiddleware } = require('../middleware/auth');

const router = express.Router();

// @route   GET /api/users/profile
// @desc    Get user profile
// @access  Private
router.get('/profile', authMiddleware, async (req, res) => {
  try {
    const user = await User.findById(req.user._id);
    
    res.json({
      success: true,
      user: {
        id: user._id,
        username: user.username,
        email: user.email,
        firstName: user.firstName,
        lastName: user.lastName,
        role: user.role,
        analysisCount: user.analysisCount,
        totalAnalysisTime: user.totalAnalysisTime,
        preferences: user.preferences,
        lastLogin: user.lastLogin,
        createdAt: user.createdAt
      }
    });

  } catch (error) {
    console.error('Get profile error:', error);
    res.status(500).json({
      success: false,
      message: 'Internal server error while fetching profile'
    });
  }
});

// @route   PUT /api/users/profile
// @desc    Update user profile
// @access  Private
router.put('/profile', [
  authMiddleware,
  body('firstName')
    .optional()
    .trim()
    .isLength({ min: 1, max: 50 })
    .withMessage('First name must be between 1 and 50 characters'),
  body('lastName')
    .optional()
    .trim()
    .isLength({ min: 1, max: 50 })
    .withMessage('Last name must be between 1 and 50 characters'),
  body('preferences.theme')
    .optional()
    .isIn(['light', 'dark', 'auto'])
    .withMessage('Theme must be light, dark, or auto'),
  body('preferences.notifications.email')
    .optional()
    .isBoolean()
    .withMessage('Email notifications must be a boolean'),
  body('preferences.notifications.push')
    .optional()
    .isBoolean()
    .withMessage('Push notifications must be a boolean')
], async (req, res) => {
  try {
    // Check for validation errors
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        success: false,
        errors: errors.array()
      });
    }

    const { firstName, lastName, preferences } = req.body;
    const updateFields = {};

    if (firstName !== undefined) updateFields.firstName = firstName;
    if (lastName !== undefined) updateFields.lastName = lastName;
    if (preferences) {
      updateFields.preferences = { ...req.user.preferences, ...preferences };
    }

    const user = await User.findByIdAndUpdate(
      req.user._id,
      updateFields,
      { new: true, runValidators: true }
    );

    res.json({
      success: true,
      message: 'Profile updated successfully',
      user: {
        id: user._id,
        username: user.username,
        email: user.email,
        firstName: user.firstName,
        lastName: user.lastName,
        role: user.role,
        analysisCount: user.analysisCount,
        totalAnalysisTime: user.totalAnalysisTime,
        preferences: user.preferences
      }
    });

  } catch (error) {
    console.error('Update profile error:', error);
    res.status(500).json({
      success: false,
      message: 'Internal server error while updating profile'
    });
  }
});

// @route   POST /api/users/change-password
// @desc    Change user password
// @access  Private
router.post('/change-password', [
  authMiddleware,
  body('currentPassword')
    .exists()
    .withMessage('Current password is required'),
  body('newPassword')
    .isLength({ min: 6 })
    .withMessage('New password must be at least 6 characters long')
], async (req, res) => {
  try {
    // Check for validation errors
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        success: false,
        errors: errors.array()
      });
    }

    const { currentPassword, newPassword } = req.body;

    // Get user with password
    const user = await User.findById(req.user._id).select('+password');

    // Verify current password
    const isMatch = await user.comparePassword(currentPassword);
    if (!isMatch) {
      return res.status(400).json({
        success: false,
        message: 'Current password is incorrect'
      });
    }

    // Update password
    user.password = newPassword;
    await user.save();

    res.json({
      success: true,
      message: 'Password changed successfully'
    });

  } catch (error) {
    console.error('Change password error:', error);
    res.status(500).json({
      success: false,
      message: 'Internal server error while changing password'
    });
  }
});

// @route   GET /api/users/analyses
// @desc    Get user's analyses with pagination and filters
// @access  Private
router.get('/analyses', authMiddleware, async (req, res) => {
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
    console.error('Get user analyses error:', error);
    res.status(500).json({
      success: false,
      message: 'Internal server error while fetching analyses'
    });
  }
});

// @route   GET /api/users/stats
// @desc    Get user statistics
// @access  Private
router.get('/stats', authMiddleware, async (req, res) => {
  try {
    const userId = req.user._id;

    // Get basic stats
    const totalAnalyses = await Analysis.countDocuments({ user: userId });
    const completedAnalyses = await Analysis.countDocuments({ 
      user: userId, 
      status: 'completed' 
    });
    const totalProcessingTime = await Analysis.aggregate([
      { $match: { user: userId, status: 'completed', processingTime: { $gt: 0 } } },
      { $group: { _id: null, total: { $sum: '$processingTime' } } }
    ]);

    // Get file type distribution
    const fileTypeStats = await Analysis.aggregate([
      { $match: { user: userId } },
      { $group: { _id: '$fileType', count: { $sum: 1 } } },
      { $sort: { count: -1 } }
    ]);

    // Get business domain distribution
    const domainStats = await Analysis.aggregate([
      { $match: { user: userId, status: 'completed' } },
      { $group: { _id: '$analysisData.businessDomain.primaryDomain', count: { $sum: 1 } } },
      { $sort: { count: -1 } }
    ]);

    // Get monthly activity
    const monthlyActivity = await Analysis.aggregate([
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

    // Get recent activity
    const recentActivity = await Analysis.find({ user: userId })
      .sort({ createdAt: -1 })
      .limit(10)
      .select('originalName status createdAt fileType processingTime');

    res.json({
      success: true,
      stats: {
        totalAnalyses,
        completedAnalyses,
        successRate: totalAnalyses > 0 ? Math.round((completedAnalyses / totalAnalyses) * 100) : 0,
        totalProcessingTime: totalProcessingTime[0]?.total || 0,
        averageProcessingTime: completedAnalyses > 0 ? Math.round((totalProcessingTime[0]?.total || 0) / completedAnalyses) : 0,
        fileTypeDistribution: fileTypeStats,
        domainDistribution: domainStats,
        monthlyActivity,
        recentActivity
      }
    });

  } catch (error) {
    console.error('Get user stats error:', error);
    res.status(500).json({
      success: false,
      message: 'Internal server error while fetching user statistics'
    });
  }
});

// @route   DELETE /api/users/account
// @desc    Delete user account and all associated data
// @access  Private
router.delete('/account', [
  authMiddleware,
  body('password')
    .exists()
    .withMessage('Password is required for account deletion')
], async (req, res) => {
  try {
    // Check for validation errors
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        success: false,
        errors: errors.array()
      });
    }

    const { password } = req.body;

    // Get user with password
    const user = await User.findById(req.user._id).select('+password');

    // Verify password
    const isMatch = await user.comparePassword(password);
    if (!isMatch) {
      return res.status(400).json({
        success: false,
        message: 'Password is incorrect'
      });
    }

    // Delete all user's analyses and associated files
    const analyses = await Analysis.find({ user: req.user._id });
    
    for (const analysis of analyses) {
      // Remove uploaded file
      if (analysis.filePath && await require('fs-extra').pathExists(analysis.filePath)) {
        await require('fs-extra').remove(analysis.filePath);
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
          if (await require('fs-extra').pathExists(file)) {
            await require('fs-extra').remove(file);
          }
        }
      }
    }

    // Delete all analyses
    await Analysis.deleteMany({ user: req.user._id });

    // Delete user account
    await User.findByIdAndDelete(req.user._id);

    res.json({
      success: true,
      message: 'Account deleted successfully. All data has been removed.'
    });

  } catch (error) {
    console.error('Delete account error:', error);
    res.status(500).json({
      success: false,
      message: 'Internal server error while deleting account'
    });
  }
});

// @route   GET /api/users/search
// @desc    Search for users (admin only)
// @access  Private (Admin)
router.get('/search', authMiddleware, async (req, res) => {
  try {
    // Check if user is admin
    if (req.user.role !== 'admin') {
      return res.status(403).json({
        success: false,
        message: 'Access denied. Admin privileges required.'
      });
    }

    const { q, page = 1, limit = 10 } = req.query;

    const query = {};
    if (q) {
      query.$or = [
        { username: { $regex: q, $options: 'i' } },
        { email: { $regex: q, $options: 'i' } },
        { firstName: { $regex: q, $options: 'i' } },
        { lastName: { $regex: q, $options: 'i' } }
      ];
    }

    const options = {
      page: parseInt(page),
      limit: parseInt(limit),
      select: '-password',
      sort: { createdAt: -1 }
    };

    const users = await User.paginate(query, options);

    res.json({
      success: true,
      users: users.docs,
      pagination: {
        page: users.page,
        limit: users.limit,
        totalPages: users.totalPages,
        totalDocs: users.totalDocs,
        hasNextPage: users.hasNextPage,
        hasPrevPage: users.hasPrevPage
      }
    });

  } catch (error) {
    console.error('Search users error:', error);
    res.status(500).json({
      success: false,
      message: 'Internal server error while searching users'
    });
  }
});

module.exports = router;
