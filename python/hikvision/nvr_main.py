import sys
import argparse
import datetime
from callbackhandler import CallbackHandler

log = None

nvr = None
nvr_ip = ''
user = ''
password = ''

nvr_handler = None
event_manager = None

def get_current_timestamp() -> str:
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")

def validate(argv) -> bool:
    help = "{0} -n <http://nvr ip> -u <user> -p <password>".format(argv[0])
    
    parser = argparse.ArgumentParser()

    parser.add_argument('-n', dest='nvr_ip', help='NVR IP')
    parser.add_argument('-u', dest='user', help='username')
    parser.add_argument('-p', dest='password', help='password')
    args = parser.parse_args()

    if not all([args.nvr_ip, args.user, args.password]):
        parser.error('Missing required options')
    
    global nvr_ip
    global user
    global password
    nvr_ip = args.nvr_ip
    password = args.password
    user = args.user

    return True

def main():
    handler = CallbackHandler(nvr_ip, user, password)
    handler.go()

if __name__ == "__main__":
    if validate(sys.argv):
        main()

