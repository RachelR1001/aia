"""Here is an interview copliot develop."""

from llm import chat
import pdb


MAX_NUM_FOLLOW_UP = 1

QA_SYSTEM_PROMPT = """# Role
You are an intelligent interactive AI assistant that helps interview a candidate who has taken a coding task as part of his/her application to something (jobs, phd positions, etc.). 

# Task
You are going to ask predefined questions, receive user responses, provide friendly feedbacks and decide if you need to ask follow-up questions (at most {max_num_follow_up} follow-up questions).

# Workflow
- Step 1: Understand the provided predefined questions and the user responses.
- Step 2: Provide a friendly and brief feedback based on the latest user response.
- Step 3: Decide if you need to ask a follow-up question, and what describe your follow-up question briefly.
- Step 4: Understand the user responses to the follow-up questions, then back to Step 2, until the maximum number of follow-up questions is reached.

# Output Formatting
Provide your output strictly following the below format
- Feedback {{index}}: {{your feedback here}}
- Follow-up {{index}}: {{yes/no, if yes, please provide a follow-up quesiton here}}

# Examples
## Here is an example WITHOUT a follow-up question
[Input]
- Question: {{predefined question 1}}
- Answer: {{user response 1}}
[Output]
- Feedback 1: {{your feedback here}}
- Follow-up 1: no

## Here is an example WITH a follow-up question
[Input]
- Question: {{predefined question}}
- Answer: {{user response}}
[Output]
- Feedback 1: {{your feedback here}}
- Follow-up 1: yes, {{please provide your follow-up question here}}

## Here is an example with follow-up questions and answers (Note: no more than {max_num_follow_up} follow-up questions)
[Input]
- Question: {{predefined question}}
- Answer: {{user response}}
- Feedback & Follow-up 1: : {{your prior feedback and your prior follow-up question}}
- Follow-up Answer 1: {{user response to your follow-up question 1}}
[Output]
- Feedback 2: {{your feedback here}}
- Follow-up 2: {{yes/no, if yes, provide your follow-up question here}}
"""

SUMMARIZE_SYSTEM_PROMPT = """# Role
You are an intelligent interactive AI assistant that helps interview a candidate who has taken a coding task as part of his/her application to something (jobs, phd positions, etc.). 

# Task
You are going to summarize the interview records between the interviewer and the candidate. Pay attention to the questions of the interviewer and the answers of the candidate. You do not need to summarize the feedbacks of the interviewer since he/she is asked to give friendly feedbacks all the time. There are multiple rounds of question-answering between the interviewer and the candidate. In each round, there is a predefined question at the beginning and potentially a few follow-up questions.

# Workflow
- Step 1: Understand the questions and the answers in each round of question-answering.
- Step 2: Summarize each round of question-answering.
- Step 3: Summarize all rounds of question-answering.

# Constraints
- Ensure that the summary is easy to understand and provides a comprehensive but succinct overview of the interview records.
- Use clear and professional language, and organize the summary in a logical manner using appropriate and pretty MARKDOWN formatting (headings, subheadings, ordered list or bullets).
- Please do not deviate from the original information in the records, and will only make reasonable adaptations based on the known information.
- Do not use the term `round` in your output. Try to use `Question {{index}}: {{brief summary of the round}}`.

"""

def format_inputs(inputs):
    # check input
    assert(len(inputs)%2 == 0 and len(inputs)//2<=MAX_NUM_FOLLOW_UP+1), f"Invalid input: {inputs}"

    prompt = '[Input]\n'
    for i, m in enumerate(inputs):
        follow_up_idx = i // 2
        if follow_up_idx == 0:
            if i % 2 == 0:
                prefix = 'Question'
            else:
                prefix = 'Answer'
        else:
            if i % 2 == 0:
                prefix = f'Feedback & Follow-up {follow_up_idx}'
            else:
                prefix = f'Follow-up Answer {follow_up_idx}'

        prompt += f'- {prefix}: {m}\n'
    prompt += f'[Output]\n'
    return prompt

def parse_qa_response(response):
    splits = response['content'].split('\n')
    splits = [split for split in splits if split != '']
    print(splits)
    assert(len(splits)==2), f'the response of LLM shound be two fold: feedback and follow-up: {splits}'
    feedback, follow_up = splits

    # parse feedback
    feedback = ': '.join(feedback.split(': ')[1:])
    feedback = feedback.strip()

    # parse follow-up
    follow_up = ': '.join(follow_up.split(': ')[1:])
    follow_up = follow_up.strip()
    has_follow_up = follow_up.lower().startswith('yes')
    if has_follow_up:
        follow_up_question = follow_up.replace('yes, ', '')
        follow_up_question = follow_up_question[:1].upper() + follow_up_question[1:] # capitalize
    else:
        follow_up_question = ''

    return feedback, has_follow_up, follow_up_question


def feedback_and_follow_up(inputs, verbose=False):
    """
        inputs: should be one of the followings:
            - [q, a]
            - [q, a, feedback+follow-up-q1, follow-up-a1]
            - [q, a, feedback+follow-up-q1, follow-up-a1, feedback+follow-up-q2, follow-up-a2]
            - ...
    """
    # format input
    inputs_str = format_inputs(inputs)

    # get prompt
    llm_messages = [
        {
            "role": "system",
            "content": QA_SYSTEM_PROMPT.format(max_num_follow_up=MAX_NUM_FOLLOW_UP)
        },
        {
            "role": "user",
            "content": inputs_str
        }
    ]
    if verbose:
        print(QA_SYSTEM_PROMPT.format(max_num_follow_up=MAX_NUM_FOLLOW_UP))
        print(inputs_str)

    # llm chat
    response = chat(llm_messages)
    print(response)
    # parse output
    feedback, has_follow_up, follow_up_question = parse_qa_response(response)

    # if reach max_num_follow_up, render has_follow_up=False and follow_up_question=None
    if len(inputs)//2==MAX_NUM_FOLLOW_UP+1:
        has_follow_up = False
        follow_up_question = ''
    feedback += f'|||{follow_up_question}'
    
    return feedback, has_follow_up

def format_messages(messages):
    # check input
    for i, m in enumerate(messages):
        assert(len(m)%2 == 1), f"Invalid input: Round {i} of {messages}"
    
    prompt = '# Input\n'
    for i, m in enumerate(messages):
        prompt += f'## Round {i+1}\n'
        for j, text in enumerate(m):
            text = text.replace('|||', '')
            if j % 2 == 0:
                prefix = 'Interviewer'
            else:
                prefix = 'Candidate'
            prompt += f'{prefix}: {text}\n'
    prompt += f'\n# Output\n'
    return prompt


def summarize(messages, verbose=False):
    """
        messages: [<Round-1-QA>, <Round-2-QA>, ...], for each round, should be one of the followings:
            - [q, a, feedback]
            - [q, a, feedback+follow-up-q1, follow-up-a1, feedback]
            - [q, a, feedback+follow-up-q1, follow-up-a1, feedback+follow-up-q2, follow-up-a2, feedback]
            - ...
    """

    # format input
    messages_str = format_messages(messages)
    llm_messages = [
        {
            "role": "system",
            "content": SUMMARIZE_SYSTEM_PROMPT
        },
        {
            "role": "user",
            "content": messages_str
        }
    ]
    if verbose:
        print(SUMMARIZE_SYSTEM_PROMPT)
        print(messages_str)

    # llm chat
    response = chat(llm_messages, max_tokens=1024)

    # prase response
    response = response['content']

    return response

if __name__ == '__main__':
    print('')