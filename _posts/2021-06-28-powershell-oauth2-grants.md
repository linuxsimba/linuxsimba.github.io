---
title: "Using PowerShell to configure Enterprise App User Consents"
tags: ["powershell", "azure"]
---

I spent quite of time fighting off application integrations into Microsoft Teams that require admin approval that gives a 3rd party enterprise application
permission to read or write into the tenant's chat, file locations. 

Decided to spend some time if there was a way to configure an integration but the 3rd party application integrator never sees the message _"admin approval required"_

So here goes. Appspace a Cisco product integrates with Microsoft Teams by sending Team chat write requests into specific Teams channels.  To do this the AppSpace folks
created a [multi-tenant enterprise application](https://www.youtube.com/watch?v=B416AxHoMJ4) then using some REST-API magic in their cloud app, ask the Appspace Admin to seek approval to integrate with Teams. 

I was asked by our global security czar to figure out how to do this without granting the Appspace admin any escalated privileges. So here goes.

A global admin:
* creates a service principal (app instance) of the Appspace application in the tenant
* configures the appropriate oauth2 permissions
* assigns these permissions to the Azure Active Directory system account owned by the Appspace admin. 

All the appspace admin does is goes to their admin page, begins the Teams integration, enters the appspace azure system account when prompted and voila, connection is automatically made. It's beautiful and secure. 

Appspace functional account is subject to access/ownership reviews and uses a one time password system, so there is decent security with the system account.

What really made me angry is how long it took to figure this out - 3 days! I was lost in the dozens of web pages that show how you invoke Graph API using PowerShell. Some really complicated junk. It was so simple. Just two simple command `connect-MgGraph` and `Invoke-MgGraphRequest`. Now perform a web search for those commands and yeah, you don't find much. Microsoft, your documentation sucks !!! But I guess that keeps me employed.  I realized after web searching for a few hours that my best bet is to just track the correct Graph API then figure out how to run the graph API in PowerShell. Yeah it was requirement I figure this out in Powershell.  

Happy to say I'm putting this problem behind me and I hope it is helpful to someone searching the internet and going crazy trying to find a simpler solution to the question "How the hell do you I run graph API calls using PowerShell".  

Microsoft seems to be building a (huge library of PowerShell commands that access Graph API)[https://www.powershellgallery.com/packages/Microsoft.Graph/1.6.0], some which don't work, like `New-MgServicePrincipalOauth2PermissionGrantByRef`. 

I hope this gist is helpful to someone out there and you don't have to spend 3 days finding this info. 

{% gist linuxsimba/be966938393aeb94b477d4acfe4bf661 %}




