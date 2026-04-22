from env import GEMINI_API_KEY, URL #this is another file where all the secrets should be writtin, it is not neccesary to use this method but more secure espically when you want to upload the script to public AND (make sure you dont upload env.py)
from AIAgents import Agents
from DataPrepare import DataPrepare
from EmailService import EmailService
import sys
from pathlib import Path
import json
def main():
    casheData = 'src/dataCache.json'
    agent = Agents(API_KEY=GEMINI_API_KEY) #init gemini agent instance
    data = DataPrepare(agent) #init dataPrepare instance
    email = EmailService() #init emailService instance
    email.login(client_secret_file='src/client_secret.json')
    cv = data.extract_CV('src/CV.pdf')
    if not Path(casheData).exists():
        companiesData = data.read_data(url=URL)
        emailsdata = data.run(cvData=cv, companies=companiesData)
        with open('src/dataCache.json', 'w') as logging:
            json.dumps(emailsdata, logging, ensure_ascii=False, indent=2)
    else:
        with open(casheData, 'r', encoding='utf-8') as logging:
            emailsdata = json.load(logging)
    if not emailsdata:
        sys.exit("No valid emails were found")
    email.sendMail(mailData=emailsdata, CV='src/CV.pdf') #In this step of the program we start to see EmailService instance depend on the login step and the result of DataPrepare instance
if __name__ == "__main__":
    main()