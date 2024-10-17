var map = L.map('map').setView([9.801081, 126.119202], 13);
        var currentMarker = null; // Store the currently displayed marker

        // Add tile layer
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 19
        }).addTo(map);

        let hourlyChart; // Store Chart.js instance

        // Function to create or update a chart
        function createOrUpdateChart(chart, ctx, labels, data, label) {
            if (chart) {
                chart.data.labels = labels;
                chart.data.datasets[0].data = data;
                chart.update();
            } else {
                chart = new Chart(ctx, {
                    type: 'line',
                    data: {
                        labels: labels,
                        datasets: [{
                            label: label,
                            data: data,
                            borderColor: 'rgba(75, 192, 192, 1)',
                            fill: false,
                        }]
                    },
                    options: {
                        responsive: true,
                        plugins: {
                            legend: { display: true }
                        }
                    }
                });
            }
            return chart;
        }

        // Add click event listener on the map
        map.on('click', function(e) {
            var lat = e.latlng.lat.toFixed(6);
            var lng = e.latlng.lng.toFixed(6);

            // Check if the current marker already exists
            if (currentMarker) {
                // Remove the existing marker
                map.removeLayer(currentMarker);
                currentMarker = null; // Reset the current marker
                // Reset table values and location info
                document.getElementById('swellHeight').innerText = 'N/A';
                document.getElementById('swellTimestamp').innerText = 'N/A';
                document.getElementById('swellDirection').innerText = 'N/A';
                document.getElementById('swellPeriod').innerText = 'N/A';
                document.getElementById('locationLat').innerText = 'N/A';
                document.getElementById('locationLng').innerText = 'N/A';
            } else {
                // Fetch stored swell data from the backend
                fetch('/get-stored-data', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ latitude: lat, longitude: lng })
                })
                .then(response => response.json())
                .then(data => {
                    console.log('Data received from server:', data);

                    if (data.success) {
                        // Update the location information
                        document.getElementById('locationLat').innerText = lat;
                        document.getElementById('locationLng').innerText = lng;

                        // Update the current swell data table
                        document.getElementById('swellHeight').innerText = data.current.swell_wave_height + ' m';
                        document.getElementById('swellTimestamp').innerText = data.current.time || 'N/A'; 
                        document.getElementById('swellDirection').innerText = data.current.swell_wave_direction || 'N/A';
                        document.getElementById('swellPeriod').innerText = data.current.swell_wave_period || 'N/A';



                        // Plot hourly swell data
                        const hourlyCtx = document.getElementById('hourlySwellChart').getContext('2d');
                        hourlyChart = createOrUpdateChart(
                            hourlyChart,
                            hourlyCtx,
                            data.hourly.time,
                            data.hourly.swell_wave_height,
                            'Hourly Swell Wave Height'
                        );

                        // Add marker to the clicked location
                        currentMarker = L.marker([lat, lng]).addTo(map)
                            .bindPopup(`Latitude: ${lat}<br> Longitude: ${lng} `)
                            .openPopup();
                    } else {
                        alert('No data found for this location.');
                    }
                })
                .catch(error => console.error('Error:', error));
            }
        });