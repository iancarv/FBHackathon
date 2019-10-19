require('dotenv').config()
const ZAMZAR_API_KEY = process.env.ZAMZAR_API_KEY;
var request = require('request'),
    fs = require('fs'),
    apiKey = ZAMZAR_API_KEY


module.exports = {
    convertFile: function(url) {
        formData = {
            source_file: url,
            target_format: 'flac'
        };
    
        request.post({url:'https://api.zamzar.com/v1/jobs/', formData: formData}, function (err, response, body) {
            if (err) {
                console.error('Unable to start conversion job', err);
            } else {
                console.log('SUCCESS! Conversion job started:', JSON.parse(body));
            }
        }).auth(apiKey, '', true);
    }
}