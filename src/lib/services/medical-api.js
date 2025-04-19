// src/lib/services/medical-api.js
// API client for medical data via Aptible-hosted Express/Postgres backend

const API_BASE = 'https://app-91403.on-aptible.com'; // Ensure the URL includes the https:// prefix

async function getIdToken() {
  // Use Firebase Auth to get the current user's ID token
  const { getAuth } = await import('firebase/auth');
  const user = getAuth().currentUser;
  if (!user) throw new Error('Not authenticated');
  return user.getIdToken();
}

export async function saveMedicalData(medicalData) {
  const token = await getIdToken();
  console.log('Token:', token);
  console.log('[saveMedicalData] Sending request to save medical data:', medicalData);
  const res = await fetch(`${API_BASE}/store-medical-data`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify({ medicalData }),
  });
  console.log('[saveMedicalData] Response status:', res.status);
  if (!res.ok) throw new Error('Failed to save medical data');
  const responseData = await res.json().catch(() => ({}));
  console.log('[saveMedicalData] Response data:', responseData);
  return responseData;
}

export async function updateMedicalData(partialData) {
  console.log('[updateMedicalData] Updating medical data with partial data:', partialData);
  return saveMedicalData(partialData);
}

export async function getMedicalData() {
  const token = await getIdToken();
  console.log('[getMedicalData] Sending request to fetch medical data');
  const res = await fetch(`${API_BASE}/get-medical-data`, {
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });
  console.log('[getMedicalData] Response status:', res.status);
  if (!res.ok) throw new Error('Failed to fetch medical data');
  const data = await res.json();
  console.log('[getMedicalData] Response data:', data);
  if (Array.isArray(data)) return data[0]?.data || null;
  return data?.data || null;
}

export async function hasMedicalRecord() {
  console.log('[hasMedicalRecord] Checking if medical record exists');
  try {
    const data = await getMedicalData();
    console.log('[hasMedicalRecord] Medical record exists:', !!data);
    return !!data;
  } catch (error) {
    console.error('[hasMedicalRecord] Error checking medical record:', error);
    return false;
  }
}
