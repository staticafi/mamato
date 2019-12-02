from time import time
import re, sys, os
import subprocess

from . dir import load_dir

def extractXmlLinks(email):
    links = []
    regex = re.compile(r'https://sv-comp.sosy-lab.org/\d{4}/.*\.xml.bz2')
    matches = regex.findall(email)
    if len(matches) == 0:
        err('Extracting result tables links failed')
    for match in matches:
        links.append(str(match))
    return links


def extractVerifierName(email):
    regex = re.compile(r'Please find below the (final|preliminary) results for verifier ([^,]+),')
    matches = regex.findall(email)

    if len(matches) == 0:
        err('Extracting verifier name failed.')

    return matches[0][1]

def extractLogfileLinks(email):
    links = []
    regex = re.compile(r'https://sv-comp.sosy-lab.org/\d{4}/.*\.logfiles.zip')
    matches = regex.findall(email)
    if len(matches) == 0:
        err('Extracting logfile zip links failed')
    for match in matches:
        links.append(str(match))
    return links

def readEmail(inStream):
    email = ''
    for line in inStream:
        email += line + '\n'

    return email

def download(url, directory):
    print('[INFO] curl -O ', url)
    proc = subprocess.run(['curl', '-O', url], cwd=directory)
    if proc.returncode != 0:
        raise Exception('failed to download {}'.format(url))

def prepare(verifier):
    dname = 'results/' + verifier + '_' + str(int(time()))
    os.makedirs(dname)
    return dname

def load_from_email(xmlparser, email, description, append_vers, allow_duplicates):
    print('Reading {}'.format(email))
    with open(email) as fEmail:
        text = readEmail(fEmail)
        verifier = extractVerifierName(text)
        xmlUrls = extractXmlLinks(text)
        logfileUrls = extractLogfileLinks(text)
    dirname = prepare(verifier)

    for xmlUrl in xmlUrls:
        download(xmlUrl, dirname)

    for logUrl in logfileUrls:
        download(logUrl, dirname)

    return load_dir(xmlparser, dirname, description, append_vers, allow_duplicates)

def load_svcomp(xmlparser, emails, description, append_vers, allow_duplicates):
    total = 0
    toolrun_ids = []
    outputs = []
    for email in emails:
        cnt, runs, outs = load_from_email(xmlparser, email, description, append_vers, allow_duplicates)
        total += cnt
        toolrun_ids.extend(runs)
        outputs.extend(outs)
    return total, toolrun_ids, outputs
