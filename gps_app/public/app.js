// Global map variable
let map;

// Function to show an error message on the UI
function showError(message) {
    const errorContainer = document.getElementById('error-container');
    errorContainer.textContent = message;
    errorContainer.style.display = 'block';
    setTimeout(() => {
        errorContainer.style.display = 'none';
    }, 5000); // Hide after 5 seconds
}

// Function to show the loading spinner while fetching data
function showLoadingSpinner() {
    document.getElementById('loading-spinner').style.display = 'block';
}

// Function to hide the loading spinner once data is fetched
function hideLoadingSpinner() {
    document.getElementById('loading-spinner').style.display = 'none';
}

function initialize() {
    map = new google.maps.Map(document.getElementById('map'), {
        center: { lat: 0, lng: 0 }, // Set your initial map center
        zoom: 12 // Set the initial zoom level
    });

    function updateMap(lat, lng) {
        const location = new google.maps.LatLng(lat, lng);
        map.setCenter(location);
        const marker = new google.maps.Marker({
            position: location,
            map: map
        });
    }

    function fetchGPSData() {
        showLoadingSpinner(); // Show the loading spinner while fetching data
        fetch('/gps_data') // Replace with your API endpoint
            .then(response => response.json())
            .then(data => {
                updateMap(data.lat, data.longi);
                hideLoadingSpinner(); // Hide the loading spinner after data is fetched
            })
            .catch(error => {
                showError('Error fetching GPS data: ' + error);
                hideLoadingSpinner(); // Hide the loading spinner in case of an error
            });
    }

    // Fetch GPS data every X seconds (adjust as needed)
    setInterval(fetchGPSData, 5000); // Update every 5 seconds
}
