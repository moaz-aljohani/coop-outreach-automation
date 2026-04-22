import pandas
from google.genai import types
from pathlib import Path
import json

class DataPrepare:
    def __init__(self, agent):
        self.agent = agent


    def __load_data(self, url) -> pandas.DataFrame: #The double underscore at the beginning of the function name is used to make the method class-private by name mangling.
        data = pandas.read_csv(url) #we used pandas to load the file as csv, so i can manipulate it however i need later
        data = data.iloc[4:].reset_index(drop=True) #the first four rows are empty, so we start from the fifth column and resetting the index so it start from 1 not 5
        data.columns = ["Company Name", "Company Link"]
        return data

    def read_data(self, url) -> list: #The '->' in python functions does not do anything but it is useful to help team members to understand the code quicly
        loadData = self.__load_data(url)
        if loadData.empty:
            raise ValueError("The data is empty or not valid csv")
        else:
            companies = []
            for companyName, companyLink in zip(loadData['Company Name'], loadData['Company Link']):
                if pandas.notna(companyName) and pandas.notna(companyLink):
                    companies.append({ #putting the data of every company in dictionary {'company Name' and 'Company Link'} preparing it to the next stage
                        'Company Name': companyName,
                        'Company Link': companyLink
                    })
            return companies

    def extract_CV(self, CV) -> json:
        response = self.agent.models.generate_content(
            config = types.GenerateContentConfig( #Extracting the data from the CV to not read the cv everytime we call an Agent, we only extract the data one time and use it as string
                system_instruction="""
                Return JSON only with:
                {
                "name": "string",
                "skills": ["string"]
                }
                Max 5 skills.
                """,
            response_mime_type="application/json"
            ),
            contents=[
                types.Part.from_bytes(
                    mime_type='application/pdf',
                    data=Path(CV).read_bytes()
                )
            ],
            model='gemini-2.5-flash',
        ).text
        try:
            return json.loads(response)
        except Exception as e:
            raise ValueError(e)
        
    def __search_company(self, companyName, companyLink, CV) -> json:
        response = self.agent.models.generate_content(
            model="gemini-2.5-flash",
            config=types.GenerateContentConfig(
                temperature=0,
                tools=[types.Tool(google_search=types.GoogleSearch())],
                system_instruction="""You prepare a concise Arabic outreach email for a coop training opportunity.
                Rules:
                - Return valid JSON only.
                - Use formal Arabic.
                - Keep the message short and practical.
                - Start the email body with: "السلام عليكم"
                - Maximum 45 words in the email body.
                - No markdown.
                - No bullet points.
                - No exaggerated praise.
                - If no reliable contact email is found, set email to null.
                - Use only the candidate profile provided.

                Return exactly this JSON shape:
                {
                "email": string or null,
                "body": string,
                }
                """
                ),
            contents=[f"""Candidate profile:
                {json.dumps(CV)}

                Company name:
                {companyName}

                Company website:
                {companyLink}

                Task:
                Find the most likely public contact email for the company, if available.
                Then generate a short Arabic outreach email for coop training.
                Return JSON only.
                """]
        ).text
        cleaned = response.strip() #The reason of this cleaninig, is that google does not support json output with google search tool
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]

        cleaned = cleaned.strip()
        try:
            return json.loads(cleaned)
        except Exception:
            raise ValueError(f"Model did not return valid JSON: {response}")
        

    def __validateCompanies(self, data, CV) -> json:
        response = self.agent.models.generate_content(
            config=types.GenerateContentConfig(
                system_instruction="""
                    You are evaluating multiple companies.
                    Rules:
                    - Evaluate EACH company separately.
                    - Return a JSON array.
                    - Each item corresponds to the company in the same order.
                    - Rate from 0 to 100.
                    - Do not merge companies.
                    Use EXACT field names:
                        - rate
                        - company_domain
                    - Return JSON only.""",
                
                response_mime_type='application/json',
                response_json_schema= {
                    "type": "array",
                    "properties": {
                        #"relevant": {"type": "boolean"}, Why did i replace this field with rate? because the operation becomes so restricted for the agent as it outputs a boolean value, sometimes the company may relate somehow to the candidate skills but the Agent will assume it is not related because the general view of the company is not technical for example: Saudi Ministry of Tourism it has nothing technical more than a website so the Agent will assume it is not relevant, but deeply inside their system they need data analysis. 
                        'rate': {"type": "integer"},
                        "company_domain": {"type": "string"}
                    },
                    "required": ['rate', "company_domain"],
                    "additionalProperties": False
                }
            ),
            model='gemini-2.5-flash',
            contents=[
            f"""
                Candidate profile:
                {json.dumps(CV)}

                Companies:
                {json.dumps(data)}
                Return JSON only.
            """
            ]
        ).text
        
        return json.loads(response)
    
    def run(self, cvData, companies) -> list: #List of all companies that passed the validating process
        results = []
        for i in range(0, len(companies), 3): #The validation was 1 company each time in a for loop but i noticed it is so slow, i tried with two companies, still slow, tried 3, normal speed, tried with 4 and 5, it was faster each time but the output was not as accurate as required
            batch = companies[i:i+3]
            validation = self.__validateCompanies(data=batch, CV=cvData)
            
            for company, validate in zip(batch, validation):
                if validate["rate"] >= 60:
                        print(f"Validate {company['Company Name']} and started working on it")
                        search = self.__search_company(
                            company['Company Name'],
                            company['Company Link'],
                            CV=cvData
                        )
                        results.append({
                            'Company Name': company['Company Name'],
                            'Company Email': search['email'],
                            'Company Body' : search['body']
                        })
                else:
                    print(f"Skipped: {company['Company Name']}")
        return results