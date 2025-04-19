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
  const res = await fetch(`${API_BASE}/store-medical-data`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify({ medicalData }),
  });
  if (!res.ok) throw new Error('Failed to save medical data');
  return await res.json().catch(() => ({}));
}

export async function updateMedicalData(partialData) {
  // For simplicity, use the same endpoint as save (API should handle upsert)
  return saveMedicalData(partialData);
}

export async function getMedicalData() {
  const token = await getIdToken();
  const res = await fetch(`${API_BASE}/get-medical-data`, {
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });
  if (!res.ok) throw new Error('Failed to fetch medical data');
  const data = await res.json();
  // If API returns an array, return the first record (as in the reference)
  if (Array.isArray(data)) return data[0]?.data || null;
  return data?.data || null;
}

export async function hasMedicalRecord() {
  try {
    const data = await getMedicalData();
    return !!data;
  } catch {
    return false;
  }
}
