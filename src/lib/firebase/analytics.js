import { getAnalytics, isSupported } from "firebase/analytics";
import app from './app';

// Initialize analytics safely with browser check
let analytics = null;

// Only initialize analytics in the browser environment
const initializeAnalytics = async () => {
  if (typeof window !== "undefined") {
    try {
      // Check if analytics is supported in this environment
      const isAnalyticsSupported = await isSupported();
      if (isAnalyticsSupported) {
        analytics = getAnalytics(app);
        console.log("Firebase Analytics initialized");
      } else {
        console.log("Firebase Analytics is not supported in this environment");
      }
    } catch (error) {
      console.error("Error initializing Firebase Analytics:", error);
    }
  }
};

// Only try to initialize if in browser environment
if (typeof window !== "undefined") {
  initializeAnalytics();
}

export default analytics;
