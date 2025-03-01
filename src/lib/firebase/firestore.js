import { getFirestore, doc, getDoc, setDoc, updateDoc, serverTimestamp, collection, query, where, orderBy, limit, getDocs } from 'firebase/firestore';
import app from './app';

// Initialize Firestore
const db = getFirestore(app);

// Test connection to Firestore
export const testFirestoreConnection = async () => {
  try {
    const testDoc = doc(db, 'test', 'connection');
    await setDoc(testDoc, { timestamp: serverTimestamp() }, { merge: true });
    return true;
  } catch (error) {
    console.error('Firestore connection test failed:', error);
    return false;
  }
};

// Track verification email attempts to implement rate limiting
export const trackVerificationAttempt = async (userId) => {
  try {
    const userRef = doc(db, 'users', userId);
    const userDoc = await getDoc(userRef);
    
    if (!userDoc.exists()) {
      // Create user document if it doesn't exist
      await setDoc(userRef, {
        verificationAttempts: [{
          timestamp: serverTimestamp()
        }],
        createdAt: serverTimestamp()
      });
    } else {
      // Update existing user document
      const userData = userDoc.data();
      const verificationAttempts = userData.verificationAttempts || [];
      
      // Add new attempt
      await updateDoc(userRef, {
        verificationAttempts: [
          ...verificationAttempts,
          { timestamp: serverTimestamp() }
        ]
      });
    }
    
    return true;
  } catch (error) {
    console.error('Error tracking verification attempt:', error);
    return false;
  }
};

// Check if user is rate limited for verification emails
export const isRateLimited = async (userId) => {
  try {
    const userRef = doc(db, 'users', userId);
    const userDoc = await getDoc(userRef);
    
    if (!userDoc.exists()) {
      return false;
    }
    
    const userData = userDoc.data();
    const verificationAttempts = userData.verificationAttempts || [];
    
    // No attempts yet
    if (verificationAttempts.length === 0) {
      return false;
    }
    
    // Check for more than 5 attempts in the last hour
    const oneHourAgo = new Date();
    oneHourAgo.setHours(oneHourAgo.getHours() - 1);
    
    const recentAttempts = verificationAttempts.filter(attempt => {
      const attemptTime = attempt.timestamp?.toDate();
      return attemptTime && attemptTime > oneHourAgo;
    });
    
    return recentAttempts.length >= 5;
  } catch (error) {
    console.error('Error checking rate limit:', error);
    return false;
  }
};

export default db;
