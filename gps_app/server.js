const express = require('express');
const mysql = require('mysql');
const app = express();
const port = 3000; // Replace with your desired port number

// MySQL Connection
const connection = mysql.createConnection({
    host: 'bifrost0602.duckdns.org',
    user: 'TEST',
    password: '1234',
    database: 'CANSATDB',
    port: 2024
});

// Connect to the MySQL server
connection.connect((err) => {
    if (err) {
        console.error('Error connecting to MySQL:', err);
        return;
    }
    console.log('Connected to MySQL server!');
});

// Serve static files from the 'public' directory
app.use(express.static('public'));

// API endpoint to fetch GPS data
app.get('/gps_data', (req, res) => {
    const sql = 'SELECT `longi`, `lat` FROM `SENSOR` ORDER BY `TIME` DESC LIMIT 1';
    connection.query(sql, (err, result) => {
        if (err) {
            console.error('Error fetching GPS data from MySQL:', err);
            res.status(500).json({ error: 'Error fetching GPS data' });
            return;
        }
        if (result.length === 0) {
            res.status(404).json({ error: 'No GPS data found' });
            return;
        }
        res.json({ lat: result[0].lat, longi: result[0].longi });
    });
});

// Handle the root route and serve the index.html file
app.get('/', (req, res) => {
    res.sendFile(__dirname + '/public/index.html');
});

// Start the server
app.listen(port, () => {
    console.log(`Server is running on http://localhost:${port}`);
});
