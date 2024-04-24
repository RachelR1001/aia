# AI Interview Assistant

This is an AI interview assistant based on ChatGPT4 that asks users predefined questions, records their answers, and writes a summary of the interview at the end. 
![Xnip2024-04-25_03-28-31](https://github.com/RachelR1001/aia/assets/148432322/42dd1b4a-7789-4c79-ac19-866d191022f7)


## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Features](#features)

## Installation
```
├── asr.py #whisper
├── interview_assistant.py #Encapsulates the prompt project and data conversion required for the task
├── llm.py #general llm
├── main.py #main ui
├── sources #source files
├── summary #folder for generated summary files
├── test.wav
├── tts.py #tts
└── user_input.wav #recording file for user inputs
```

To get started with AI Assistant, follow these steps:
1. Clone this repository to your local machine:

```bash
git clone https://github.com/RachelR1001/aia.git
cd aia
```

2. Install the dependencies:
   - Install python3.10 or above version
   - Kivy: https://kivy.org/doc/stable/gettingstarted/installation.html
   - KivyMD: https://kivymd.readthedocs.io/en/latest/getting-started/
  
    
3. Configure environment variables:
```bash
open ~/.zshrc
```
add the following information at the end of the file:
  export AZURE_OPENAI_ENDPOINT="https://yourendpoint.openai.azure.com/"
  export AZURE_LLM_DEPLOY_ID="Your_LLM_Depoly_Id"
  export AZURE_WHISPER_DEPLOY_ID="Your_Whisper_Deploy_Idr"
  export AZURE_OPENAI_API_KEY="Your_Key"

```bash
source ~/.zshrc
```

4. Run the application:
```bash
python main.py
```


## Usage
1. Click “Start A New Interview" Button to start
   
![Xnip2024-04-25_03-28-31](https://github.com/RachelR1001/aia/assets/148432322/efaa0f13-8c0e-482a-a4d0-e122bfa1319a)

2. When the AI assistant has finished asking the question, the user can manually click the button to start recording the answer. You can also end recording early by manually clicking the button. Status and timers are displayed on the right side of the bottom bar
   
![Xnip2024-04-25_05-32-34](https://github.com/RachelR1001/aia/assets/148432322/28ce4ca8-2732-4913-bf88-a99aeea3a3f7)

3. Wait for the AI assistant to give feedback and follow-up questions, and continue the same operation until the interview is completed
   
![Xnip2024-04-25_05-32-41](https://github.com/RachelR1001/aia/assets/148432322/b1a0cac5-f020-4638-adfa-fc014c62cbdb)

4. Complete the interview, generate an interview summary and save it to a local folder
   
![Xnip2024-04-25_05-45-03](https://github.com/RachelR1001/aia/assets/148432322/33c10b0b-cd29-4cc6-a2a7-157367ee9793)

5. Summary

![Xnip2024-04-25_06-05-10](https://github.com/RachelR1001/aia/assets/148432322/a0088b9e-0cec-45df-b8a6-0bdb57345746)


## Features
- Voice Recognition: AI Assistant can accurately process voice commands.
- Voice dialogue communication: AI Assistant will ask questions via voice, and the user will also answer via voice
- Visualization: Question and reply text will be displayed visually on the interface. Various statuses during program execution will also be displayed on the interface.
- Encouraging feedback and intelligent questioning: AI Assistant will give positive feedback based on the user’s answers and determine whether to provide further questioning.
- Generate summary: After the interview is completed, a summary of the entire interview will be automatically generated and saved locally.
