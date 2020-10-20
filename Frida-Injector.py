#!/usr/bin/env python3
#!Author: Sharanbasu Panegav
import subprocess,sys,os,wget,lief
from pathlib import Path
from shutil import copyfile
from xml.dom import minidom
import requests,argparse
from colorama import Fore, Back, Style

apk_name=''
method=''
outputdirectory="lol"
new_apk_name="new.apk"
archdata=["arm","arm64","x86","x86_64"]
abislist=["armeabi-v7a","arm64-v8a","x86","x86_64"]
parser = argparse.ArgumentParser(description='Frida Injection')
parser.add_argument('-i',metavar='inputfile',help='APK_NAME.apk')
parser.add_argument('-m',metavar='(1 or 2))',help='Method 1:-Injecting into bytecode  (Preferred method) Method 2:-Injecting as dependency to a native library (JNI)')
args = parser.parse_args()
apk_name=args.i
method=args.m
def getmainactivity():
    print("Scaning Main Activity")
    activityxml = minidom.parse(outputdirectory+'/AndroidManifest.xml')
    activities = activityxml.getElementsByTagName('activity')
    for activity in activities:
        intentFilterTag = activity.getElementsByTagName("intent-filter")
        if len(intentFilterTag) > 0:
            for intent in intentFilterTag:
                categoryTag = intent.getElementsByTagName("category")
                if len(categoryTag) > 0:
                    for category in categoryTag:
                        if category.hasAttribute("android:name"):
                            if "android.intent.category.LAUNCHER" in category.attributes["android:name"].value:
                                activityName = activity.attributes["android:name"].value
                                launcherActivity=((activityName.split(".")[-1:])[0])
                                return(find_all(launcherActivity+".smali",outputdirectory))
                                


def SmaliInjection(mainactivity):
    with open(mainactivity,'r') as smalifile:
        smalicontent=smalifile.readlines()
    Flag=False
    for line in smalicontent:
        if "# direct methods" in line:
            smalicontent[smalicontent.index(line)+2] = smalicontent[smalicontent.index(line)+2].replace('0','1')
            smalicontent[smalicontent.index(line)+3] = '\n    const-string v0, "frida-gadget"\n    invoke-static {v0}, Ljava/lang/System;->loadLibrary(Ljava/lang/String;)V\n'
            Flag = True
            break
    with open(mainactivity, 'w') as f:
        f.writelines(smalicontent) 
    if Flag:
        print('Direct Method Found and Smali injected in '+mainactivity)
    else:
        print("No Direct method found")

def copygadget():
    isgadgetdir=os.path.isdir('gadget')
    if (isgadgetdir==False):
        print("Downloading Latest Gadget")
        os.mkdir('gadget')
        for a in archdata:
            download_gadget(a)
    
    isdir = os.path.isdir(outputdirectory+'/lib')
    if isdir==True:
        arch=subprocess.check_output('ls '+outputdirectory+'/lib/',shell=True)
        arch_name=arch.decode("utf-8").rstrip()
        if arch_name in abislist:
            print("copying the architecture  "+arch_name)
            if arch_name=="armeabi-v7a":
                copyfile("gadget/arm/libfrida-gadget.so",Path(outputdirectory+"/lib/"+arch_name+"/libfrida-gadget.so"))
            elif arch_name=="arm64-v8a":
                copyfile("gadget/arm64/libfrida-gadget.so",Path(outputdirectory+"/lib/"+arch_name+"/libfrida-gadget.so"))
            else:
                copyfile("gadget/"+arch_name+"/libfrida-gadget.so",Path(outputdirectory+"/lib/"+arch_name+"/libfrida-gadget.so"))

    else:
        print("No lib folder found adding lib folder")
        os.mkdir(outputdirectory+'/lib')
        while True:
            try:
                archinput=int(input("Select Mobile architecture \n1)All\n2)armeabi-v7a\n3)arm64-v8a\n4)x86\n5)x86_64\n  :-"))
                break
            except ValueError:
                print("Please enter Valid Integer")
        if(archinput==1):
            for i,j in zip(archdata,abislist):
                os.mkdir(outputdirectory+"/lib/"+j)
                copyfile("gadget/"+i+"/libfrida-gadget.so",Path(outputdirectory+"/lib/"+j+"/libfrida-gadget.so"))
        elif(archinput==2):
            os.mkdir(outputdirectory+"/lib/"+abislist[0])
            copyfile("gadget/arm/libfrida-gadget.so",Path(outputdirectory+"/lib/"+abislist[0]+"/libfrida-gadget.so"))
        elif(archinput==3):
            os.mkdir(outputdirectory+"/lib/"+abislist[1])
            copyfile("gadget/arm64/libfrida-gadget.so",Path(outputdirectory+"/lib/"+abislist[1]+"/libfrida-gadget.so"))
        elif(archinput==4):
            os.mkdir(outputdirectory+"/lib/"+abislist[2])
            copyfile("gadget/x86/libfrida-gadget.so",Path(outputdirectory+"/lib/"+abislist[2]+"/libfrida-gadget.so"))
        elif(archinput==5):
            os.mkdir(outputdirectory+"/lib/"+abislist[3])
            copyfile("gadget/x86_64/libfrida-gadget.so",Path(outputdirectory+"/lib/"+abislist[3]+"/libfrida-gadget.so"))

def find_all(name, path):
    #result = []
    for root, dirs, files in os.walk(path):
        if name in files:
            return (os.path.join(root, name))
    #return result

def Recompile_code():
    subprocess.call(['apktool','b',outputdirectory,'-o',new_apk_name])
    subprocess.call(['java','-jar','uber-apk-signer.jar','--apks',new_apk_name])

def download_gadget(arch):
    
    r = requests.get('https://github.com/frida/frida/releases/latest', allow_redirects=False)
    frida_latest_version=((r.headers['Location'].split("/")[-1:])[0])
    try:
        os.mkdir("gadget/"+arch)
    except OSError:
        print("arch  already present removing it")
        subprocess.call(["rm","gadget/"+arch+"/libfrida-gadget.so"])
    
    print("Downloading Architecture"+arch)
    url = 'https://github.com/frida/frida/releases/download/'+frida_latest_version+'/frida-gadget-'+frida_latest_version+'-android-'+arch+'.so.xz'
    wget.download(url, 'gadget/'+arch+'/libfrida-gadget.so.xz')
    subprocess.call(['unxz','gadget/'+arch+'/libfrida-gadget.so.xz'])

def install_apk():
    install_input=input(Fore.RED +" Do you want to install the APK please connect devices and press  y/yes   ")
    print(Style.RESET_ALL)
    if((install_input=="y")|(install_input=="yes")):
        devices=subprocess.check_output(['adb','devices','-l']).decode("utf-8")
        if "product" in devices:
            print("Devices is connected and installing the APK")
            subprocess.call(['adb','install',"new-aligned-debugSigned.apk"])
            print(" Copying the burp Certificate to local temp on device")
            subprocess.call(['adb','push',"cert-der.crt","/data/local/tmp/cert-der.crt"])
            input(Fore.RED +"   To Start Frida Server Open the application on device and press enter :-")
            print(Style.RESET_ALL)
            subprocess.call(["frida","--codeshare","pcipolloni/universal-android-ssl-pinning-bypass-with-frida","-U","Gadget"])
        else:
            print("please connect device")
            exit()

def inject_native():
    isdir = os.path.isdir(outputdirectory+'/lib')
    if isdir==True:
        isgadgetdir=os.path.isdir('gadget')
        if (isgadgetdir==False):
            print("Downloading Latest Gadget")
            os.mkdir('gadget')
            for a in archdata:
                download_gadget(a)
        arch=subprocess.check_output('ls '+outputdirectory+'/lib/',shell=True)
        arch_name=arch.decode("utf-8").rstrip()
        for i,j in zip(archdata,abislist):
            if(str(j)==str(arch_name)):
                print(i)
                copyfile("gadget/"+i+"/libfrida-gadget.so",Path(outputdirectory+"/lib/"+j+"/libfrida-gadget.so"))
                break
        allnativelib=os.listdir(outputdirectory+'/lib/'+arch_name)
        for lib in allnativelib:
            print(lib)
        
        selectedlib=input("Paste the name of  One of the Native Library to Inject Hope that the library is loaded early ")
        print("Injecting Into selected library  "+selectedlib)
        libnative = lief.parse(outputdirectory+'/lib/'+arch_name+'/'+selectedlib)
        libnative.add_library("libfrida-gadget.so")
        libnative.write(outputdirectory+'/lib/'+arch_name+'/'+selectedlib)
        subprocess.call(["readelf","-d",outputdirectory+"/lib/"+arch_name+"/"+selectedlib])

    else:
        print("No lib folder Can't Inject native library  ")
        exit()
   

def main():
    subprocess.call(['apktool','d',apk_name,'-o',outputdirectory,'-f'])
    subprocess.call(['apktool','empty-framework-dir'])
    print(method)
    if(int(method)==1):
            smali_path=getmainactivity()
            SmaliInjection(smali_path)
            copygadget()
            Recompile_code()
            install_apk()
    if(int(method)==2):
        inject_native()
        Recompile_code()
        install_apk()


if __name__=="__main__":
    main()


