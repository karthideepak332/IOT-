// socket_io.js

var socket = io.connect('http://' + document.domain + ':' + location.port);

socket.on('distance_update', function (data) {
    document.getElementById('distance').value = data.distance;
});

// Optional: You can send events to the server to trigger updates
setInterval(function() {
    socket.emit('update_distance');
}, 5000); // Send update request every 5 seconds (adjust as needed)
