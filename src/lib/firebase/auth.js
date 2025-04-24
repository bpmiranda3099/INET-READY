import { 
    getAuth, 
    createUserWithEmailAndPassword, 
    signInWithEmailAndPassword, 
    signOut, 
    onAuthStateChanged, 
    GoogleAuthProvider, 
    FacebookAuthProvider, 
    signInWithPopup, 
    sendPasswordResetEmail, 
    setPersistence, 
    browserLocalPersistence, 
    browserSessionPersistence, 
    sendEmailVerification,
    fetchSignInMethodsForEmail,
    linkWithCredential
} from "firebase/auth";
import app from './app';

// Initialize Firebase Auth
const auth = getAuth(app);

// Initialize Google Auth Provider
const googleProvider = new GoogleAuthProvider();
googleProvider.setCustomParameters({ prompt: 'select_account' });

// Initialize Facebook Auth Provider
const facebookProvider = new FacebookAuthProvider();

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
    if (error.code === 'auth/account-exists-with-different-credential') {
      try {
        // Get sign-in methods for this email
        const email = error.customData.email;
        const providers = await fetchSignInMethodsForEmail(auth, email);
        
        if (providers[0] === 'facebook.com') {
          // The user has a Facebook account with the same email
          // Sign in with Facebook to get credentials
          const facebookResult = await signInWithPopup(auth, facebookProvider);
          
          // Get Google credential
          const googleCredential = GoogleAuthProvider.credentialFromError(error);
          
          // Link Google credential to the Facebook account
          await linkWithCredential(facebookResult.user, googleCredential);
          return { user: facebookResult.user, error: null };
        }
        
        // Handle other providers if needed
        return { 
          user: null, 
          error: {
            code: 'auth/needs-linking',
            message: `This email is already associated with a ${providers[0]} account. Please sign in with ${providers[0]} first.`
          }
        };
      } catch (linkError) {
        console.error('Error during account linking:', linkError);
        return { user: null, error: linkError };
      }
    }
    return { user: null, error };
  }
};

// Sign in with Facebook
export const signInWithFacebook = async () => {
  try {
    const result = await signInWithPopup(auth, facebookProvider);
    return { user: result.user, error: null };
  } catch (error) {
    if (error.code === 'auth/account-exists-with-different-credential') {
      try {
        // Get sign-in methods for this email
        const email = error.customData.email;
        const providers = await fetchSignInMethodsForEmail(auth, email);
        
        if (providers[0] === 'google.com') {
          // The user has a Google account with the same email
          // Sign in with Google to get credentials
          const googleResult = await signInWithPopup(auth, googleProvider);
          
          // Get Facebook credential
          const facebookCredential = FacebookAuthProvider.credentialFromError(error);
          
          // Link Facebook credential to the Google account
          await linkWithCredential(googleResult.user, facebookCredential);
          return { user: googleResult.user, error: null };
        }
        
        // Handle other providers if needed
        return { 
          user: null, 
          error: {
            code: 'auth/needs-linking',
            message: `This email is already associated with a ${providers[0]} account. Please sign in with ${providers[0]} first.`
          }
        };
      } catch (linkError) {
        console.error('Error during account linking:', linkError);
        return { user: null, error: linkError };
      }
    }
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
