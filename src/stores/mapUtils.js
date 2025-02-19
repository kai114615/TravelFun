import L from "leaflet";
import axios from "axios";

export default {
  map: null,
  async initializeMap(mapContainerId, center = [25.0330, 121.5654], zoom = 13) {
    // 初始化地圖
    this.map = L.map(mapContainerId).setView(center, zoom);
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    }).addTo(this.map);
  },
  async fetchLocations(apiUrl) {
    // 獲取景點數據
    try {
      const response = await axios.get(apiUrl);
      return response.data;
    } catch (error) {
      console.error("Failed to fetch locations:", error);
      throw error;
    }
  },
  addMarkers(locations) {
    // 添加標記到地圖
    if (!this.map) {
      console.error("Map is not initialized.");
      return;
    }
    locations.forEach((loc) => {
      L.marker([loc.latitude, loc.longitude])
        .addTo(this.map)
        .bindPopup(`<strong>${loc.name}</strong><br>${loc.description}`);
    });
  },
};