const express = require('express')
const app = require('./app')

app.get('/add_twitch', (req, res) => {
    var channel = req.query.channel;
    console.log(channel);
    io.sockets.emit('add_twitch', {channel : channel});
    res.status(200).send('EVENT_RECEIVED');
});

app.get('/exit_twitch', (req, res) => {
    io.sockets.emit('exit_twitch', {channel : 'none'});
    res.status(200).send('EVENT_RECEIVED');
});

//Listen on port 3000
server = app.listen(3000)



//socket.io instantiation
const io = require("socket.io")(server)


//listen on every connection
io.on('connection', (socket) => {
	console.log('New user connected')

	//default username
	socket.username = "Anonymous"
    io.sockets.emit('connect', {message : 'mess'});
    //listen on change_username
    socket.on('change_username', (data) => {
        socket.username = data.username
    })

    //listen on new_message
    socket.on('new_message', (data) => {
        //broadcast the new message
        io.sockets.emit('new_message', {message : data.message, username : socket.username});
    })

    //listen on typing
    socket.on('typing', (data) => {
    	socket.broadcast.emit('typing', {username : socket.username})
    })
})