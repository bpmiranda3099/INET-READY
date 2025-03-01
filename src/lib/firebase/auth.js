import { getAuth, createUserWithEmailAndPassword, signInWithEmailAndPassword, signOut, onAuthStateChanged, GoogleAuthProvider, signInWithPopup, sendPasswordResetEmail, setPersistence, browserLocalPersistence, browserSessionPersistence, sendEmailVerification } from "firebase/auth";
import app from './app';

// Initialize Firebase Auth
const auth = getAuth(app);

// Initialize Google Auth Provider
const googleProvider = new GoogleAuthProvider();
googleProvider.setCustomParameters({ prompt: 'select_account' });

// Auth state observer
export const subscribeToAuthChanges = (callback) => {
  if (typeof window !== "undefined") {
    return onAuthStateChanged(auth, callback);
  }
  return () => {};
};

// Sign up with email/password
export const registerWithEmailAndPassword = async (email, password) => {
  try {
    const userCredential = await createUserWithEmailAndPassword(auth, email, password);
    
    // Send verification email
    await sendEmailVerification(userCredential.user);
    
    return { user: userCredential.user, error: null };
  } catch (error) {
    return { user: null, error };
  }
};

// Send email verification
export const sendVerificationEmail = async (user) => {
  try {
    await sendEmailVerification(user);
    return { success: true, error: null };
  } catch (error) {
    return { success: false, error };
  }
};

// Sign in with email/password
export const loginWithEmailAndPassword = async (email, password, rememberMe = false) => {
  try {
    // Set persistence based on remember me option
    const persistenceType = rememberMe ? browserLocalPersistence : browserSessionPersistence;
    await setPersistence(auth, persistenceType);

    const userCredential = await signInWithEmailAndPassword(auth, email, password);
    return { user: userCredential.user, error: null };
  } catch (error) {
    return { user: null, error };
  }
};

// Sign in with Google
export const signInWithGoogle = async () => {
  try {
    const result = await signInWithPopup(auth, googleProvider);
    return { user: result.user, error: null };
  } catch (error) {
    return { user: null, error };
  }
};

// Send password reset email
export const sendPasswordReset = async (email) => {
  try {
    await sendPasswordResetEmail(auth, email);
    return { success: true, error: null };
  } catch (error) {
    return { success: false, error };
  }
};

// Sign out
export const logoutUser = async () => {
  try {
    await signOut(auth);
    return { success: true, error: null };
  } catch (error) {
    return { success: false, error };
  }
};

// Get current user
export const getCurrentUser = () => {
  return auth.currentUser;
};

// Check if email is verified
export const isEmailVerified = (user) => {
  return user && user.emailVerified;
};

export default auth;
