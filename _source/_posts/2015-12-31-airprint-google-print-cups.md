---
title: Setup CUPS on Ubuntu with AirPrint and Google Print Server Support
tags: ['cups', 'google-print', 'airprint']
---

## Equipment:
* Ubuntu 14.04 Server
* Samsung CLX-3185 USB Printer _(no wifi module)_

## Goal

Setup Ubuntu 14.04 Server as Print server for the Ipads/Iphones/Android phones
in the house.

## Prep CUPS Server

### Install CUPS and necessary dependencies

```
sudo apt-get install cups
sudo apt-get install python-cups
sudo apt-get install avahi-discover
```

### Setup CUPs with remote admin access
By default, CUPS Admin Portal at port 631 runs only on localhost. The following
command allows you to control it from any device on the subnet.

```
sudo cupsctl --remote-admin
sudo cups restart
```

When all configuration was finished, and test pages from Android and Apple mobile
devices worked, the remote-admin access was disabled.

```
sudo cupsctl --no-remote-admin
sudo cups restart
```

### Add the Printer to CUPS

Click on:

  * "Adding Printers and Classes" then

  * "Add Printer". Clicking this may prompt a Basic Auth  prompt.
Use the credentials for the user that ran ``sudo`` when installing CUPS.
CUPS is able to do this, by checking if the user belongs to the ``lpadmin`` group.
  * In my case, the Samsung printer was not in the default set of printer PPDs.
Installing the [Linux Samsung Installer](http://www.bchemnet.com/suldr/) and restarting the CUPS service resolved
that issue.

  * Send a Test Page to the Printer from the "Manage Printers" section, to
confirm that the installation works.


## Configuring AirPrint Support

AirPrint support is enabled via the Avahi service. By default, when the ``avahi-discover``
deb is installed, no print services are advertised.

### Adding Printer to Avahi

Download this [handy python script](https://raw.github.com/tjfontaine/airprint-generate/master/airprint-generate.py) that loads all the CUPS printers into the Avahi service. Restart the Avahi daemon when this is done.

```
wget https://raw.github.com/tjfontaine/airprint-generate/master/airprint-generate.py
sudo python airprint-generate.py -d /etc/avahi/services
sudo service avahi-daemon restart
```

The printer should now be viewable by the Macbook Print Utility and the Print
utilities on Apple mobile devices.

## Configuring Google Print Support

Google provides a [CUPS connector](https://github.com/google/cups-connector) written in GoLang.
The connector by default runs in _local_ mode. This mode means that on the
same subnet, the Android device will able to see the printer. This mode requires
**no** configuration. Just start the connector app.

There is another mode, where it connects fully, to Google Print Web service and you can print
 from anywhere. There is no need for that in this setup. That mode does require
a config file and authorization from a Google account.

### Install the CUPS connector
In the wiki mentioned in the README is an INSTALL section that describes how to install
the connector.

```
 wget https://github.com/google/cups-connector/releases/download/2015.10.05/gcp-cups-connector-linux-amd64-2015.10.05.tar.gz
tar xvfz gcp-cups-connector-linux-amd64-2015.10.05.tar.gz
sudo mv gcp-cups-connector /usr/bin

```

### Create a simple init script to start the connector

Here is the simple init script to start the Google Print CUPs connector on bootup.
Just install the mentioned file. Nothing else needs to be done. Upstart will do the rest.
For those running systemd, I'm sure an equivalent systemd startup file is easy to create.

#### /etc/init/gcp-cups-connector.conf
{% gist 76842d7a58f2d6ffa840 %}

### Start the Google Print CUPs connector
```
sudo service gcp-cups-connector start
```

## References

* [Link to advertise CUPS printer in Avahi (AirPrint)](https://wiki.archlinux.org/index.php/Avahi)
* [Widely referenced Airprint/Cups/Ubuntu Blog Post](https://david.gyttja.com/2010/11/11/airprint-on-ubuntu/)
* [Google Connector](https://github.com/google/cups-connector)
