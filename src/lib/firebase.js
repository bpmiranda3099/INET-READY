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
  sendPasswordReset,
  signInWithGoogle,
  sendVerificationEmail,
  isEmailVerified
} from './firebase/auth';
import medicalService, {
  hasMedicalRecord,
  saveMedicalData,
  updateMedicalData,
  getMedicalData
} from './firebase/medical';

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
  sendPasswordReset,
  signInWithGoogle,
  sendVerificationEmail,
  isEmailVerified,
  medicalService,
  hasMedicalRecord,
  saveMedicalData,
  updateMedicalData,
  getMedicalData
};
