---
title: "Using PowerShell to configure Enterprise App User Consents"
tags: ["powershell", "azure"]
---

I spent quite some time pushing back on application integrations into Microsoft Teams that require admin approval that gives a 3rd party enterprise application
permission to read or write into the tenant's chat, file locations. 

Is there a way to configure an integration, but the 3rd party application integrator never sees the message _"admin approval required"_?

So here goes. Appspace, a Cisco product, integrates with Microsoft Teams by sending Team chat to write requests into specific Teams channels.  To do this, the AppSpace folks
created a [multi-tenant enterprise application](https://www.youtube.com/watch?v=B416AxHoMJ4), then using some REST-API magic in their cloud app, ask the Appspace Admin to seek approval to integrate with Teams. 

Our global security czar asked me to figure out how to do this without granting the Appspace admin any escalated privileges.

A global admin:
* creates a service principal (app instance) of the Appspace application in the tenant
* configures the appropriate oauth2 permissions
* assigns these permissions to the Azure Active Directory system account owned by the Appspace admin. 

All the Appspace admin does is go to their admin page, begin the Teams integration, enters the Appspace azure system account when prompted, and voila, the connection completes. It's beautiful and secure. 

Appspace's Azure functional account is subject to access/ownership reviews and uses a one-time password system, so there is decent security with the system account.

What made me angry is how long it took to figure this out - 3 days! I reviewed many web pages describing how to send Graph API calls using PowerShell.  It was so simple, just two commands, `connect-MgGraph` and `Invoke-MgGraphRequest`. Now perform a web search for those commands, and yeah, you don't find much. Microsoft, your documentation sucks !!! But I guess that keeps me employed.  After web searching for a few hours, I realized that my best bet is to track the correct Graph API then figure out how to run the graph API in PowerShell. It was a requirement I figure this out in Powershell.  

I'm putting this problem behind me, and I hope it is helpful to someone searching the internet and going crazy trying to find a more straightforward solution to the question "How the hell do I run graph API calls using PowerShell".  

Microsoft seems to be building a (massive library of PowerShell commands that access Graph API)[https://www.powershellgallery.com/packages/Microsoft.Graph/1.6.0], some of which don't work, like `New-MgServicePrincipalOauth2PermissionGrantByRef`. 

I hope this gist is helpful to someone out there, and you don't have to spend three days finding this info. 

{% gist linuxsimba/be966938393aeb94b477d4acfe4bf661 %}




