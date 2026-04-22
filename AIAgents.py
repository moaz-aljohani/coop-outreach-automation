from google import genai

class Agents: # why did i make the Agent initlization in a sipirit class ? because maybe i will need to add more AI functionality in the future, add a general gemini request function that could be used in any form to make the code shorter and less complicated
    def __new__(self, API_KEY):
        return genai.Client(api_key=API_KEY)
    