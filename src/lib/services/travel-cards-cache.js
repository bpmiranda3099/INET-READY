export const TRAVEL_CARDS_CACHE_KEY = 'inet-ready-travel-cards-cache-v1';
export const TRAVEL_CARDS_STATE_CACHE_KEY = 'inet-ready-travel-cards-state-cache-v1';

export function saveTravelCardsCache({ cards, cardIndex, mapState }) {
    // Only cache non-sensitive fields!
    const safeCards = cards.map(card => ({
        fromCity: card.fromCity,
        toCity: card.toCity,
        advice: card.rowOne?.inetReady?.advice || '',
        status: card.rowOne?.inetReady?.status || '',
        timestamp: card.timestamp,
        pois: card.rowThree?.tiles?.[0]?.pois?.map(poi => ({
            title: poi.title,
            address: poi.address,
            lat: poi.lat,
            lng: poi.lng
        })) || [],
        hospital: card.rowThree?.tiles?.[1]?.hospitalPOI ? {
            title: card.rowThree.tiles[1].hospitalPOI.title,
            address: card.rowThree.tiles[1].hospitalPOI.address,
            phone: card.rowThree.tiles[1].hospitalPOI.phone
        } : null
    }));
    localStorage.setItem(TRAVEL_CARDS_CACHE_KEY, JSON.stringify(safeCards));
    localStorage.setItem(TRAVEL_CARDS_STATE_CACHE_KEY, JSON.stringify({ cardIndex, mapState }));
}

export function loadTravelCardsCache() {
    try {
        const cardsRaw = localStorage.getItem(TRAVEL_CARDS_CACHE_KEY);
        const stateRaw = localStorage.getItem(TRAVEL_CARDS_STATE_CACHE_KEY);
        if (!cardsRaw) return null;
        return {
            cards: JSON.parse(cardsRaw),
            state: stateRaw ? JSON.parse(stateRaw) : {}
        };
    } catch {
        return null;
    }
}

export function clearTravelCardsCache() {
    localStorage.removeItem(TRAVEL_CARDS_CACHE_KEY);
    localStorage.removeItem(TRAVEL_CARDS_STATE_CACHE_KEY);
}
