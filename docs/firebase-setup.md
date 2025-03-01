# Firebase Firestore Setup Guide

This guide explains how to set up Firebase Firestore for the hourly_heat_index application.

## Initial Setup

1. Go to the [Firebase Console](https://console.firebase.google.com/)
2. Select your project (or create a new one)
3. In the left sidebar, click on "Firestore Database"
4. Click "Create database"
5. Choose "Start in production mode" (recommended for most cases)
6. Select a location for your database that's closest to your users
7. Click "Enable"

## Verify Project ID

Make sure the project ID in your service account credentials matches your actual Firebase project ID:

1. Open your service account JSON file
2. Check the value of the `project_id` field
3. Verify this matches the project ID in your Firebase console URL (e.g., `https://console.firebase.google.com/project/YOUR-PROJECT-ID`)

## Security Rules

For testing, you can use the default security rules. For production, consider setting appropriate security rules:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /latest_hourly_heat_index/{document=**} {
      // Allow read access to all users
      allow read: if true;

      // Allow write access only to authenticated service accounts
      allow write: if request.auth != null && request.auth.token.email.endsWith('@your-project-id.iam.gserviceaccount.com');
    }
  }
}
```

## Troubleshooting

If you see an error like:

```
404 The database (default) does not exist for project your-project-id
```

This means you need to create the Firestore database following the steps above.
