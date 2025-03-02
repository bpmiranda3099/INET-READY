const functions = require("firebase-functions");
const admin = require("firebase-admin");
admin.initializeApp();

/**
 * Cloud Function to subscribe a device token to an FCM topic
 * This requires server authentication and can't be done directly from the frontend
 */
exports.subscribeToTopic = functions.https.onCall(async (data, context) => {
  try {
    // Validate parameters
    if (!data.token || !data.topic) {
      throw new functions.https.HttpsError(
        "invalid-argument",
        "Token and topic are required"
      );
    }

    // Require authentication if not in development
    if (!context.auth && process.env.NODE_ENV !== "development") {
      throw new functions.https.HttpsError(
        "unauthenticated",
        "Authentication required"
      );
    }

    // Subscribe the token to the topic
    await admin.messaging().subscribeToTopic(data.token, data.topic);

    // Update the user document if authenticated
    if (context.auth) {
      const userId = context.auth.uid;
      const db = admin.firestore();
      
      // Get current user data
      const userRef = db.collection("users").doc(userId);
      const userDoc = await userRef.get();
      
      // Update the topic subscriptions
      if (userDoc.exists) {
        const userData = userDoc.data();
        const subscriptions = userData.topicSubscriptions || [];
        
        // Only add if not already subscribed
        if (!subscriptions.includes(data.topic)) {
          await userRef.update({
            topicSubscriptions: [...subscriptions, data.topic],
          });
        }
      }
    }

    return { success: true, message: "Successfully subscribed to topic" };
  } catch (error) {
    console.error("Error subscribing to topic:", error);
    throw new functions.https.HttpsError(
      "internal",
      "Failed to subscribe to topic",
      error
    );
  }
});

/**
 * Cloud Function to update user FCM token
 * This is triggered when a new token is written to fcm_tokens collection
 */
exports.processNewFcmToken = functions.firestore
  .document("fcm_tokens/{tokenId}")
  .onCreate(async (snapshot, context) => {
    try {
      const tokenData = snapshot.data();
      
      if (!tokenData.token || !tokenData.userId) {
        console.log("Invalid token data:", tokenData);
        return null;
      }
      
      // Subscribe the token to default topics
      const defaultTopics = ["daily_weather_insights", "emergency_alerts"];
      
      // Subscribe to each topic
      for (const topic of defaultTopics) {
        try {
          await admin.messaging().subscribeToTopic(tokenData.token, topic);
          console.log(`Subscribed token to topic: ${topic}`);
        } catch (error) {
          console.error(`Error subscribing to topic ${topic}:`, error);
        }
      }
      
      // Update the token document with subscribed topics
      await snapshot.ref.update({
        subscribedTopics: defaultTopics,
        updatedAt: admin.firestore.FieldValue.serverTimestamp()
      });
      
      return null;
    } catch (error) {
      console.error("Error processing new FCM token:", error);
      return null;
    }
  });
