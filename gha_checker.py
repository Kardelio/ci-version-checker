#!/usr/bin/env python3
import requests
import argparse
import subprocess
import itertools
import json
import re
import sys
import os
import base64

blue="\033[97;104m"
lin="\033[94m"
faded="\033[2m"
yell="\033[33m"
black="\033[30;107m"
reset="\033[0m"

class Entry:
    def __init__(self, file, value, lineNo):
        self.file = file
        self.value = value
        self.lineNo = int(lineNo)
        splitedValue = value.split("@")
        self.currentVersion = splitedValue[1].strip()
        self.justVersionNumber = re.sub(r'[a-zA-Z]',"",splitedValue[1].strip())
        self.splitVers=self.justVersionNumber.split(".")
        self.versionBits=len(self.splitVers)
        self.owner = splitedValue[0].split("/")[0].strip()
        self.repo = splitedValue[0].split("/")[1].strip()

def getNeededVersionBits(oldVersion, newerVersionFull):
    return newerVersionFull[:len(oldVersion)]

def needToUpdate(one, two):
    cleanedValue = re.sub(r'[a-zA-Z]',"",one.strip())
    split=cleanedValue.split(".")
    cleanedValueTwo = re.sub(r'[a-zA-Z]',"",two.strip())
    splitTwo=cleanedValueTwo.split(".")
    
    try:
        numericOne=list(map(int,split))
        numericTwo=list(map(int,splitTwo))
    except ValueError:
        return False
    currentResult=False
    for i in list(itertools.zip_longest(numericOne, numericTwo)):
        a, b=i
        if a != None and b != None:
            if a < b:
                currentResult=True
                break
    return currentResult

parser = argparse.ArgumentParser(
        prog='Github Actions Action Version Checker',
        description='Check the versions of the actions used in your .github/ dir',
        epilog='')

parser.add_argument("--replace", action="store_true", help="Add this flag to allow the script to automatically edit the file for you") 

args = parser.parse_args()

if(os.path.exists(".github") == True):
    USER=os.environ["GITHUB_USERNAME"]
    KEY=os.environ["GITHUB_API_KEY"]
    b64Key=base64.b64encode((USER+":"+KEY).encode("ascii")).decode("ascii")

    headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "Authorization": f"Basic {b64Key}"
            }

    res = subprocess.run(['/usr/bin/grep','-nr','uses','.github'], capture_output=True, text=True)
    lines=res.stdout.splitlines()
    out=[]

    for i in lines:
        file=i.split(":")[0]
        lineNo=i.split(":")[1].strip()
        value=i.split("uses:")[1]
        out.append(Entry(file.replace("\"","").strip(),value.replace("\"","").strip(),lineNo))

    for j in out:
        url=f"https://api.github.com/repos/{j.owner}/{j.repo}/releases"
        response = requests.get(url, headers=headers)
        newerVersion=response.json()[0]["name"]
        update=needToUpdate(j.currentVersion,newerVersion)
        if update == True:
            shortVersion=getNeededVersionBits(j.currentVersion, newerVersion)
            print(f"Action {blue}{j.value}{reset} in  file: {yell}{j.file}{reset} (@ line {j.lineNo}) can be updated to {black}{newerVersion} ({shortVersion}){reset}")
            if args.replace == True:
                fileToEdit = open(j.file, 'r') 
                fileLines = fileToEdit.readlines() 
                fileLines[j.lineNo - 1] = re.sub(r'@[\.a-zA-Z0-9]*',f"@{shortVersion}",fileLines[j.lineNo - 1])
                with open(j.file, 'w') as editting:
                    editting.writelines( fileLines )

else:
    print("No .github folder exists")
    sys.exit(1)
