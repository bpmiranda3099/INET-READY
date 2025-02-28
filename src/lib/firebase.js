// Main Firebase entry point that consolidates all Firebase services

import app from './firebase/app';
import analytics from './firebase/analytics';
import messaging, { requestFCMToken, onMessageListener } from './firebase/messaging';
import db, { testFirestoreConnection } from './firebase/firestore';
import auth, { 
  subscribeToAuthChanges, 
  registerWithEmailAndPassword, 
  loginWithEmailAndPassword, 
  logoutUser, 
  getCurrentUser,
  signInWithGoogle
} from './firebase/auth';

// Re-export everything
export {
  app,
  analytics,
  messaging,
  requestFCMToken,
  onMessageListener,
  db,
  testFirestoreConnection,
  auth,
  subscribeToAuthChanges,
  registerWithEmailAndPassword,
  loginWithEmailAndPassword,
  logoutUser,
  getCurrentUser,
  signInWithGoogle
};
