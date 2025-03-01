# Firebase Troubleshooting Guide

## Issue: "The database (default) does not exist" error when different Firebase apps work

If you're experiencing an error like this:

```
404 The database (default) does not exist for project inet-ready
```

...while other Firebase functionality (like your frontend authentication) is working correctly, you likely have a configuration mismatch between different parts of your application.

## Common Causes and Solutions

### 1. Different Firebase Projects

You might be using different Firebase projects for different parts of your application:

- Your frontend (medicalform.svelte) might be connected to one Firebase project
- Your backend or GitHub Actions might be connected to a different project

**Solution:** Ensure all components use the same Firebase project.

### 2. Firestore Database Not Created

Even when using the same project, you might have:

- Created Authentication
- Created Realtime Database
- But not created Firestore Database

**Solution:** Create the Firestore database in your Firebase Console:

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select your project (verify it's `inet-ready` from the error)
3. In the left sidebar, click "Firestore Database"
4. Click "Create database"
5. Choose "Start in production mode" or "Start in test mode"
6. Select a region close to your users
7. Click "Enable"

### 3. Service Account Permissions

Your service account might not have permission to access Firestore.

**Solution:** Check and update permissions:

1. Go to [Firebase Console](https://console.firebase.google.com/) > Project Settings > Service Accounts
2. Ensure your service account has at least "Firebase Admin SDK Administrator Service Agent" role
3. If needed, generate a new service account key and update your GitHub secret

### 4. Project ID Mismatch

The project ID in your service account file might not match the actual Firebase project.

**Solution:**

1. Verify the project ID in your service account JSON file
2. Check that it matches the project ID in the Firebase console URL (`https://console.firebase.google.com/project/inet-ready/`)
3. Update either the service account file or switch to the correct project

## Quick Verification Steps

1. Check which project your frontend is using:

   - In your frontend code, look for the Firebase initialization config
   - Note the `projectId` field

2. Check which project your GitHub Actions is using:

   - Print the project ID from the service account credentials
   - Add this code to your `hourly_heat_index_api.py` script, before initializing Firebase:

   ```python
   with open(service_account_path, 'r') as f:
       import json
       service_account = json.load(f)
       print(f"Using Firebase project: {service_account.get('project_id')}")
   ```

3. Make sure they match, and that you've created a Firestore database in that project
