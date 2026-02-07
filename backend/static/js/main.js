// Map Initialization
const map = L.map('map').setView([13.0827, 80.2707], 12);

L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; OpenStreetMap',
    maxZoom: 20
}).addTo(map);

let geoJsonLayer = null;
let itParkBoundaryLayer = null;
let itParkCirclesLayer = null;

const els = {
    feature: document.getElementById('featureSelect'),
    yearSlider: document.getElementById('yearSlider'),
    yearDisplay: document.getElementById('yearDisplay'),
    scenarioToggle: document.getElementById('scenarioToggle'),
    loading: document.getElementById('loadingIndicator'),
    status: document.getElementById('statusMessage'),
    legendContent: document.getElementById('legendContent'),
    aiPanel: document.getElementById('aiPanel'),
    aiMetrics: document.getElementById('aiMetrics'),
    aiSeverity: document.getElementById('aiSeverity'),
    aiRecommendations: document.getElementById('aiRecommendations'),
    closeAiPanel: document.getElementById('closeAiPanel')
};

let state = {
    year: 2025,
    scenario: 'Before',
    feature: 'heat_risk_index'
};

const PALETTE = {
    q20: "#2ECC71",
    q40: "#F1C40F",
    q60: "#E67E22",
    q80: "#E74C3C",
    q100: "#7B241C"
};

els.feature.addEventListener('change', (e) => { state.feature = e.target.value; fetchData(); });
els.yearSlider.addEventListener('input', (e) => { state.year = parseInt(e.target.value); els.yearDisplay.innerText = state.year; fetchData(); });
els.scenarioToggle.addEventListener('change', (e) => { state.scenario = e.target.checked ? 'After' : 'Before'; fetchData(); });
els.closeAiPanel.addEventListener('click', () => { els.aiPanel.classList.add('hidden'); });

async function fetchData() {
    setLoading(true);
    try {
        // 1. Prediction Grid
        const predUrl = `/api/predictions?year=${state.year}&scenario=${state.scenario}`;
        const predRes = await fetch(predUrl);
        const predData = await predRes.json();

        const quantiles = calculateQuantiles(predData, state.feature);

        if (geoJsonLayer) map.removeLayer(geoJsonLayer);

        geoJsonLayer = L.geoJSON(predData, {
            style: (feature) => getFeatureStyle(feature, quantiles),
            onEachFeature: onEachFeature
        }).addTo(map);

        updateLegend(quantiles);

        // 2. IT Park Layers
        clearITParkLayers();
        if (state.scenario === 'After') {
            await fetchITParkLayer();
            fetchAIAnalysis();
        } else {
            els.aiPanel.classList.add('hidden');
        }

    } catch (error) {
        console.error("Main Fetch Error:", error);
        els.status.innerText = "Error";
    } finally {
        setLoading(false);
    }
}

function clearITParkLayers() {
    if (itParkBoundaryLayer) { map.removeLayer(itParkBoundaryLayer); itParkBoundaryLayer = null; }
    if (itParkCirclesLayer) { map.removeLayer(itParkCirclesLayer); itParkCirclesLayer = null; }
}

async function fetchITParkLayer() {
    try {
        const res = await fetch('/api/it-park');
        if (!res.ok) { console.error("API IT Park Error"); return; }
        const data = await res.json();

        // Split features
        const boundaries = data.features.filter(f => f.properties.type === "Boundary");
        const points = data.features.filter(f => f.properties.type === "Point");

        // A. Draw Boundary
        if (boundaries.length > 0) {
            itParkBoundaryLayer = L.geoJSON({ type: "FeatureCollection", features: boundaries }, {
                style: {
                    color: "#000000",
                    weight: 3,
                    opacity: 1,
                    fillColor: "#000000",
                    fillOpacity: 1.0 // High contrast
                }
            }).addTo(map);
            itParkBoundaryLayer.bringToFront();
        }

        // B. Draw Policy Circles (Green/Blue buffers)
        if (points.length > 0) {
            const circleMarkers = [];

            points.forEach(pt => {
                // Geometry is [lon, lat] in GeoJSON, Leaflet needs [lat, lon]
                // L.geoJSON does this automatically, but doing manually for L.circle
                const lat = pt.geometry.coordinates[1];
                const lon = pt.geometry.coordinates[0];
                const latlng = [lat, lon];

                // Green Buffer (500m)
                circleMarkers.push(L.circle(latlng, {
                    radius: 500,
                    color: "green",
                    fillColor: "green",
                    fillOpacity: 0.6,
                    weight: 1
                }).bindPopup("Green Buffer Zone"));

                // Traffic Mgmt (300m)
                circleMarkers.push(L.circle(latlng, {
                    radius: 300,
                    color: "blue",
                    fillColor: "blue",
                    fillOpacity: 0.6,
                    weight: 1
                }).bindPopup("Traffic Management Zone"));
            });

            itParkCirclesLayer = L.layerGroup(circleMarkers).addTo(map);
        }

    } catch (e) {
        console.error("IT Park Logic Error:", e);
    }
}

function calculateQuantiles(data, property) {
    const values = data.features.map(f => f.properties[property]).sort((a, b) => a - b);
    if (values.length === 0) return { q20: 0, q40: 0, q60: 0, q80: 0 };
    const getQ = (q) => values[Math.floor((values.length - 1) * q)];
    return { q20: getQ(0.20), q40: getQ(0.40), q60: getQ(0.60), q80: getQ(0.80) };
}

function getFeatureStyle(feature, q) {
    const v = feature.properties[state.feature];
    let color;
    if (v <= q.q20) color = PALETTE.q20;
    else if (v <= q.q40) color = PALETTE.q40;
    else if (v <= q.q60) color = PALETTE.q60;
    else if (v <= q.q80) color = PALETTE.q80;
    else color = PALETTE.q100;

    return {
        fillColor: color,
        weight: 0,
        color: null,
        fillOpacity: 0.1
    };
}

function onEachFeature(feature, layer) {
    if (feature.properties) {
        const v = feature.properties[state.feature].toFixed(2);
        layer.bindTooltip(`<b>${state.feature}:</b> ${v}`, { sticky: true });
        layer.on('mouseover', (e) => { e.target.setStyle({ weight: 2, color: '#fff', fillOpacity: 0.9 }); });
        layer.on('mouseout', (e) => { geoJsonLayer.resetStyle(e.target); });
    }
}

async function fetchAIAnalysis() {
    /* Same analysis logic */
    els.aiPanel.classList.remove('hidden');
    els.aiSeverity.innerText = "AI suggestions based on predictive analysis...";
    els.aiMetrics.innerHTML = ""; els.aiRecommendations.innerHTML = "<div>Loading...</div>";
    try {
        const res = await fetch(`/api/impact-analysis?year=${state.year}`);
        const data = await res.json();
        const m = data.delta_metrics;
        if (m) {
            els.aiMetrics.innerHTML = `
                <div class="metric"><span class="metric-label">Temp</span><span class="metric-value">+${m.temperature_rise}°C</span></div>
                <div class="metric"><span class="metric-label">Traffic</span><span class="metric-value">+${m.traffic_increase}</span></div>
                <div class="metric"><span class="metric-label">PM2.5</span><span class="metric-value">+${m.pm25_worsening}</span></div>
            `;
        }
        els.aiSeverity.innerText = data.severity;
        els.aiRecommendations.innerHTML = data.recommendations.map(r => `<div class="rec-item">${r}</div>`).join('');
    } catch (e) { els.aiRecommendations.innerHTML = "Analysis Failed"; }
}

function updateLegend(q) {
    let html = `<b>${state.feature}</b><br>`;
    html += `<div style="display:flex; align-items:center;"><span style="background:${PALETTE.q20}; width:10px; height:10px; margin-right:5px;"></span> Low</div>`;
    html += `<div style="display:flex; align-items:center;"><span style="background:${PALETTE.q60}; width:10px; height:10px; margin-right:5px;"></span> High</div>`;
    html += `<div style="display:flex; align-items:center;"><span style="background:${PALETTE.q100}; width:10px; height:10px; margin-right:5px;"></span> Extreme</div>`;
    els.legendContent.innerHTML = html;
}

function setLoading(b) { if (b) els.loading.classList.remove('hidden'); else els.loading.classList.add('hidden'); }

fetchData();
