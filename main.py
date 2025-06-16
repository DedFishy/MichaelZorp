import os
import sys
import lmstudio as lms
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter
import speech_recognition as sr
import multiprocessing

images = {
    "Idle": "images/Idle.png",
    "Listening": "images/Listening.png",
    "Think": "images/Think.png"
}
class Michael:
    # 0=Idle, 1=Listening, 2=Recognizing, 3=Generating, 4=Yapping
    state = 0
    def __init__(self):

        self.app = QApplication(sys.argv)
        self.window = QPushButton("Michael Zorp")
        self.window.setFixedSize(200, 200)
        self.window.setWindowFlag(Qt.WindowType.FramelessWindowHint, True)
        self.set_image("Idle")
        self.window.setAttribute(Qt.WA_TranslucentBackground)

        self.window.mousePressEvent = self.mousePressEvent
        self.window.mouseMoveEvent = self.mouseMoveEvent
        self.window.mouseReleaseEvent = self.mouseReleaseEvent

        self.start_position = None

        self.source = sr.Microphone()

        self.r = sr.Recognizer()

        self.pool = multiprocessing.Pool(os.cpu_count())

        self.window.show()

        #with self.source:
        #    self.r.adjust_for_ambient_noise(self.source, duration=5)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.start_position = event.pos()
        elif event.button() == Qt.RightButton:
            self.window.close()

    def mouseMoveEvent(self, event):
        if self.start_position is not None:
            delta = event.pos() - self.start_position
            self.window.move(self.window.pos() + delta)

    def mouseReleaseEvent(self, event):
        self.start_position = None

    def set_image(self, image_string):
        self.window.setStyleSheet(f"""
background-color: transparent; 
border-image: url({images[image_string]}); 
background-repeat: no-repeat;
background-position: center;
""")

    def listen_to_mic(self):
        with self.source:
            audio_data = self.r.record(self.source, duration=5)
        print("Recognizing")
        self.set_image("Think")
        try:
            text = self.r.recognize_google(audio_data)
        except sr.exceptions.UnknownValueError:
            text = ""
        return text
    
    def listen(self):
        self.set_image("Listening")
        self.pool.apply_async(self.listen_to_mic, callback=self.prompt)
        
        
    def prompt(self, text):
        print(text)

    def run_window(self):
        self.app.exec()
if __name__ == "__main__":
    window = Michael()
    window.run_window()
    