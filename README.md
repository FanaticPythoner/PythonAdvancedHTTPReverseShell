# PythonAdvancedHTTPReverseShell
Advanced python HTTP reverse shell made for Hacking Competition purpose. I am not responsible of what you do with this tool or any consequence/damage that can occur if you use it for illegal purpose.

This reverse shell works on any network that have the port 80 open. That being said, It can be extremely usefull. It was tested in a closed network, not over the whole internet. However, It will work over the internet, all you have to do is change the variables values of ATTACKER_IP, ATTACKER_PORT (AttackerSide.py) and ATTACKER_IP_URL (VictimSide.py). More details below.

### Language: ### 

- Tested in Python 3.6, should work in all Python 3 version.

### Limitations: ###

- Obviously, this is HTTP protocol, meaning it is possible for someone to intercept the request and read them in plain text. I encoded every request except for file transfer with Base64, but I should either implement HTTPS or a custom encrypting algorithm combined with Base64 for optimal purpose.
               
- This reverse shell has no implemented persistancy. This is, however, not a major issue if you use this for Hacking competition purpose...

- It is in python, meaning that you need to compile it to be sure that it will execute on any machine, regardless if python is installed or not. It is simple to do, just Google it. But if you are reading this right now, you probably already know how.

### Table of Contents: ###
- [*Setting up*](https://github.com/FanaticPythoner/PythonAdvancedHTTPReverseShell#setting-up-)
  - [*Attacker side script*](https://github.com/FanaticPythoner/PythonAdvancedHTTPReverseShell#attacker-side-script)
  - [*Victim side script*](https://github.com/FanaticPythoner/PythonAdvancedHTTPReverseShell#victim-side-script)
- [*Commands*](https://github.com/FanaticPythoner/PythonAdvancedHTTPReverseShell#Commands-)
  - [*Remotely upload a file to the victim side -> upload::{FILE_TO_UPLOAD_PATH}*](https://github.com/FanaticPythoner/PythonAdvancedHTTPReverseShell#upload-command)
  - [*Change the remote working directory of the victim side -> cd::{PATH}*](https://github.com/FanaticPythoner/PythonAdvancedHTTPReverseShell#cd-command)
  - [*Download a remote file to the attacker side -> get::{FILE_TO_GET_PATH}*](https://github.com/FanaticPythoner/PythonAdvancedHTTPReverseShell#get-command)
  - [*Scan the ports of remote machine on the victim side -> scan::{IP_TO_SCAN}::{PORT_1},{PORT_2},{PORT_N}*](https://github.com/FanaticPythoner/PythonAdvancedHTTPReverseShell#scan-command)
  - [*Take a screenshot of the victim desktop -> screens*](https://github.com/FanaticPythoner/PythonAdvancedHTTPReverseShell#screens-command)
  
# Installation

- Download the repository

- Install the requirements for the attacker side in the requirements_(AttackerSide).txt file (pip install -r requirements_(AttackerSide).txt)

- If you decided not to compile the VictimSide.py script, install the requirements for the victim side on the remote machine with the requirements_(VictimSide).txt file (pip install -r requirements_(VictimSide).txt)

- Happy Hacking.


