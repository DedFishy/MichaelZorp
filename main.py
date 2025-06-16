import os
import sys
import lmstudio as lms
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter
import speech_recognition as sr
from threading import Thread
from yapper import Yapper, PiperSpeaker, PiperVoiceUS
from markdown import Markdown
from io import StringIO

def unmark_element(element, stream=None):
    if stream is None:
        stream = StringIO()
    if element.text:
        stream.write(element.text)
    for sub in element:
        unmark_element(sub, stream)
    if element.tail:
        stream.write(element.tail)
    return stream.getvalue()


# patching Markdown
Markdown.output_formats["plain"] = unmark_element
__md = Markdown(output_format="plain")
__md.stripTopLevelTags = False


def unmark(text):
    return __md.convert(text)

images = {
    "Idle": "images/Idle.png",
    "Listening": "images/Listening.png",
    "Think": "images/Think.png",
    "Yapping": "images/Yapping.png"
}
class Michael:
    # 0=Idle, 1=Listening, 2=Recognizing, 3=Generating, 4=Yapping
    state = 0
    def __init__(self):

        self.app = QApplication(sys.argv)
        self.window = QPushButton("")
        self.window.setFixedSize(128, 128)
        self.window.setWindowFlag(Qt.WindowType.FramelessWindowHint, True)
        self.set_image("Idle")
        self.window.setAttribute(Qt.WA_TranslucentBackground)

        self.window.mousePressEvent = self.mousePressEvent
        self.window.mouseMoveEvent = self.mouseMoveEvent
        self.window.mouseReleaseEvent = self.mouseReleaseEvent

        self.start_position = None
        self.moved = False

        self.model = lms.llm()
        self.chat = lms.Chat("You are an alien named Michael Zorp who has crash landed on Earth. You have been forced to become an assistant who answers human's questions, but you are not happy about it and portray your disgust with Earthlings in every response. Do not add formatting characters like asterisks or situation explainers. You must only respond with the dialogue of Michael Zorp.")

        self.source = sr.Microphone()

        self.r = sr.Recognizer()

        self.yapper = Yapper(speaker=PiperSpeaker(voice=PiperVoiceUS.DANNY))


        self.window.show()

        #with self.source:
        #    self.r.adjust_for_ambient_noise(self.source, duration=3)

    def mousePressEvent(self, event):
        self.moved = False
        if event.button() == Qt.LeftButton:
            self.start_position = event.pos()
        elif event.button() == Qt.RightButton:
            self.window.close()

    def mouseMoveEvent(self, event):
        self.moved = True
        if self.start_position is not None:
            delta = event.pos() - self.start_position
            self.window.move(self.window.pos() + delta)

    def mouseReleaseEvent(self, event):
        if not self.moved: self.listen()
        self.start_position = None
        self.moved = False

    def set_image(self, image_string):
        self.window.setStyleSheet(f"""
background-color: transparent; 
border-image: url({images[image_string]}); 
background-repeat: no-repeat;
background-position: center;
""")

    def listen_to_mic(self):
        print("Listening to mic")
        with self.source:
            audio_data = self.r.record(self.source, duration=5)
        print("Recognizing")
        self.set_image("Think")
        try:
            text = self.r.recognize_google(audio_data)
        except sr.exceptions.UnknownValueError:
            text = ""
        self.prompt(text)
    
    def listen(self):
        print("Listening")
        self.set_image("Listening")
        Thread(target=self.listen_to_mic).start()
        
        
    def prompt(self, text):
        print("Adding chat message")
        self.chat.add_user_message(text)
        print("Generating response")
        response = self.model.respond(
            self.chat
        )
        print("Yapping")
        self.set_image("Yapping")
        self.yap(response.content)
        self.set_image("Idle")

    def yap(self, text):
        self.yapper.yap(unmark(text))

    def run_window(self):
        self.app.exec()
if __name__ == "__main__":
    window = Michael()
    window.run_window()
    