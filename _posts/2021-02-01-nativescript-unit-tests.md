---
title: "NativeScript Unit Testing using NG10 and NS7"
tags: ["nativescript", "unit-test"]
---

I played with NS6 a year ago and doing unit testing worked, based on the documentation provided with a few minor adjustments.

Recently created a new NS7 project and wanted build my app following some kind of test driving development methodology. The second
I added ``nsTestBedInit()`` call in my tests. Everything broke. Any of my tricks I used in NS6 failed. So I guessed it must be because of NG10,
and the NS unit testing code has not been thoroughly tested and updated to handle it.

Please note that the [Nativescript docs say unit testing](https://docs.nativescript.org/angular/tooling/testing/testing) is for testing **Javascript Functionality**, not the UI. I guess that's what [Appium](https://docs.nativescript.org/tooling/testing/end-to-end-testing/overview) is for, which is next on my list to perfect for my project.

## First error message

``Node is not defined``.  After some troubleshooting I figured out that this has
do with the webpack versions. So I fixed it and hit another problem...


## Second error message

``currentNode not defined``.  It seemed like the [``nsTestBedInit()``](https://github.com/NativeScript/nativescript-angular/blob/master/nativescript-angular/testing/src/util.ts) and related functions were not created the initial Nativescript Frame/Page that it seems to depend on to attach a Layout Component.  I overcame this by writing some custom code to build this. It didn't help. So I found a post which said you can inject a component instead of applying it the declaration list. Basically avoiding all the dom building code. Okay I did this, but now I encountered the strangest error

## Third error message

``Zone already loaded``. After lots of debugging I found that [@nativescript/zone-js](https://github.com/NativeScript/zone.js/blob/master/lib/zone.ts#L648) Zone creation is conflicting with the Angular TestBed zone creation software. I found the solution was to just rebuild the nsTestBedInit and related helpers and remove all references to Nativescript calls.

Now I was finally able to unit test... but only on Android...

On my macbook, which is M1 by the way..(that had its own challenges)... I got the following error

## Forth error message

``...dirname not defined``:  I found a post on a nativescript issue that said its related to the Karma webpack version. You have to hard code to 3.0.5. I was using 4.x.x.  Once I did this.. I was finally able to perform unit tests on components. As the Nativescript unit test documentation page says, only test the functions, not the DOM. Which makes sense. But this has now greatly improved the confidence in my project as it grows ever so complicated.

I hope this posting helps someone. Now no more boring explanations, here is the code that worked. Again I'm using NG10 , and NS7. I have not tested NG11 yet.

* [./package.json](https://gist.github.com/linuxsimba/66d5bfd2c95f3d082a39a6d306f4abdf): pay special attention to the webpack versions. basically wherever the word 'webpack' shows up. Clear node_modules and run a clean npm install afterwards. I didn't do that at first and found issues.
* [./karma.conf.js](https://gist.github.com/linuxsimba/a29d79a48f764e2522477f7ebc39b548): just made a few modifications from what `ns test init` produces
* [./src/tests/setup.ts](https://gist.github.com/linuxsimba/12dc983bd542b73e86b487ab590bf4e2): create custom test helpers. I have an example of how use it in the component example
* [./src/tests/test.component.spec.ts](https://gist.github.com/linuxsimba/27324f7c3c5c267f124e703a9990f446): example component unit file
* [./src/tests/test.service.spec.ts](https://gist.github.com/linuxsimba/ffdf3ef7964523f57a4f9cbcdd6462e8): example service spec file

