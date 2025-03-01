# Firebase Security Rules

Below are the recommended security rules for this application. These rules maintain any existing collection rules while adding proper security for the weather data collection.

```javascript
rules_version = '2';

service cloud.firestore {
  match /databases/{database}/documents {
    // Make sure users can only access their own medical records
    match /medical_records/{userId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }

    // Basic test collection for connection testing
    match /test_connection/{document=**} {
      allow read: if request.auth != null;
      allow write: if false;
    }

    // Weather data collection - allow public reads but restrict writes
    match /latest_hourly_heat_index/{document=**} {
      // Anyone can read the weather data
      allow read: if true;

      // Only authenticated service accounts can write
      // You'll need to replace "your-project-id" with your actual Firebase project ID
      allow write: if request.auth != null &&
                     (request.auth.token.email.endsWith('@your-project-id.iam.gserviceaccount.com') ||
                      request.auth.token.email.endsWith('@inet-ready.iam.gserviceaccount.com'));
    }

    // Default rule - deny all access unless specifically allowed above
    match /{document=**} {
      allow read, write: if false;
    }
  }
}
```

## Important Note

Your current default rule (`allow read, write: if true;`) allows unrestricted access to ALL collections not explicitly covered by other rules. This is a security risk and should be changed to the more restrictive default rule shown above (`allow read, write: if false;`).

## How to Update Rules

1. Go to the [Firebase Console](https://console.firebase.google.com/)
2. Select your project
3. Click on "Firestore Database" in the left sidebar
4. Click on the "Rules" tab
5. Replace the current rules with the ones above
6. Click "Publish"

Make sure to replace `your-project-id` with your actual Firebase project ID before publishing.
