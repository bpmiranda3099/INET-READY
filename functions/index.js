const functions = require("firebase-functions");
const admin = require("firebase-admin");
admin.initializeApp();

const { subscribeToTopic, processNewFcmToken } = require('./topicManagement');
const { sendTestNotification } = require('./sendTestNotification');

// Topic management functions
exports.subscribeToTopic = subscribeToTopic;
exports.processNewFcmToken = processNewFcmToken;

// Test notification function
exports.sendTestNotification = sendTestNotification;
