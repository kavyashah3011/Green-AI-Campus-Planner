const API_URL = "http://127.0.0.1:5000";

document.addEventListener("DOMContentLoaded", () => {
    loadCharts();
    initMap();
    loadRecs();
});

// --- GLOBAL CHARTS ---
function loadCharts() {
    fetch(`${API_URL}/solar`).then(res => res.json()).then(data => {
        if(data.length === 0) return;
        new Chart(document.getElementById("solarChart"), {
            type: "bar",
            data: {
                labels: data.map(d => d.building),
                datasets: [{
                    label: "Solar Potential (kWh)",
                    data: data.map(d => d.predicted_energy_kwh),
                    backgroundColor: "#f1c40f"
                }]
            },
            options: { responsive: true, maintainAspectRatio: false }
        });
    });

    fetch(`${API_URL}/carbon`).then(res => res.json()).then(data => {
        if(data.length === 0) return;
        new Chart(document.getElementById("carbonChart"), {
            type: "line",
            data: {
                labels: data.map(d => d.building),
                datasets: [{
                    label: "Carbon Saved (kg)",
                    data: data.map(d => d.carbon_saved_kg),
                    borderColor: "#2ecc71",
                    backgroundColor: "rgba(46, 204, 113, 0.1)",
                    fill: true
                }]
            },
            options: { responsive: true, maintainAspectRatio: false }
        });
    });
}

// --- RECOMMENDATIONS ---
function loadRecs() {
    fetch(`${API_URL}/recommendations`).then(res => res.json()).then(data => {
        const list = document.getElementById("rec-list");
        list.innerHTML = "";
        data.forEach(r => {
            const li = document.createElement("li");
            li.textContent = r;
            list.appendChild(li);
        });
    });
}

// --- MAP & SMART GRID ---
let map, drawnItems, gridLayer;

function initMap() {
    map = L.map('map').setView([23.078, 72.501], 18);
    
    L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
        attribution: 'Tiles &copy; Esri'
    }).addTo(map);

    drawnItems = new L.FeatureGroup();
    map.addLayer(drawnItems);
    gridLayer = L.layerGroup().addTo(map);

    const drawControl = new L.Control.Draw({
        draw: {
            polyline: false, marker: false, circlemarker: false, circle: false,
            polygon: { allowIntersection: false, showArea: true },
            rectangle: { showArea: true }
        },
        edit: { featureGroup: drawnItems, remove: true }
    });
    map.addControl(drawControl);

    map.on(L.Draw.Event.CREATED, function (e) {
        drawnItems.clearLayers();
        drawnItems.addLayer(e.layer);
        analyzeArea(e.layer.getBounds());
    });

    map.on(L.Draw.Event.DELETED, resetMap);
}

function analyzeArea(bounds) {
    document.getElementById("loader").style.display = "flex";
    
    fetch(`${API_URL}/analyze_region`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            lat_min: bounds.getSouthWest().lat,
            lat_max: bounds.getNorthEast().lat,
            lon_min: bounds.getSouthWest().lng,
            lon_max: bounds.getNorthEast().lng
        })
    })
    .then(res => res.json())
    .then(data => {
        renderGrid(data.grid_points);
        showStats(data.summary);
        document.getElementById("loader").style.display = "none";
    });
}

function renderGrid(points) {
    gridLayer.clearLayers();
    points.forEach(p => {
        let color = '#3498db';
        if(p.recommendation === 'SOLAR') color = '#f1c40f';
        if(p.recommendation === 'TREE') color = '#2ecc71';
        
        L.circleMarker([p.lat, p.lon], {
            color: color, fillColor: color, fillOpacity: 0.8, radius: 4, weight: 1
        }).addTo(gridLayer);
    });
}

function showStats(summary) {
    document.getElementById("analysis-panel").style.display = "block";
    document.getElementById("main-suggestion").textContent = summary.main_rec; // SHOWS MAIN SUGGESTION
    document.getElementById("zone-solar").textContent = summary.avg_solar;
    document.getElementById("zone-trees").textContent = summary.tree_count;
    document.getElementById("zone-score").textContent = summary.build_score;
}

function resetMap() {
    drawnItems.clearLayers();
    gridLayer.clearLayers();
    document.getElementById("analysis-panel").style.display = "none";
}