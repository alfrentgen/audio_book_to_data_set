import re
from sentence_matcher import SentenceMatcher 
from text_splitter import SentenceSplitter
from speech_recognizer import SpeechRecognizer
import argparse

argparser = argparse.ArgumentParser()
argparser.add_argument('-t', '--txt', type=str, help='reference text', required=True)
argparser.add_argument('-w', '--wav', type=str, help='sound file to recognize', required=True)
argparser.add_argument('-m', '--mod', type=str, help='model path', required=False, default='models/vosk-model-ru-0.22')


def __main__():
    args = argparser.parse_args()
    txt_file = args.txt
    wav_file = args.wav
    model_path = args.mod
    
    # reference texеt sentece tokenizing section
    input_ref_file = txt_file
    splitter = SentenceSplitter()
    with open(input_ref_file, 'rb') as f:
        text = f.read().decode()
        ref_sents = splitter.tokenize_text(text)
    
    #print(ref_sentences)
    ref_sentences = [re.findall('[\w\\-]+', s['body']) for s in ref_sents]

    # speech recongnition section
    recognizer = SpeechRecognizer(model_path)
    audio_filename = wav_file
    rec_result = recognizer.recognize(audio_filename)
    rec_words = [rec_word['word'] for rec_word in rec_result['result']]

    matcher = SentenceMatcher()
    min_sentence_lenght = 0
    stat = matcher.indexRecSentences(ref_sentences, rec_words, min_sentence_lenght)

    
    #print(stat)
    for k, v in stat.items():
        ref_idx = v['ref_index']
        rec_pos = v['rec_positions'][0]
        start_word = rec_result['result'][rec_pos]
        start_pts = start_word['start']
        sent_len = len(v['ref_words'])
        end_word = rec_result['result'][rec_pos + sent_len - 1]
        end_pts = end_word['end']
        print(ref_sents[ref_idx[0]])
        print(f'{start_pts}-{end_pts}')
 
__main__()

