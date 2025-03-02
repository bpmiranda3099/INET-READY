const functions = require("firebase-functions");
const admin = require("firebase-admin");

/**
 * Cloud Function to send a test notification to a specific token
 * Useful for debugging notification issues
 */
exports.sendTestNotification = functions.https.onCall(async (data, context) => {
  try {
    // Validate parameters
    if (!data.token) {
      throw new functions.https.HttpsError(
        "invalid-argument",
        "Token is required"
      );
    }

    // Customize notification content
    const notificationTitle = data.title || "Test Notification";
    const notificationBody = data.body || "This is a test notification from the server";
    const timestamp = new Date().toISOString();
    
    // Create the notification message
    const message = {
      token: data.token,
      notification: {
        title: notificationTitle,
        body: notificationBody,
      },
      webpush: {
        headers: {
          Urgency: "high",
          TTL: "300" // 5 minutes
        },
        notification: {
          title: notificationTitle,
          body: notificationBody,
          icon: "/app-icon.png",
          badge: "/favicon.png",
          requireInteraction: true,
          timestamp: Date.now(),
          tag: `test-${Date.now()}`
        },
        fcmOptions: {
          link: "/app/test-notification"
        }
      },
      data: {
        timestamp: timestamp,
        type: "test",
        url: "/app/test-notification",
        click_action: "/app/test-notification"
      }
    };

    // Send the message
    const response = await admin.messaging().send(message);
    
    return {
      success: true,
      messageId: response,
      timestamp: timestamp
    };
  } catch (error) {
    console.error("Error sending test notification:", error);
    throw new functions.https.HttpsError(
      "internal",
      "Failed to send test notification",
      error
    );
  }
});
