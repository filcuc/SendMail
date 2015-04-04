# SendMail
Small python script that uses Google OAuth 2.0 authentication for sending email with your google account

#Requirements
* Python 3.4
* google-api-python-client-py3 1.2
* httplib2 0.9

The best way for testing this is to create virtualenv

```
virtualenv SendMail
source SendMail/bin/activate
pip install google-api-python-client-py3
python3 ./path/to/SendMail.py
```

#Usage
First create an application through [Google API Console](https://code.google.com/apis/console)
for obtaining the CLIENT_SECRET and CLIENT_ID to be used
inside the script.
After that you've to setup the oauth 2.0 credentials by typing 

```
sudo ./SendMail --setup
```

Finally you can start sending email by invoking

```
sudo ./SendMail \
--from 'from_email' \
--to 'to_email' \
--subject 'subject' \
--body 'body'
```
