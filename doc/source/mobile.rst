Charm for Android
=========================

Here are the simple instructions for deploying Charm:

	1. Install ``Python3ForAndroid.apk`` found in github repository on your Android device.

	2. Install the ``SL4A`` package at the following link: https://android-scripting.googlecode.com/files/sl4a_r5.apk

	3. Charm Advanced Setup: Download ``pkg_resources.py`` and place in the appropriate place using the ADB tool. Configure your device to enable the android debug bridge and connect to your machine via USB. Next, use ``adb`` to push the ``pkg_resources.py`` and ``charm-schemes`` to a specified location on your SD card. Execute the following command:

	- ``adb push pkg_resources /mnt/sdcard/com.googlecode.python3forandroid/extras/python3/lib/python3.2/site-packages``

	- ``adb push schemes /mnt/sdcard/sl4a/scripts/schemes``

See more detailed blog posts on installing Charm on Android:

	1. http://mhlakhani.com/blog/2012/05/charm-on-android/

	2. http://michael-rushanan.blogspot.com/2012/07/charm4a-part-0-why-bother.html

