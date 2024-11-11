#!/usr/bin/env python3
import requests
import subprocess
import itertools
import json
import re
import sys
import os
import base64
import packaging.version #need Version

blue="\033[97;104m"
lin="\033[94m"
faded="\033[2m"
yell="\033[33m"
black="\033[30;107m"
reset="\033[0m"

class StepEntry:
    def __init__(self, name, version, lineNo):
        self.name = name
        self.version = version
        self.lineNo = lineNo

def sortVersions(cleanedSemVers):
    versions = cleanedSemVers
    versions.sort(key=packaging.version.Version)
    return versions

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

def cleanEntry(line, num):
    cleanA = line.strip()
    cleanB = cleanA.split(" ")
    cleanC = cleanB[1].replace(":","")
    cleanD = cleanC.split("@")
    name = cleanD[0]
    ver = cleanD[1]
    return StepEntry(name, ver, num)

if(os.path.isfile("bitrise.yml") == True):
    USER=os.environ["GITHUB_USERNAME"]
    KEY=os.environ["GITHUB_API_KEY"]
    b64Key=base64.b64encode((USER+":"+KEY).encode("ascii")).decode("ascii")

    headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "Authorization": f"Basic {b64Key}"
            }

    txtfile = open('bitrise.yml', 'r') 
    glines = txtfile.readlines() 

    out = []
    for idx, line in enumerate(glines):
        lineNumber = idx + 1
        if re.match(r'.* - [a-zA-Z-]*\@[0-9\.]*:.*', line):
            se = cleanEntry(line.replace("\n",""),lineNumber)
            out.append(se)

    for j in out:
        url=f"https://api.github.com/repos/bitrise-io/bitrise-steplib/contents/steps/{j.name}"

        response = requests.get(url, headers=headers)
        filtered = list(map(lambda a: a["name"] ,filter(lambda item: re.match(r'^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$',item["name"]), response.json())))

        sortedVers=sortVersions(filtered)
        newerVersion=sortedVers[-1]

        print(f"{faded}{j.name} => [{j.version}] (line: {j.lineNo}) versus {newerVersion}{reset}")
        update=needToUpdate(j.version,newerVersion)
        if update == True:
            print(f"Step {blue}{j.name}{reset} can be updated to {black}{newerVersion}{reset} -> {yell}on line {j.lineNo}{reset}")

else:
    print("No bitrise.yml file exists!")
    sys.exit(1)
