---
title: Running D3.js in Node.js
tags: ['node.js', 'd3']
---

[D3 wiki](https://github.com/mbostock/d3/wiki) says to run d3.js in a node.js environment, do the following:

<blockquote>
 D3 also runs on Node.js. Use npm install d3 to install it.

 Note that because Node itself lacks a DOM and multiple DOM implementations exist
for it (e.g., JSDOM), you'll need to explicitly pass in a DOM element to your d3
 methods like so:
<pre><code>
var d3 = require("d3"),
    jsdom = require("jsdom");

var document = jsdom.jsdom(),
    svg = d3.select(document.body).append("svg");
</code></pre>
</blockquote>

This did not quite work for me.  I needed a little more config.
I use the Express Framework.

This is my config snippets from an [example
github repo](https://github.com/linuxsimba/running-d3-in-node-example)


### server.js
```
require('coffee-script/register');
require('./app');
```


### app.coffee
```
express = require 'express'
load = require 'express-load'
# this is part of node.js handling and transforming file paths.
app = express()
app.d3 = require 'd3'
app.jsdom = require 'jsdom'
app.set 'view engine', 'pug'

load("controllers")
  .into(app)

# define where controllers are stored.
main = app.controllers.main

# render home page as the index() controller in the main controller file
app.get '/', main.index

## listen to the server on port 3000
server = app.listen '3000'
```

### controllers/main.coffee
```
exports.index = (req, res) ->
  d3 = req.app.d3
  html = '<!doctype html><html></html>'
  # jsdom magic to get d3 to work within a DOM
  document = req.app.jsdom.jsdom(html)

  width =  300
  height = 450

  ###
  # draw 2 circles side-by-side
  ###
  circleData = [
    { cx: 20, cy: 25, r: 20, fill: 'blue' },
    { cx: 60, cy: 25, r: 20, fill: 'green'}
  ]
  layoutRoot = d3.select(document.body)
    .append('svg')
  layoutRoot.attr('width', width)
            .attr('height', height)
            .append('g')
            .selectAll('circle')
            .data(circleData)
            .enter()
            .append('circle')
            .attr('cx', (d) ->  d.cx)
            .attr('cy', (d) ->  d.cy)
            .attr('r', (d) -> d.r)
            .attr('fill', (d) -> d.fill)

  # only render text in and include the <svg></svg> tags only
  # draws it in the pug template where !{svgstuff} is defined
  res.render 'index', svgstuff: layoutRoot.node().outerHTML
```


### views/index.pug
```
doctype html
html
  head
  body
    div.container
      h1 Running D3 in Node.js Example
      p Two Circles side-by side
      div#map !{svgstuff}
    footer
```


