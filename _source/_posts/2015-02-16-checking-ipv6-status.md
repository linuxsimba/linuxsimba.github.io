---
title: Checking Server IPv6 status
tags: ['ipv6']
---

> Note: Dec 2016 - Had to move the site to a provide who doesn't provide IPv6.
Hopefully the provider will use IPv6 soon.

In an [earlier post]({% post_url 2015-02-15-ipv6-blog-ip %}), I setup IPv6 on
the server hosting this blog. I figured out how to verify the IPv6 setup.

### Checking that DNS has IPv6 hostname
```
$ host -t AAAA linuxsimba.com
linuxsimba.com has IPv6 address 2600:3c02::f03c:91ff:fe93:7057
```

### IPv6 Connectivity Verification
Some websites recommend using [ipv6-test.com](http://ipv6-test.com) to verify
IPv6 connectivity. The site requires Javascript and my server does not have GUI
software.

I tried to [recompile
elinks with
Javascript](http://elinks.or.cz/documentation/html/manual.html-chunked/ch01s06.html) and failed.

I found success in deploying [PhantomJS](http://phantomjs.org/), a headless
browser, normally used for website testing.

* First I installed [NVM](https://github.com/creationix/nvm)
which I used to install [Node](http://nodejs.org)
* Then installed [PhantomJS](http://phantomjs.org) using NPM.
`npm install -g phantomjs`
* The following [script](https://gist.github.com/skamithi/6cb7e26975eb3ee472eb) then grabs IPv6 connectivity results from
[ipv6-test.com](http://ipv6-test.com)

```
$ phantomjs ipv6-test.js
'waitFor()' finished in 655ms.

  IPv6
  Supported

  Address
  2600:3c02::f03c:91ff:fe93:7057

  Type
  Native IPv6

```

