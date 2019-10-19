const tmi = require('tmi.js');

const TWITCH_TOKEN = process.env.TWITCH_TOKEN;


var buildClient = function(channel) {
  if (!channel.includes('#')) {
    channel = '#'+channel;
  }
  // Define configuration options
  var opts = {
    identity: {
      username: 'iancarv',
      password: TWITCH_TOKEN
    },
    channels: [
      channel
    ]
  };

  // Create a client with our options
  var client = new tmi.client(opts);

  // Register our event handlers (defined below)
  // client.on('message', onMessageHandler);
  client.on('connected', onConnectedHandler);

  // Connect to Twitch:
  client.connect();

  var test = true;

  // Called every time a message comes in
  function onMessageHandler (target, context, msg, self) {
    if (self) { return; } // Ignore messages from the bot

    // Remove whitespace from chat message
    const commandName = msg.trim();
    console.log(`* Unknown command ${commandName}`);
  }

  // Called every time the bot connects to Twitch chat
  function onConnectedHandler (addr, port) {
    console.log(`* Connected to ${addr}:${port}`);
  //   setTimeout(function(){ console.log("Hello"); client.say("#mukluktwitch", 'This is a test :)'); }, 3000);
  }

  return client
}


module.exports = buildClient