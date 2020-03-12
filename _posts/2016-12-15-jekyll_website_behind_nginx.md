---
title: Placing a Jekyll Blog behind a SSL Nginx Proxy
tags: ['nginx','jekyll', 'ssl']
---

[Linuxsimba.com](https://linuxsimba.com) is now behind a Nginx SSL Proxy.

I have always been confused by SSL Nginx configuration. So here's is what I did to get it working.

### Create the Certificate

My service provider gives me a free SSL certificate for the website.

First create the Certificate Request.

```
openssl req -nodes -newkey rsa:2048 -sha256 -keyout linuxsimba.key -out linuxsimba.csr
```

> Remember to save the **SSL private key** !!

Why not use 4096 bit certificate? Here is a [blog post](https://certsimple.com/blog/measuring-ssl-rsa-keys) that shows a 2048 bit certificate is good enough.


### Upload the CSR to the Certificate Request form
The service provider had a Certificate Request form where I could upload the ``linuxsimba.csr`` file.

After an hour the SSL certificate creation was complete. The service provider SSL web page offered 2 certificates for download.
There were:

* Server Certificate
* Intermediary Certificate

__Intermediary Certificate??__ Its a certificate that verifies that your certificate is legit. It creates what the industry calls a certificate chain.  Here is what linuxsimba.com's certificate chain looks like.
<table>
<tr>
<td>**SSL Command:**</td>
<td>``openssl s_client -showcerts -connect linuxsimba.com:443``</td>
<tr>
</tr>
<tr><td>**Output:**</td>
<td>
[OpenSSL s_client output](https://gist.github.com/linuxsimba/3d9f504c4757bc971bc2e89a56a81273)
</td></tr>
</table>  


With the 2 certificates, the server and intermediary certificate, you then have to
place the 2 certs in the same file like so

```
cat server.crt serverproviderCA.pem >> linuxsimba.crt
```

### Copy the files into cert and private key into NGINX related directories

Remember that SSL key that was generated as part of the Certificate Request(CSR)? You need it now!

Do these steps on the host that will run nginx.

```
cp linuxsimba.crt /etc/nginx/certs
cp linuxsimba.key /etc/nginx/private/
chmod 400 /etc/nginx/private/linuxsimba.key
```

### What the Nginx.conf file looks like

{% gist linuxsimba/5a295ff2a333bded04d366b95fcc99c6 %}
