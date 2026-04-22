# # AI-powered coop outreach automation pipeline

This project is an AI-powered automation pipeline that helps a student search for coop training opportunities and prepare outreach emails automatically.

The idea of the project is simple:
the program reads the user CV, reads a list of companies from a CSV file, evaluates which companies are more related to the user skills, searches for a public contact email, generates a short Arabic email, then sends it using Gmail API.

## Project structure

The project currently consists of three main classes:

1. **Agents**  
   This class is responsible for initializing the AI agent used in the project, which is Gemini in this case.

2. **DataPrepare**  
   This class is responsible for preparing the data needed in the workflow.  
   It handles:
   - extracting user information from the CV
   - reading company data from CSV
   - validating company relevance to the user profile
   - searching for company contact emails
   - generating the email body

3. **EmailService**  
   This class is responsible for Gmail authentication and sending emails based on the generated data from the `DataPrepare` instance.

## Workflow

The current workflow of the project is:

1. Initialize the Gemini agent
2. Extract the main user data from the CV
3. Load companies data from CSV
4. Evaluate which companies are more suitable for the user skills
5. Search for a likely public contact email
6. Generate a short Arabic outreach email
7. Send the email using Gmail API

## Sequence Diagram

This diagram shows the main workflow of the current version of the project, including CV extraction, company validation, email generation, and Gmail sending.

[Sequence Diagram](https://drive.google.com/file/d/1CDqrUCprsgtjVJf66gMqL_4u2E04uvVL/view?usp=sharing)

## Current limitations

The project is still under development, and currently has some limitations:

- it does not handle errors well yet
- it does not support all file encodings
- it does not support all file mime types
- generated results still depend on the quality of public data and AI output
- the workflow still needs more validation before being considered reliable for full automation

## Future updates

Planned future updates include:

1. Allow the program to accept data from more file mime types
2. Allow the user to upload the CV in more mime types
3. Allow the AI agent to search for opportunities from more sources such as LinkedIn and other job platforms
4. Improve the workflow to become more agentic and more practical
5. Add response tracking for sent applications
6. Add a status system such as:
   - rejected
   - no response
   - accepted
7. Avoid resending to the same company unless the user updates the CV
8. Notify the user by email when there is an important response or status update

## Notes

This project is mainly a learning project that focuses on:
- AI integration
- workflow automation
- API usage
- practical software design

It is being built step by step, and more improvements will be added over time.
