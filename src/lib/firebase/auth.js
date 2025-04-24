import { 
    getAuth, 
    createUserWithEmailAndPassword, 
    signInWithEmailAndPassword, 
    signOut, 
    onAuthStateChanged, 
    GoogleAuthProvider, 
    FacebookAuthProvider, 
    signInWithPopup,
    signInWithRedirect,
    getRedirectResult,
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

// Check if device is mobile
const isMobileDevice = () => {
  return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(
    typeof navigator !== 'undefined' ? navigator.userAgent : ''
  );
};

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
    const user = result.user;
    
    // After successful Google sign in, check for other auth methods
    try {
      const email = user.email;
      const methods = await fetchSignInMethodsForEmail(auth, email);
      
      // Try to link Facebook if not already linked
      if (methods.includes('facebook.com') && !user.providerData.some(p => p.providerId === 'facebook.com')) {
        // Try to sign in with Facebook to get credential
        const fbResult = await signInWithPopup(auth, facebookProvider);
        if (fbResult.user) {
          // Get Facebook credential
          const fbCredential = FacebookAuthProvider.credentialFromResult(fbResult);
          if (fbCredential) {
            await linkWithCredential(user, fbCredential);
          }
        }
      }
    } catch (linkError) {
      console.error('Error attempting to link Facebook:', linkError);
      // Return warning but don't fail - user is still signed in with Google
      return { 
        user: result.user, 
        error: { 
          code: 'auth/link-warning',
          message: 'Successfully signed in with Google, but couldn\'t link Facebook account.' 
        }
      };
    }
    return { user: result.user, error: null };
  } catch (error) {
    if (error.code === 'auth/account-exists-with-different-credential') {
      try {
        // Get sign-in methods for this email
        const email = error.customData.email;
        const providers = await fetchSignInMethodsForEmail(auth, email);
        
        // Map provider IDs to friendly names
        const providerNames = {
          'google.com': 'Google',
          'facebook.com': 'Facebook',
          'password': 'Email/Password',
          'phone': 'Phone',
        };

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
        const providerName = providerNames[providers[0]] || 'your existing account';
        return { 
          user: null, 
          error: {
            code: 'auth/needs-linking',
            message: `This email is already associated with ${providerName}. Please sign in with ${providerName} first.`
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
    // Check if mobile device
    const isMobile = isMobileDevice();
    console.log('Device type:', isMobile ? 'mobile' : 'desktop');
    
    if (isMobile) {
      try {
        // Configure Facebook provider for mobile
        facebookProvider.setCustomParameters({
          // Force re-authentication
          auth_type: 'reauthenticate',
          // Specify display type
          display: 'touch'
        });
        
        console.log('Initiating Facebook redirect sign-in...');
        await signInWithRedirect(auth, facebookProvider);
        // We won't reach here - redirect happens
        return { user: null, error: null };
      } catch (redirectError) {
        console.error('Facebook redirect error:', {
          code: redirectError.code,
          message: redirectError.message,
          customData: redirectError.customData
        });
        return { user: null, error: redirectError };
      }
    }

    // Desktop flow
    console.log('Initiating Facebook popup sign-in...');
    const result = await signInWithPopup(auth, facebookProvider);
    const user = result.user;
    
    // After successful Facebook sign in, try to get Google credential if available
    try {
      const email = user.email;
      const methods = await fetchSignInMethodsForEmail(auth, email);
      
      // Try to link Google if not already linked
      if (methods.includes('google.com') && !user.providerData.some(p => p.providerId === 'google.com')) {
        // Try to sign in with Google to get credential
        const googleResult = await signInWithPopup(auth, googleProvider);
        if (googleResult.user) {
          // Get Google credential and link it
          const googleCredential = GoogleAuthProvider.credentialFromResult(googleResult);
          if (googleCredential) {
            await linkWithCredential(user, googleCredential);
          }
        }
      }
    } catch (linkError) {
      console.error('Error attempting to link Google:', linkError);
      // Return warning but don't fail - user is still signed in with Facebook
      return { 
        user: result.user, 
        error: { 
          code: 'auth/link-warning',
          message: 'Successfully signed in with Facebook, but couldn\'t link Google account.' 
        }
      };
    }
    return { user, error: null };
  } catch (error) {
    console.error('Facebook sign-in error:', {
      code: error.code,
      message: error.message,
      customData: error.customData
    });
    
    if (error.code === 'auth/account-exists-with-different-credential') {
      try {
        // Get sign-in methods for this email
        const email = error.customData.email;
        const methods = await fetchSignInMethodsForEmail(auth, email);
        
        // Map provider IDs to friendly names
        const providerNames = {
          'google.com': 'Google',
          'facebook.com': 'Facebook',
          'password': 'Email/Password',
          'phone': 'Phone',
          'microsoft.com': 'Microsoft',
          'apple.com': 'Apple'
        };

        if (methods[0] === 'google.com') {
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
        const providerName = providerNames[methods[0]] || 'your existing account';
        return { 
          user: null, 
          error: {
            code: 'auth/needs-linking',
            message: `This email is already associated with ${providerName}. Please sign in with ${providerName} first.`
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

// Handle redirect result
export const handleRedirectResult = async () => {
  try {
    console.log('Checking for redirect result...', {
      url: typeof window !== 'undefined' ? window.location.href : 'SSR',
      timestamp: new Date().toISOString()
    });

    const result = await getRedirectResult(auth);
    
    if (result) {
      console.log('Redirect result found:', {
        userId: result.user?.uid,
        providerId: result.providerId,
        operationType: result.operationType,
        email: result.user?.email,
        providerData: result.user?.providerData
      });

      // If we got here, the sign-in was successful
      if (result.user) {
        // Try to link with other providers if needed
        try {
          const email = result.user.email;
          const methods = await fetchSignInMethodsForEmail(auth, email);
          
          // Try to link Google if not already linked
          if (methods.includes('google.com') && !result.user.providerData.some(p => p.providerId === 'google.com')) {
            console.log('Attempting to link Google account after redirect...');
            const googleResult = await signInWithPopup(auth, googleProvider);
            if (googleResult.user) {
              const googleCredential = GoogleAuthProvider.credentialFromResult(googleResult);
              if (googleCredential) {
                await linkWithCredential(result.user, googleCredential);
                console.log('Successfully linked Google account');
              }
            }
          }
        } catch (linkError) {
          console.warn('Non-critical error linking accounts after redirect:', linkError);
          // Don't fail the sign-in, just return with a warning
          return {
            user: result.user,
            error: {
              code: 'auth/link-warning',
              message: 'Successfully signed in with Facebook, but couldn\'t link other accounts.'
            }
          };
        }
      }
      
      return { user: result.user, error: null };
    }
    
    console.log('No redirect result found');
    return { user: null, error: null };
  } catch (error) {
    console.error('Error handling redirect result:', {
      code: error.code,
      message: error.message,
      stack: error.stack,
      customData: error.customData
    });

    // Handle specific error cases
    if (error.code === 'auth/popup-closed-by-user') {
      return {
        user: null,
        error: {
          code: error.code,
          message: 'The sign in was cancelled. Please try again.'
        }
      };
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
