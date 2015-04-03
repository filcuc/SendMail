

import base64
from email.mime.text import MIMEText
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.file import Storage
from apiclient.discovery import build
import os.path
import httplib2
import sys
import argparse

CLIENT_ID = None # Put here your client id
CLIENT_SECRET = None # Put here your client secret
SCOPE = 'https://www.googleapis.com/auth/gmail.compose'
REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'
AUTH_URI = 'https://accounts.google.com/o/oauth2/auth'
TOKEN_URI = 'https://accounts.google.com/o/oauth2/token'


def parse_arguments():
    parser = argparse.ArgumentParser(prog='SendMail', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--config-path', help='Set script store path', action="store", default='/etc/SendMail')
    parser.add_argument('--setup', help='Setup the credentials', action="store_true")
    parser.add_argument('--from', help="The 'from' field of the email", dest='from_')
    parser.add_argument('--to', help="The 'to' field of the email")
    parser.add_argument('--subject', help="The 'subject' field of the email")
    parser.add_argument('--body', help="The 'body' field of the email ")
    parser.add_argument('-v', '--version', action='version', version='%(prog)s 0.0.1')
    return parser.parse_args()


def validate_arguments(args):
    if not os.path.exists(args.config_path):
        print('The config file directory ', args.config_path, "doesn't exists.")
        sys.exit(1)

    if not os.path.isdir(args.config_path):
        print('The config file ', args.config_path, ' is not a directory.')
        sys.exit(1)

    credential_filename = 'credentials.txt'
    credential_file_path = os.path.join(args.config_path, credential_filename)

    if not os.path.exists(credential_file_path) and not args.setup:
        print('The credential file ', credential_filename, ' in path ', credential_file_path, '.')
        print('Please re-run the script with the --setup option')
        sys.exit(1)


    if not args.setup:
        error_msg = "Missing %s argument. Type --help for further information"
        if not args.from_:
            print(error_msg % '--from')
            sys.exit(1)
        if not args.to:
            print(error_msg % '--to')
            sys.exit(1)
        if not args.subject:
            print(error_msg % '--subject')
            sys.exit(1)
        if not args.body:
            print(error_msg % '--body')
            sys.exit(1)

    return credential_file_path


def create_message(sender, to, subject, body):
    msg = MIMEText(body)
    msg['to'] = to
    msg['from'] = sender
    msg['subject'] = subject
    buffer = bytes(msg.as_string(), 'UTF-8')
    return {'raw': base64.urlsafe_b64encode(buffer).decode('UTF-8')}


def setup_credentials(credential_file_path):
    flow = OAuth2WebServerFlow(client_id=CLIENT_ID,
                               client_secret=CLIENT_SECRET,
                               scope=SCOPE,
                               redirect_uri=REDIRECT_URI,
                               auth_uri=AUTH_URI,
                               token_uri=TOKEN_URI)
    auth_uri = flow.step1_get_authorize_url()
    print("Authenticate here: ", auth_uri)
    code = input("Please paste the obtained code: ")
    credentials = flow.step2_exchange(code)
    save_credentials(credential_file_path, credentials)
    return credentials


def save_credentials(credential_file_path, credentials):
    storage = Storage(credential_file_path)
    storage.put(credentials)


def load_credentials(credential_file_path):
    storage = Storage(credential_file_path)
    return storage.get()


def send_message(service, user_id, body):
    service.users().messages().send(userId=user_id, body=body).execute()


def main():
    args = parse_arguments()
    credential_file_path = validate_arguments(args)
    if args.setup:
        credentials = setup_credentials(credential_file_path)
    else:
        credentials = load_credentials(credential_file_path)
    http = httplib2.Http()
    http = credentials.authorize(http)
    service = build('gmail', 'v1', http=http)
    message = create_message(args.from_, args.to, args.subject, args.body)
    send_message(service, "me", message)


if __name__ == '__main__':
    try:
        main()
        sys.exit(0)
    except Exception as e:
        print("An error occurred:", e)
        sys.exit(1)
