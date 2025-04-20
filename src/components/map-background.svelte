<script>
  import { onMount, onDestroy } from 'svelte';
  import mapboxgl from 'mapbox-gl';
  export let center = [120.9842, 14.5995]; // Default: Manila (lon, lat)
  export let zoom = 15;
  export let pitch = 60;
  export let bearing = -20;
  export let style = 'mapbox://styles/mapbox/light-v11';

  let map;
  let mapContainer;
  
  // Fix: TypeScript compatibility for Vite env
  // Use a type declaration for import.meta.env if not present
  // @ts-ignore
  const MAPBOX_TOKEN = import.meta.env.VITE_MAPBOX_ACCESS_TOKEN;

  // Always ensure center is a valid {lng, lat} object
  function getSafeCenter(val) {
    if (Array.isArray(val) && val.length === 2) {
      const lng = Number(val[0]);
      const lat = Number(val[1]);
      if (!isNaN(lng) && !isNaN(lat)) {
        return { lng, lat };
      }
    }
    // fallback: Manila
    return { lng: 120.9842, lat: 14.5995 };
  }

  let initialCenter = getSafeCenter(center);

  onMount(() => {
    if (!MAPBOX_TOKEN) {
      console.error('Mapbox token missing');
      return;
    }
    mapboxgl.accessToken = MAPBOX_TOKEN;
    map = new mapboxgl.Map({
      container: mapContainer,
      style,
      center: initialCenter,
      zoom,
      pitch,
      bearing,
      interactive: false,
      antialias: true
    });
    map.on('load', () => {
      // 3D buildings layer
      map.addLayer({
        id: '3d-buildings',
        source: 'composite',
        'source-layer': 'building',
        filter: ['==', 'extrude', 'true'],
        type: 'fill-extrusion',
        minzoom: 20,
        paint: {
          'fill-extrusion-color': '#aaa',
          'fill-extrusion-height': ['get', 'height'],
          'fill-extrusion-base': ['get', 'min_height'],
          'fill-extrusion-opacity': 0.6
        }
      });
    });
    return () => {
      if (map) map.remove();
    };
  });

  // React to prop changes (center)
  $: if (map && Array.isArray(center) && center.length === 2) {
    const safe = getSafeCenter(center);
    map.jumpTo({ center: safe });
  }

  onDestroy(() => {
    if (map) map.remove();
  });
</script>

<style>
  .map-bg {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    z-index: 0;
    pointer-events: none; /* Prevents accidental interaction */
    filter: grayscale(0.2) brightness(0.97) contrast(1.05);
    /* Slightly dim for overlay readability */
    transition: filter 0.3s;
  }
  /* Remove unused selectors to fix Svelte compile errors */
  /* .mapboxgl-ctrl-logo, .mapboxgl-ctrl-attrib { display: none !important; } */
</style>

<div bind:this={mapContainer} class="map-bg"></div>
