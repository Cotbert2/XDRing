const express = require('express');
const app = express();


const http = require('http').Server(app);

//Comunicacion
const io = require('socket.io')(http);


//routes
app.use(require('./routes.js'));

app.use(express.static(__dirname + "/public"))

io.on('connection', (socket) => {
    socket.on('stream', (image) => {
        socket.broadcast.emit('stream', image)
    });
})


module.exports = http;