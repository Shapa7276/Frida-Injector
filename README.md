# "Frida-Injector" It automates  the Injection of FRIDA-gadget binary into an Android application , in order to Hook function or bypass SSL Pinning of that application on Non rooted Device


**#Usage:- Frida-Injector.py [-h] [-i inputfile] [-m 1 or 2)]**

* Method1:-Injecting into bytecode (Preferred method)
* Method2:-Injecting as dependency to a native library (JNI)

![GitHub Logo](/images/Screenshot_1.jpg)
**#prerequisite :- latest versions of adb ,apktool,USB debugging enabled on device and Configure device with Burp proxy using (https://portswigger.net/support/installing-burp-suites-ca-certificate-in-an-android-device)**


What it does

**Method1:-Injecting into bytecode**

* Reverse the apk using apktool.
* Download all the lated frida gadget from (https://github.com/frida/frida/releases/latest)
* copy aproriate frida-gadget
* Inject smali to load frida-gadget Library
* Recompile the application 
* Sign with uber-apk-signer 
* Install the application to connected Device 
* Push the Burp certicate on local temp directory 
* Call frida function to bypass SSL- pinning 

**Method2:-Injecting as dependency to a native library**
* Reverse the apk using apktool.
* Download all the lated frida gadget from (https://github.com/frida/frida/releases/latest)
* List the availble native directory to Inject the frida-agent.so
* add frida-agent.so as a dependency of native library
* Recompile the application 
* Sign with uber-apk-signer 
* Install the application to connected Device 
* Push the Burp certicate on local temp directory 
* Call frida function to bypass SSL- pinning 


**Referene :-**

* https://koz.io/using-frida-on-android-without-root/
* https://lief.quarkslab.com/doc/stable/tutorials/09_frida_lief.html
* https://fadeevab.com/frida-gadget-injection-on-android-no-root-2-methods/
* https://github.com/kiks7/frida-non-root
