// Sync city-specific weather insights from Firestore to dashboard notification history
import { getFirestore, collection, query, where, orderBy, limit, getDocs } from 'firebase/firestore';
import { showNotification, getNotificationHistory } from './notification-service';
import app from '../firebase/app';

const db = getFirestore(app);

/**
 * Fetch recent city insights for the user's home city from Firestore and merge into dashboard notifications
 * @param {string} homeCity - The user's home city
 * @param {number} daysBack - How many days back to fetch insights (default: 3)
 */
export async function syncCityInsightsToDashboard(homeCity, daysBack = 3) {
  try {
    const today = new Date();
    const notificationHistory = getNotificationHistory();
    const existingMessages = new Set(notificationHistory.map(n => n.message));
    for (let i = 0; i < daysBack; i++) {
      const date = new Date(today);
      date.setDate(today.getDate() - i);
      const dateStr = date.toISOString().slice(0, 10);
      const insightRef = collection(db, 'weather_insights', dateStr, 'cities');
      const q = query(insightRef, where('__name__', '==', homeCity));
      const snapshot = await getDocs(q);
      snapshot.forEach(doc => {
        const data = doc.data();
        if (data.insight && !existingMessages.has(data.insight)) {
          showNotification(
            data.insight,
            'info',
            0,
            `Weather Insight for ${homeCity}`
          );
        }
      });
    }
  } catch (error) {
    console.error('Error syncing city insights to dashboard:', error);
  }
}
