const API_URL = "http://127.0.0.1:5000";

let solarChartInstance = null;
let carbonChartInstance = null;

document.addEventListener("DOMContentLoaded", () => {
  loadSolarChart();
  loadCarbonChart();
  loadMapAndGreenZones();
  loadRecommendations();
});

// ---------------- SOLAR CHART ----------------
function loadSolarChart() {
  fetch(`${API_URL}/solar`)
    .then(res => res.json())
    .then(data => {
      if (!data || data.length === 0) {
        console.error("No solar data received");
        return;
      }

      const ctx = document.getElementById("solarChart");
      if (!ctx) return;

      if (solarChartInstance) solarChartInstance.destroy();

      solarChartInstance = new Chart(ctx, {
        type: "bar",
        data: {
          labels: data.map(d => d.building),
          datasets: [{
            label: "Predicted Solar Energy (kWh)",
            data: data.map(d => Number(d.predicted_energy_kwh)),
            backgroundColor: "#f1c40f"
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false
        }
      });
    })
    .catch(err => console.error("Solar chart error:", err));
}

// ---------------- CARBON CHART ----------------
function loadCarbonChart() {
  fetch(`${API_URL}/carbon`)
    .then(res => res.json())
    .then(data => {
      if (!data || data.length === 0) {
        console.error("No carbon data received");
        return;
      }

      const ctx = document.getElementById("carbonChart");
      if (!ctx) return;

      if (carbonChartInstance) carbonChartInstance.destroy();

      carbonChartInstance = new Chart(ctx, {
        type: "bar",
        data: {
          labels: data.map(d => d.building),
          datasets: [{
            label: "Carbon Reduction (kg CO₂)",
            data: data.map(d => Number(d.carbon_saved_kg)),
            backgroundColor: "#2ecc71"
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false
        }
      });
    })
    .catch(err => console.error("Carbon chart error:", err));
}

// ---------------- MAP + GREEN ZONES ----------------
function loadMapAndGreenZones() {
  const map = L.map("map").setView([23.0225, 72.5714], 18);

  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png").addTo(map);

  fetch(`${API_URL}/solar`)
    .then(res => res.json())
    .then(data => {
      data.forEach(b => {
        if (b.lat && b.lon) {
          L.marker([b.lat, b.lon])
            .addTo(map)
            .bindPopup(`${b.building}<br>Solar: ${b.predicted_energy_kwh} kWh`);
        }
      });
    });

  fetch(`${API_URL}/green-zones`)
    .then(res => res.json())
    .then(zones => {
      zones.forEach(z => {
        L.circleMarker([z.latitude, z.longitude], {
          radius: 8,
          color: "green",
          fillOpacity: 0.6
        }).addTo(map);
      });
    });
}

// ---------------- RECOMMENDATIONS ----------------
function loadRecommendations() {
  fetch(`${API_URL}/recommendations`)
    .then(res => res.json())
    .then(data => {
      const list = document.getElementById("recommendations");
      list.innerHTML = "";
      data.forEach(rec => {
        const li = document.createElement("li");
        li.textContent = rec;
        list.appendChild(li);
      });
    });
}
