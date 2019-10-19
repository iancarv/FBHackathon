/**
 * Copyright 2017, Google, Inc.
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *    http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

'use strict';
const spawn = require('child_process').spawnSync;
const speech = require('@google-cloud/speech'),
 fs = require('fs');

var exampleUrl = 'https://cdn.fbsbx.com/v/t59.3654-21/73482881_2395018734087157_680614589699719168_n.aac/audioclip-1571465943315-4067.aac?_nc_cat=108&_nc_oc=AQmYIWyJJeGAouEMBWCJ6NvOxDebk7qo_AZwGSg3a8ONkq5QXTEh5rvx-Bs3MuFkjV-TD-YtxeBZbc-e9fAQ1iEW&_nc_ht=cdn.fbsbx.com&oh=68acae81088ff764ca612a5226d68ef2&oe=5DAD5786'

var convertToFlac = function(pathToAudio, fileName, callback) {
  console.log('Converting'+pathToAudio);
  let ffmpeg = spawn('ffmpeg', ['-i', `${ pathToAudio }`, '-c:a', 'flac', `${ fileName }`]);
}

// convertToFlac(exampleUrl, 'media/audio.flac')

module.exports = {
  convertToText: async function(url) {
    const fileName = 'media/audio.flac'
    convertToFlac(url, fileName)
    const client = new speech.SpeechClient();

    // Reads a local audio file and converts it to base64
    const file = fs.readFileSync(fileName);
    const audioBytes = file.toString('base64');

    // The audio file's encoding, sample rate in hertz, and BCP-47 language code
    const audio = {
      content: audioBytes,
    };
    const config = {
      encoding: 'FLAC',
      sampleRateHertz: 44100,
      languageCode: 'en-US'
    };
    const request = {
      audio: audio,
      config: config,
    };

    // Detects speech in the audio file
    const [response] = await client.recognize(request);
    const transcription = response.results
      .map(result => result.alternatives[0].transcript)
      .join('\n');
    console.log(`Transcription: ${transcription}`);
    return transcription
  }
}

// module.exports.convertToText(exampleUrl).then((transcription)=>{
//   console.log('OK'+transcription)
// })