/**
 * Copyright 2017-present, Facebook, Inc. All rights reserved.
 *
 * This source code is licensed under the license found in the
 * LICENSE file in the root directory of this source tree.
 *
 * Messenger Platform Quick Start Tutorial
 *
 * This is the completed code for the Messenger Platform quick start tutorial
 *
 * https://developers.facebook.com/docs/messenger-platform/getting-started/quick-start/
 *
 * To run this code, you must do the following:
 *
 * 1. Deploy this code to a server running Node.js
 * 2. Run `npm install`
 * 3. Update the VERIFY_TOKEN
 * 4. Add your PAGE_ACCESS_TOKEN to your environment vars
 *
 */

'use strict';
const request = require('request');
const s2t = require('./s2t')
const PAGE_ACCESS_TOKEN = process.env.PAGE_ACCESS_TOKEN;
const VERIFY_TOKEN = process.env.VERIFY_TOKEN;

var express = require('express')
var router = express.Router()

router.get('/', (req, res) => {  
    res.status(200).send('RELOU UORDI');
});

var ctx = {

}

// Accepts POST requests at /webhook endpoint
router.post('/webhook', (req, res) => {  
    console.log('POST');
  // Parse the request body from the POST
  let body = req.body;
  console.log(body);
  // Check the webhook event is from a Page subscription
  if (body.object === 'page') {
    try {
      body.entry.forEach(function(entry) {
        // Gets the body of the webhook event
        let webhook_event = entry.messaging[0];
        // Get the sender PSID
        let sender_psid = webhook_event.sender.id;
        if (ctx[sender_psid] == undefined) {
          ctx[sender_psid] = {'state':'start'};
        }
  
        sendSenderAction(sender_psid, 'mark_seen');
        console.log('Sender ID: ' + sender_psid);
  
        // Check if the event is a message or postback and
        // pass the event to the appropriate handler function
        if (webhook_event.message) {
          handleMessage(sender_psid, webhook_event.message);        
        } else if (webhook_event.postback) {
          handlePostback(sender_psid, webhook_event.postback);
        }
        
      });
    } catch (error) {
      
    }
    res.status(200).send('EVENT_RECEIVED');
    
    // Return a '200 OK' response to all events
  } else {
      // Return a '404 Not Found' if event is not from a page subscription
    res.sendStatus(404);
  }

});

// Accepts GET requests at the /webhook endpoint
router.get('/webhook', (req, res) => {
  // Parse params from the webhook verification request
  let mode = req.query['hub.mode'];
  let token = req.query['hub.verify_token'];
  let challenge = req.query['hub.challenge'];
  // Check if a token and mode were sent
  if (mode && token) {
  
    // Check the mode and token sent are correct
    if (mode === 'subscribe' && token === VERIFY_TOKEN) {
      
      // Respond with 200 OK and challenge token from the request
      console.log('WEBHOOK_VERIFIED');
      res.status(200).send(challenge);
    
    } else {
      // Responds with '403 Forbidden' if verify tokens do not match
      res.sendStatus(403);      
    }
  }
});


async function answerMessage(received_message, ctx) {
  let text;
  if (received_message.text) {  
    text = received_message.text;
  } else if (received_message.attachments) {
    let attachment_url = received_message.attachments[0].payload.url;
    if (attachment_url == undefined) {
      return
    } 
    let type = received_message.attachments[0].type;
    if (type === 'image') {
      return "That's a giggly picture."
    } else if(type === "video") {
      return "That's a very cool video. Let's get Giggly"
    }

    text = await s2t.convertToText(attachment_url)
  }
  text = text.toLowerCase();
  console.log('text ' + text);

  if(ctx.state == 'video') {
    let lookup = {
      'baby-shark': 'https://www.facebook.com/VT/videos/536146063482335/',
      'peppa-pig': 'https://www.facebook.com/CartoonTV001/videos/386102755462742/',
      'itsy-bitsy': 'https://www.facebook.com/Noeraroo/videos/879831325510591/'
    }
    let url = lookup[text];
    console.log(url);
    console.log(text)
    let response = {
      "attachment":{
        "type":"template",
        "payload":{
          "template_type":"media",
          "elements":[
             {
              "media_type": "video",
              "url":url
            }
          ]
        }
      }
    }
    ctx.state = 'start'
    return response
  } else if (ctx.state == 'start') {
    if(text.includes('games')) {
      ctx.state = 'twitch'
    } else if (text.includes('video')) {
      ctx.state = 'video'
      let response =  {
        "attachment": {
          "type": "template",
          "payload": {
            "template_type": "generic",
            "elements": [{
              "title": "What kind of video do you want to see?",
              "subtitle": "Tap a button to answer.",
              "buttons": [
                {
                  "type": "postback",
                  "title": "Baby Shark!",
                  "payload": "baby-shark",
                },
                {
                  "type": "postback",
                  "title": "Peppa Pig!",
                  "payload": "peppa-pig",
                },
                {
                  "type": "postback",
                  "title": "Itsy Bitsy Spider!",
                  "payload": "itsy-bitsy",
                }
              ],
            }]
          }
        }
      } 
      return response
    }


  } else if (ctx == 'twitch') {
    text = 'Twitch Context';
  }


  return {'text': text};
}


function handleMessage(sender_psid, received_message) {
  sendSenderAction(sender_psid, 'typing_on');
  let actualCtx = ctx[sender_psid];
  console.log('CONTEXT');
  console.log(actualCtx.state);
  answerMessage(received_message, actualCtx).then(response => {
    console.log('response ' + response)
    if (response) {
      callSendAPI(sender_psid, response);
    }
    sendSenderAction(sender_psid, 'typing_off');
  })
}

function handlePostback(sender_psid, received_postback) {
  sendSenderAction(sender_psid, 'typing_on');
  let payload = received_postback.payload;
  let actualCtx = ctx[sender_psid];
  console.log('CONTEXT');
  console.log(actualCtx.state);
  console.log(payload);
  answerMessage({'text': payload}, actualCtx).then(response => {
    console.log('response ' + response)
    if (response) {
      callSendAPI(sender_psid, response);
    }
    sendSenderAction(sender_psid, 'typing_off');
  })
}

function sendSenderAction(psid, action) {
  // Construct the message body
  let request_body = {
    "recipient": {
      "id": psid
    },
    "sender_action": action
  }
  console.log('sending sender');
  // Send the HTTP request to the Messenger Platform
  request({
    "uri": "https://graph.facebook.com/v2.6/me/messages",
    "qs": { "access_token": PAGE_ACCESS_TOKEN },
    "method": "POST",
    "json": request_body
  }, (err, res, body) => {
    if (!err) {
      console.log('action sent!')
    } else {
      console.error("Unable to send message:" + err);
    }
  }); 
}

function callSendAPI(sender_psid, response) {
  // Construct the message body
  let request_body = {
    "recipient": {
      "id": sender_psid
    },
    "message": response
  }
  console.log('sending api');
  // Send the HTTP request to the Messenger Platform
  request({
    "uri": "https://graph.facebook.com/v2.6/me/messages",
    "qs": { "access_token": PAGE_ACCESS_TOKEN },
    "method": "POST",
    "json": request_body
  }, (err, res, body) => {
    if (!err) {
      console.log('message sent!')
    } else {
      console.error("Unable to send message:" + err);
    }
  }); 
}

module.exports = router