from kivy.config import Config
from kivy.metrics import dp

Config.set('graphics', 'width', '1400')
Config.set('graphics', 'height', '900')
from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.list import OneLineAvatarIconListItem, IconRightWidget, ImageLeftWidget, OneLineAvatarListItem
from queue import Queue
from datetime import datetime
from kivy.core.audio import SoundLoader
from kivy.graphics import Color, Rectangle
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.label import MDLabel
from kivy.uix.label import Label
from kivymd.uix.button import MDRaisedButton, MDIconButton
from kivy.utils import get_color_from_hex
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from scipy.io import wavfile
import sounddevice as sd
from threading import Thread
import threading
import numpy as np
import time
import subprocess
import os
import asyncio
import string
import random
from threading import Event



from tts import edgetts
from asr import transcribe
from interview_assistant import feedback_and_follow_up, summarize

KV = '''
BoxLayout:
    orientation: 'horizontal'
    # Left Side Menu
    MDBoxLayout:
        orientation: 'vertical'
        size_hint_x: 0.2
        spacing: 10
        padding: 10
        md_bg_color: get_color_from_hex('#333333')
        Image:
            size_hint_y: 0.1
            source: './sources/logo.png'
            size_hint: (1, 0.2)
        MDBoxLayout:
            size_hint_y: 0.7
            height: self.minimum_height
            padding: [0, 0, 0, 10]
            orientation: 'vertical'
            MDLabel:
                text: 'AI Interview Assistant'
                font_size: "24sp"
                bold: True
                size_hint_y: None
                align: 'top'
                halign: "center"
                theme_text_color: 'Custom'
                text_color: get_color_from_hex('#ffffff')
            MDLabel:
                text: 'This is an AI interview assistant for practice purposes. Please answer each question after the AI assistant finishes asking it, and limit your response time to 1 minute per question. After the interview, a summary of the interview will be generated for you.'
                halign: "auto"
                size_hint_y: 0.8
                align: 'top'
                theme_text_color: 'Custom'
                padding:[36,20]
                line_height: 1.5
                text_color: get_color_from_hex('#ffffff')
        MDRaisedButton:
            size_hint_y: None
            spacing: dp(20)
            height: 36
            text: 'Start Your Interview!'
            font_style: 'Subtitle2'
            pos_hint: {'center_x': 0.5, 'center_y': 0.5}
            margin_bottom: dp(20)
            on_release:
                app.reset_interview()
                app.start_interview()
        Widget:
            size_hint_y: 0.01  
    # Right Side Content Area
    BoxLayout:
        orientation: 'vertical'
        size_hint_x: 0.8
        ScrollView:
        MDBoxLayout:
            size_hint_y: 0.1
            do_scroll_x: False
            do_scroll_y: True
            GridLayout:
                id: chat_list
                cols: 1
                size_hint_y: None
                height: self.minimum_height
                spacing: 20
        # Recording and Timer Status
        MDBoxLayout:
            size_hint_y: 0.1
            orientation: 'horizontal'
            align_items: 'center'
            md_bg_color: get_color_from_hex('#efefef')
            padding: dp(20)
            spacing: dp(20)
            MDRaisedButton:
                id: start_button
                text: 'Start Recording'
                on_release: app.start_recording()
                size_hint_x: 0.3
                width: dp(200)
                # pos_hint: {'center_x': 0.5, 'center_y': 0.5}
                padding: [0, 0] 
            MDRaisedButton:
                id: stop_button
                text: 'Stop Recording'
                on_release: app.stop_recording()
                disabled: True
                size_hint_x: 0.3
                width: dp(200)
                # pos_hint: {'center_x': 0.5, 'center_y': 0.5}
                padding: [0, 0] 
            MDLabel:
                id: recording_status
                text: 'Ready'
                halign: 'center'
                bold: True
                size_hint_x: 0.1
                # padding: [20, 0, 0, 0]
            MDLabel:
                id: timer
                text: '00:00'
                halign: 'center'
                bold: True
                size_hint_x: 0.1
'''
class MyApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.questions = [
            "How long did it take you to complete this coding task (in months)?",
            "Can you outline the timeline of your work on this coding task? How much time was allocated to each sub-task?",
            "What were the main challenges you encountered for the coding task, and what lessons did you learn from them?",
            "How did you ensure the usability and aesthetic appeal of your application's interface? Can you share your design and implementation strategies?",
            "What steps did you take to maintain professional code quality and application appearance?",
            "Reflecting on your experience with this coding task, what are three key takeaways you would like to emphasize?",
            "What aspects of the coding task do you believe you handled well, and what tips can you offer based on your experience?"
            # Add more questions as required
        ]
        self.current_question_index = 0
        self.hist = []
        self.all_messages = []
        self.response_history = []
        self.audio_queue = Queue()
        self.is_playing = False
        self.stop_event = Event()

    def build(self):
        self.root = Builder.load_string(KV)
        self.title = 'AI Interview Assistant'
        return self.root

    def start_interview(self):
        self.ask_next_question()

    def reset_interview(self):
        self.root.ids.chat_list.clear_widgets()
        self.current_question_index = 0
        self.hist = []
        self.all_messages = []
        self.response_history = []
        self.root.ids.recording_status.text = 'Ready'
        self.root.ids.timer.text = '00:00'

        self.root.ids.start_button.disabled = False
        self.root.ids.stop_button.disabled = True

        if hasattr(self, 'recording_thread') and self.recording_thread.is_alive():
            self.recording_thread.join()
    def ask_next_question(self):
        if self.current_question_index < len(self.questions):
            question = self.questions[self.current_question_index]
            self.speak_and_display(question, "AI")
            self.current_question = question  # Store current question for later use
            # self.start_recording()

    def start_recording(self):
        self.root.ids.recording_status.text = 'Recording...'
        self.stop_event.clear()
        self.root.ids.start_button.disabled = True
        self.root.ids.stop_button.disabled = False
        self.timer_count = 60  # Adjust duration as needed for the interview
        self.update_timer()
        self.recording_thread = Thread(target=self.record_audio, args=(60, 'user_input.wav'))
        self.recording_thread.start()

    def stop_recording(self):
        self.root.ids.recording_status.text = 'Ready'
        self.root.ids.start_button.disabled = False
        self.root.ids.stop_button.disabled = True
        self.stop_event.set()
        if self.recording_thread.is_alive():
            self.recording_thread.join()
        self.timer_count = 0
        self.root.ids.recording_status.text = 'Processing...'
        self.root.ids.timer.text = ''
        Clock.unschedule(self.timer_event)


    def record_audio(self, duration, filename, samplerate=44100):
        frames = int(samplerate * duration)
        recording = np.zeros((frames, 1), dtype='int16')
        stream = sd.InputStream(samplerate=samplerate, channels=1, dtype='int16')
        with stream:
            ptr = 0
            while ptr < frames and not self.stop_event.is_set():
                remaining_frames = frames - ptr
                block_size = min(1024, remaining_frames)
                data, overflowed = stream.read(block_size)
                recording[ptr:ptr + block_size] = data
                ptr += block_size
        wavfile.write(filename, samplerate, recording[:ptr])
        Clock.schedule_once(lambda dt: self.transcribe_and_display(filename))

    def update_timer(self):
        if self.timer_count > 0:
            mins, secs = divmod(self.timer_count, 60)
            self.root.ids.timer.text = '{:02}:{:02}'.format(mins, secs)
            self.timer_count -= 1
            self.timer_event = Clock.schedule_once(lambda dt: self.update_timer(), 1)
        else:
            self.root.ids.recording_status.text = 'Processing...'
            self.root.ids.timer.text = ''
            Clock.unschedule(self.timer_event)

    def transcribe_and_display(self, file):
        response = transcribe(file)
        transcript = response.get('text', 'No transcription available.')
        self.add_chat_message(transcript, "User")
        self.process_interaction(self.current_question, transcript)

    def process_interaction(self, question, answer):
        inputs = self.hist + [question, answer]
        print(inputs)
        try:
            # Fetch results from the assistant
            feedback_and_followup, has_follow_up = feedback_and_follow_up(inputs)
            self.root.ids.recording_status.text = ''

            # Split the feedback_and_followup into feedback and potential follow-up question
            parts = feedback_and_followup.split('|||')
            feedback = parts[0] if len(parts) > 0 else "No feedback available."
            follow_up_question = parts[1] if len(parts) > 1 else ""

            # Display the feedback
            self.speak_and_display(feedback, "AI")

            # Check if there's a follow-up question (assuming follow-up existence is indicated by a non-empty string)
            if has_follow_up and follow_up_question:
                self.speak_and_display(follow_up_question, "AI")
                self.hist = inputs
                self.current_question = feedback_and_followup
            else:
                # Proceed to the next question if there's no follow-up or end interaction
                self.current_question_index += 1
                self.all_messages.append(self.hist + [feedback])
                self.hist = []
                time.sleep(15)
                if self.current_question_index < len(self.questions):
                    self.ask_next_question()
                else:
                    self.speak_and_display("Interview completed. Thank you.", "AI")
                    self.root.ids.recording_status.text = 'Generating Summary'
                    time.sleep(60)
                    summary = summarize(self.all_messages) # summary here
                    current_time = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

                    file_path = f'./summary/summary_{current_time}.md'
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)
                    with open(file_path, 'w') as w:
                        w.write(summary)
                    folder_path = os.path.abspath(os.path.dirname(file_path))
                    subprocess.run(['open', folder_path])
                    self.root.ids.recording_status.text = 'Finish!'

        except Exception as e:
            print(f"Error processing interaction: {e}")
            self.add_chat_message("Error processing feedback and follow-up.", "System")

    def speak_and_display(self, message, speaker):
        """Handle display and speech output."""
        self.add_chat_message(message, speaker)

        if speaker == "AI":
            # Run TTS in a separate thread and play immediately when ready
            threading.Thread(target=self.async_speak, args=(message,)).start()

    def async_speak(self, text):
        """Run TTS and enqueue audio when ready."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.generate_and_enqueue_audio(text))
        loop.close()

    async def generate_and_enqueue_audio(self, text):
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        random_id = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
        output_file = f"output_{timestamp}_{random_id}.wav"
        await edgetts(text, output_file)  # Generate TTS audio
        Clock.schedule_once(lambda dt: self.add_to_queue(output_file))  # Enqueue for playback
        
    def add_chat_message(self, message, speaker):
        Clock.schedule_once(lambda dt: self._add_chat_message(message, speaker))

    def _add_chat_message(self, message, speaker):
        box = BoxLayout(size_hint_y=None,  padding=[20, 5])
        box.bind(minimum_height=box.setter('height'))

        with box.canvas.before:
            Color(0.90, 0.90, 0.67, 1) if speaker == 'AI' else Color(0.67, 0.84, 0.9, 1)
            self.rect = Rectangle(size=box.size, pos=box.pos)

        box.bind(pos=self.update_rect, size=self.update_rect)

        label = MDLabel(
            text= 'AI Assistant: ' + message if speaker == 'AI' else 'User: ' + message,
            halign='left',
            theme_text_color='Secondary' if speaker == 'AI' else 'Primary',
            size_hint_x=0.9,
            size_hint_y=None,
            valign='middle',
            markup=True
        )
        label.text_size = (self.root.width * 0.8, None)
        label.bind(texture_size=self.adjust_label_height)

        if speaker == 'AI':
            box.add_widget(label)
            box.add_widget(MDLabel(size_hint_x=0.2))
        else:
            box.add_widget(MDLabel(size_hint_x=0.2))
            box.add_widget(label)

        self.root.ids.chat_list.add_widget(box, index=0)

    def adjust_label_height(self, instance, value):
        instance.height = max(100, instance.texture_size[1])
        instance.size_hint_y = None
    def update_rect(self, instance, value):
        instance.canvas.before.clear()
        with instance.canvas.before:
            Color(0.88, 0.88, 0.88, 1) if 'AI' in instance.children[-1].text else Color(0.67, 0.84, 0.9, 1)
            Rectangle(pos=instance.pos, size=instance.size)
    def play_sound(self, *args):
        """Play sound from the queue."""
        if not self.is_playing and not self.audio_queue.empty():
            filename = self.audio_queue.get()
            self.is_playing = True
            sound = SoundLoader.load(filename)
            if sound:
                sound.bind(on_stop=self.on_sound_stop)
                sound.play()
            else:
                print('Failed to load sound from', filename)
                self.is_playing = False
                self.play_sound()

    def on_sound_stop(self, instance):
        """Handle the end of an audio playback."""
        self.is_playing = False
        self.play_sound()  # Check if there's more to play

    def add_to_queue(self, filename):
        """Add an audio file to the queue and try to play it."""
        self.audio_queue.put(filename)
        self.play_sound()


if __name__ == '__main__':
    MyApp().run()
