from pathlib import Path
import base64
from email.message import EmailMessage
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

class EmailService:
    def __init__(self):
        self.service = None

    def login(self, client_secret_file):
        path = Path(client_secret_file)
        flow = InstalledAppFlow.from_client_secrets_file(
            path,
            ["https://www.googleapis.com/auth/gmail.send"]
        )
        creds = flow.run_local_server( #Starting a local server to listen to the login process in localhost
            host='localhost',
            port=8080,
            authorization_prompt_message="browser will open automatically for authorization",
            success_message="Login succesful, you can close this page",
            open_browser=True,
            )
        
        self.service = build("gmail", "v1", credentials=creds)

    def __constructEmail(self, email, body, CV = None):
        if not self.service:
            raise RuntimeError("You must call login() first.")
        try:
            subject = "Coop training"
            message = EmailMessage()
            message.set_content(body)
            message['To'] = email
            message["Subject"] = subject
            
            if CV is not None:
                CVPath = Path(CV)
                if not CVPath.exists():
                    raise FileNotFoundError("CV file is not found plesae make sure you uploaded the file")
                with open(CVPath, 'rb') as CVFile:
                    message.add_attachment(
                        CVFile.read(),
                        maintype='application',
                        subtype='pdf',
                        filename=CVPath.name
                        )

            return base64.urlsafe_b64encode(message.as_bytes()).decode()          
        except Exception as e:
            raise RuntimeError(f"Error while making draft of the email {e}")
        
    def sendMail(self, mailData, CV = None):
        try:
            for mail in mailData:
                email = mail['Company Email']
                body = mail['Company Body']
                if not email: #I was wondering how Python would deal with JSON null since null is not a Python keyword, then I found out json.loads() converts it to None
                    print(f"Email not found for {mail['Company Name']}")
                    continue
                constructedMessage = self.__constructEmail(email=email, body=body, CV=CV)
                self.service.users().messages().send(userId="me", body={"raw": constructedMessage}).execute()
                print(f"Message sent to {mail['Company Email']}")
        except Exception as e:
            raise RuntimeError(f"Error while sending email {e}")
