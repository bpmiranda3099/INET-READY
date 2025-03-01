import { getFirestore, doc, setDoc, getDoc, updateDoc } from "firebase/firestore";
import app from './app';

// Initialize Firestore
const db = getFirestore(app);

// Helper to check if user has submitted medical form
export const hasMedicalRecord = async (userId) => {
  if (!userId) return false;
  
  try {
    const docRef = doc(db, "medical_records", userId);
    const docSnap = await getDoc(docRef);
    return docSnap.exists();
  } catch (error) {
    console.error("Error checking medical record:", error);
    return false;
  }
};

// Save medical data for a user
export const saveMedicalData = async (userId, medicalData) => {
  if (!userId) return { success: false, error: "User ID is required" };
  
  try {
    const docRef = doc(db, "medical_records", userId);
    await setDoc(docRef, {
      ...medicalData,
      updatedAt: new Date().toISOString(),
      userId
    });
    
    return { success: true, error: null };
  } catch (error) {
    console.error("Error saving medical data:", error);
    return { success: false, error: error.message };
  }
};

// Update partial medical data for a user
export const updateMedicalData = async (userId, partialData) => {
  if (!userId) return { success: false, error: "User ID is required" };
  
  try {
    const docRef = doc(db, "medical_records", userId);
    await updateDoc(docRef, {
      ...partialData,
      updatedAt: new Date().toISOString()
    });
    
    return { success: true, error: null };
  } catch (error) {
    console.error("Error updating medical data:", error);
    return { success: false, error: error.message };
  }
};

// Get medical data for a user
export const getMedicalData = async (userId) => {
  if (!userId) return { data: null, error: "User ID is required" };
  
  try {
    const docRef = doc(db, "medical_records", userId);
    const docSnap = await getDoc(docRef);
    
    if (docSnap.exists()) {
      return { data: docSnap.data(), error: null };
    } else {
      return { data: null, error: "No medical record found" };
    }
  } catch (error) {
    console.error("Error getting medical data:", error);
    return { data: null, error: error.message };
  }
};

export default {
  hasMedicalRecord,
  saveMedicalData,
  updateMedicalData,
  getMedicalData
};
