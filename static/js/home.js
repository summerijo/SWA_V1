// Select all nav links and add an event listener for active class toggle
const navLinks = document.querySelectorAll('.nav-link');

navLinks.forEach(link => {
    link.addEventListener('click', function() {
        // Remove 'active' class from all links and add to the clicked one
        navLinks.forEach(nav => nav.classList.remove('active'));
        this.classList.add('active');
    });
});

// Initialize the Leaflet map with desired coordinates and zoom level
const map = L.map('map').setView([51.505, -0.09], 13);

// Add the OpenStreetMap tile layer to the map
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 18,
    attribution: '© OpenStreetMap contributors'
}).addTo(map);

// Optional: Add a marker at specified coordinates with a popup message
const marker = L.marker([51.505, -0.09]).addTo(map);
marker.bindPopup("<b>Hello!</b><br>This is your marker.").openPopup();

// Offset scroll for map section when clicking the map link
document.querySelector('a[href="#map-section"]').addEventListener('click', function (e) {
    e.preventDefault();
    const targetSection = document.querySelector('#map-section');
    const offset = 70; // Adjust this value to match the navbar height
    const topPosition = targetSection.getBoundingClientRect().top + window.scrollY - offset;
    window.scrollTo({ top: topPosition, behavior: 'smooth' });
});
