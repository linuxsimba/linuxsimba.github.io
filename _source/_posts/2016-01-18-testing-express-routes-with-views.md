---
title: Test for View Template Name Used in Express.js Route
tags:
  - express
  - mocha
  - sinon
---

Came across an interesting problem discussed on [stackoverflow](http://stackoverflow.com/questions/28990887/unit-test-express-route-calls-controller-method/33792992)
The person wants to do something like [named routes in RubyOnRails](https://relishapp.com/rspec/rspec-rails/docs/routing-specs/named-routes)

Was unable to provide an answer for the question, but was able to solve a subset
of the problem. This solution meets the current problem I face.

That is, how does one determine if the Express route executes the correct view template.

The majority of my code is JSON API calls, so just using the
[supertest](https://github.com/visionmedia/supertest) API is
sufficient, in most cases.

There are a few ``app.render()`` calls made in the project.  I use Jade
templates to render the main HTML pages and so this solution works for now.

### controller/main.js

```javascript

exports.index = function(req, res) {
  return res.render('index');
};
```

### routers/main.js

```javascript

var mainController, routes;

mainController = require('../controllers/main');

routes = function(app) {
  return app.get('/', mainController.index);
};

module.exports = routes;
```

### test/routes/test_main.js

```javascript
var app, expect, request, sinon;

request = require('supertest');

app = require('../../app');

expect = require('chai').expect;

sinon = require('sinon');

describe('GET index', function() {
  before(function() {
    return this.spy = sinon.spy(app, 'render');
  });
  after(function() {
    return this.spy.restore();
  });
  it('should exist', function() {
    return request(app).get('/').expect(200);
  });
  return it('should render the "index" view', function() {
    return expect(this.spy.getCall(0).args[0]).to.be.eql('index');
  });
});
```

### Result

```bash
$ npm test

  GET index
    ✓ should exist
    ✓ should render the "index" view


  2 passing (326ms)

```
