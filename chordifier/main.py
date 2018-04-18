import kivy
kivy.require('1.0.8')

from kivy.config import Config
Config.set('graphics', 'resizable', False)
Config.set('graphics', 'width', '1920')
Config.set('graphics', 'height', '1080')

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.core.audio import SoundLoader
from kivy.graphics import *
from kivy.core.window import Window
from kivy.properties import StringProperty, ObjectProperty, NumericProperty
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg

from glob import glob
from os.path import dirname, join, basename
import librosa
import librosa.display
import numpy as np
import matplotlib.pyplot as plt


WINDOW_SIZE = 2048
WINDOW_STRIDE = WINDOW_SIZE
N_MELS = 128

MEL_KWARGS = {
    'n_fft': WINDOW_SIZE,
    'hop_length': WINDOW_STRIDE,
    'n_mels': N_MELS
}

class CursorBar(Widget):

    def __init__(self, sound):
        super().__init__()

        self.sound = sound
        
        with self.canvas:
            Color(1.0, 0.0, 0.0)
            # 3 - 1915            
            self.cursor = Rectangle(pos = (3,0), size = (2,900))
            Clock.schedule_interval(self.timer_callback, 0.5)

    def timer_callback(self, dt):
        self.cursor.pos = ((self.sound.get_pos() / self.sound.length) * (1912) + 3, 0)

class ChordifierCanvas(FloatLayout):

    def __init__(self, plt, sound):
        super().__init__()
        figureLayout = FigureCanvasKivyAgg(figure=plt)        
        self.add_widget(figureLayout)
        self.add_widget(CursorBar(sound))        

class AudioButton(Button):

    filename = StringProperty(None)
    sound = ObjectProperty(None, allownone=True)
    volume = NumericProperty(1.0)
    mel_spec = ObjectProperty(None, allownone=True)

    def on_press(self):
        if self.sound is None:
            self.sound = SoundLoader.load(self.filename)
            y, sr = librosa.load(self.filename, mono=True)
            print(sr)
            S = librosa.feature.melspectrogram(y=y, sr=sr, **MEL_KWARGS)
            librosa.display.specshow(
                librosa.power_to_db(S, ref=np.max),
                sr=sr,
                hop_length=WINDOW_STRIDE,
                y_axis='mel', 
                fmax=512,
                x_axis='time')
            plt.title('Mel spectrogram')
            plt.tight_layout()
            chordCanvasWidget = ChordifierCanvas(plt.gcf())
            self.mel_spec.add_widget(chordCanvasWidget)
            
            #features = librosa.feature.melspectrogram(new_input, **MEL_KWARGS)
            #print(features)
        # stop the sound if it's currently playing
        if self.sound.status != 'stop':
            self.sound.stop()
        self.sound.volume = self.volume
        self.sound.play()

    def release_audio(self):
        if self.sound:
            self.sound.stop()
            self.sound.unload()
            self.sound = None

    def set_volume(self, volume):
        self.volume = volume
        if self.sound:
            self.sound.volume = volume

class AudioBackground(FloatLayout):
    pass

class ChordifierApp(App):

    def build(self):
        root = AudioBackground()

        filename = "M:\songs\Zedd Maren Morris Grey-The Middle.wav"
        filename = "M:\songs\\'N Sync-God Must Have Spent a Little More Time on You.wav"


        root.ids.song_name.title = 'God Must Have Spent a Little More Time on You'

        self.sound = SoundLoader.load(filename)
        
        y, sr = librosa.load(filename, mono=True)
        print(sr)
        S = librosa.feature.melspectrogram(y=y, sr=sr, **MEL_KWARGS)

        plt.figure(figsize=(85,20))

        librosa.display.specshow(
            librosa.power_to_db(S, ref=np.max),
            sr=sr,
            hop_length=WINDOW_STRIDE,
            y_axis='off', 
            fmax=256,
            x_axis=None)
            
        plt.tight_layout()
        #plt.savefig("testing.png")
        chordCanvasWidget = ChordifierCanvas(plt.gcf(), self.sound)
        root.ids.mel_spec.add_widget(chordCanvasWidget)

        self.sound.play()
        
        #for fn in glob(join('M:\songs', '*.wav')):
        #    btn = AudioButton(
        #        text=basename(fn[:-4]).replace('_', ' '), filename=fn,
        #        size_hint=(None, None), halign='center',
        #        size=(128, 50), text_size=(118, None))
        #    root.ids.sl.add_widget(btn)
        #    btn.mel_spec = root.ids.mel_spec
        
        return root

    def release_audio(self):
        for audiobutton in self.root.ids.sl.children:
            audiobutton.release_audio()

    def set_volume(self, value):
        for audiobutton in self.root.ids.sl.children:
            audiobutton.set_volume(value)


if __name__ == '__main__':
    ChordifierApp().run()
