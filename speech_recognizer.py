import wave
import json

from vosk import Model, KaldiRecognizer

class SpeechRecognizer:
    def __init__(self, model_path) -> None:
        self.model = Model(model_path)

    def recognize(self, audio_filename, offset = 0, nframes = None):
        result = None
        with wave.open(audio_filename, "rb") as wf:
            assert(wf.getnchannels() == 1)
            wf.setpos(offset)
            nframes = wf.getnframes() if nframes == None else nframes
            rec = KaldiRecognizer(self.model, wf.getframerate())
            rec.SetWords(True)
            data = wf.readframes(nframes)
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
            rec.FinalResult()

        return result

def __main__():
    model_path = "models/vosk-model-ru-0.22"
    recognizer = SpeechRecognizer(model_path)
    filename = 'TraineesStrugRU.mp4_cut'
    audio_filename = '../data_pile/' + filename + '.wav'
    result = recognizer.recognize(audio_filename)

    with open(filename + '.json', 'w') as json_file:
        json.dump(result, json_file, ensure_ascii=False)

    text = result['text']
    assert(len(text) > 0), "Result text is empty!"

    with open(filename + '.txt', 'wb') as file:
        file.write(text.encode('utf-8'))

    exit(0)

__main__()