# NLP-Sentimental-Analysis
Sentimental analysis of messages gathered from gmail and whatsapp

This is a unsupervised model for sentiment analysis of chats gathered from gmail and whatsapp in realtime
having three emotions positive,neutral and negative with a score 0 to 1(+ve),0 to 0(neutral),and 0 to -1(-ve)


How to use->>

Step 1: Set Up a Project in Google Cloud Console

Go to the Google Cloud Console.
Click on the project dropdown in the top bar and select "New Project."
Enter a name for your project and click "Create."

Step 2: Enable the Gmail API

In the Google Cloud Console, navigate to the "APIs & Services" > "Dashboard."
Click on the "+ ENABLE APIS AND SERVICES" button.
Search for "Gmail API" and select it from the results.
Click on the "Enable" button.

Step 3: Create Credentials

In the Google Cloud Console, navigate to "APIs & Services" > "Credentials."
Click on the "Create Credentials" button and choose "OAuth client ID."
Select "Desktop App" as the application type.
Enter a name for your client ID and click "Create."
A dialog will appear displaying the client ID and client secret. Click "OK."
Find your newly created OAuth 2.0 client ID in the "OAuth 2.0 Client IDs" section.
Click the download icon to download the JSON file containing your client ID and client secret. This file is your credentials file.

Step 4: Use the Credentials in Your Code

def authenticate_gmail_api():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json')

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return creds



Note:-Make sure to replace 'path/to/your/credentials.json' with the actual path to your downloaded credentials file.

:->>install python in your system
install pip
now install these libraries using pip

pip install selenium 
pip install bs4
pip install google.oauth2.credentials
pip install google_auth_oauthlib.flow
pip install googleapiclient.discovery
pip install requests
pip install google.auth.transport.requests
pip install re
pip install matplotlib
pip install numpy

once installed execute the overall code in any suitable ide of python 
recommended is IDLE of python default

NOW YOU WILL GET THE OVERALL RESULT IN AN OUTPUT FOLDER
