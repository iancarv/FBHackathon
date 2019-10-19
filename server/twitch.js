const tmi = require('tmi.js');

const TWITCH_TOKEN = process.env.TWITCH_TOKEN;

// Define configuration options
const opts = {
  identity: {
    username: 'iancarv',
    password: TWITCH_TOKEN
  },
  channels: [
    '#mukluktwitch'
  ]
};

// Create a client with our options
const client = new tmi.client(opts);

// Register our event handlers (defined below)
client.on('message', onMessageHandler);
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
  if (test) {
    console.log(target);
    // client.say(target, 'This is a test :)');
    test = false;
  }

//   If the command is known, let's execute it
//   if (commandName === '!dice') {
//     const num = rollDice();
//     client.say(target, `You rolled a ${num}`);
//     console.log(`* Executed ${commandName} command`);
//   } else {
//     console.log(`* Unknown command ${commandName}`);
//   }
}

// Function called when the "dice" command is issued
function rollDice () {
  const sides = 6;
  return Math.floor(Math.random() * sides) + 1;
}

// Called every time the bot connects to Twitch chat
function onConnectedHandler (addr, port) {
  console.log(`* Connected to ${addr}:${port}`);
//   setTimeout(function(){ console.log("Hello"); client.say("#mukluktwitch", 'This is a test :)'); }, 3000);
}