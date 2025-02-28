import { getAnalytics, isSupported } from "firebase/analytics";
import app from './app';

let analytics = null;

// Initialize Analytics only if in browser and supported
if (typeof window !== "undefined") {
  isSupported()
    .then((supported) => {
      if (supported) {
        analytics = getAnalytics(app);
      }
    })
    .catch(console.error);
}

export default analytics;
