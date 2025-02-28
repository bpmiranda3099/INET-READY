import { getFirestore, collection, getDocs, query, limit } from "firebase/firestore";
import app from './app';

// Initialize Firestore
const db = getFirestore(app);

// Function to test Firestore connection
export const testFirestoreConnection = async () => {
  try {
    if (!db) {
      console.log("Firestore: Not initialized");
      return false;
    }
    
    // Try to get a document from any collection
    const testCollection = collection(db, "test_connection");
    const q = query(testCollection, limit(1));
    const snapshot = await getDocs(q);
    
    console.log("Firestore: Successfully connected");
    return true;
  } catch (error) {
    console.error("Firestore connection test failed:", error);
    return false;
  }
};

export default db;
