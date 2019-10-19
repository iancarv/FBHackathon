require('dotenv').config()
const
  express = require('express'),
  bodyParser = require('body-parser'),
  app = express().use(bodyParser.json()); // creates express http server
const fb = require('./fb')
const port = 3000

app.use('/', express.static('./dist', {
  index: "index.html"
}))

app.listen(port, () => console.log(`Example app listening on port ${port}!`))

app.use('/fb', fb)