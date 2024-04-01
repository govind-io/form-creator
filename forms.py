import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# Your OAuth 2.0 credentials
CLIENT_ID = ""
CLIENT_SECRET =""
ACCESS_TOKEN = ""
REFRESH_TOKEN =""

# The scopes for the Google Forms API
SCOPES = ['https://www.googleapis.com/auth/forms.body']

# Assuming you have these credentials set up
credentials = Credentials(
    token=ACCESS_TOKEN,
    refresh_token=REFRESH_TOKEN,
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    token_uri='https://oauth2.googleapis.com/token',
    scopes=['https://www.googleapis.com/auth/forms.body']
)


# Build the service object
service = build('forms', 'v1', credentials=credentials)

# Create the form with only the title
form = {
    'info': {
        'title': 'Test Quiz',
    }
}

form_response = service.forms().create(body=form).execute()

form_id = form_response['formId']

print(f'Form created: {form_id}')

# Load your questions from a JSON file
with open('questions.json', 'r') as f:
    data = json.load(f)

# Prepare the requests for batchUpdate to add questions
requests = [{
            "updateSettings": {
                "settings": {"quizSettings": {"isQuiz": True}},
                "updateMask": "quizSettings.isQuiz",
            }
        }]

batch_update_settings={"includeFormInResponse": False,'requests': requests}

service.forms().batchUpdate(formId=form_id, body=batch_update_settings).execute()

requests=[]

for question in data['questions']:
    requests.append({
        'createItem': {
            'item': {
                'title': question['question'],
                'questionItem': {
                    'question': {
                        'required': False,
                        "grading": {
                "pointValue": 2,
                "correctAnswers": {
                    "answers": [{"value":question['answer'] }]
                },
                "whenRight": {"text": "You got it!"},
                "whenWrong": {"text": "Sorry, that's wrong"}
            },
                        'choiceQuestion': {
                            'type': 'RADIO',
                             'options': [{'value': option} for option in question['options']],
                            'shuffle': True
                        }
                    }
                } 
            },
            'location': {
                'index': 0
            }
        }
    })

# Execute batchUpdate to add the questions
batch_update_body = {"includeFormInResponse": False,'requests': requests}
service.forms().batchUpdate(formId=form_id, body=batch_update_body).execute()

print('Questions added to the form.')