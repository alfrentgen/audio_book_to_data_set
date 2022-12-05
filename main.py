import re
from sentence_matcher import SentenceMatcher 
from text_splitter import SentenceSplitter
from speech_recognizer import SpeechRecognizer
import argparse
import ffmpeg
from io import BytesIO, open
from os import path, mkdir
import wave
import json

argparser = argparse.ArgumentParser()
argparser.add_argument('-t', '--text', type=str, help='reference text', required=True)
argparser.add_argument('-s', '--stream', type=str, help='sound file to recognize', required=True)
argparser.add_argument('-m', '--model', type=str, help='model path', required=False, default='models/vosk-model-ru-0.22')
argparser.add_argument('-o', '--output', type=str, help='output directory', required=False, default='output')
argparser.add_argument('-lr', '--load_rec', type=str, help='a JSON file to load recognition results', required=False)
argparser.add_argument('-sr', '--save_rec', type=str, help='a JSON file to save recognition results', required=False)
argparser.add_argument('-b', '--begin_time', type=int, help='begin stream time', required=False)
argparser.add_argument('-e', '--end_time', type=int, help='end stream time', required=False)

def __main__():
    args = argparser.parse_args()
    args = vars(args)
    txt_file = args['text']
    stream_file = args['stream']
    model_path = args['model']
    output_dir = args['output']
    in_rec = args['load_rec']
    out_rec = args['save_rec']
    begin_time = args['begin_time']
    end_time = args['end_time']
    print(args)

    if not path.exists(output_dir):
        mkdir(output_dir)
    elif path.isfile(output_dir):
        print('Cannot create output directory.')
        exit(0)

    # reference texеt sentece tokenizing section
    input_ref_file = txt_file
    splitter = SentenceSplitter()
    with open(input_ref_file, 'rb') as f:
        text = f.read().decode()
        ref_sents = splitter.tokenize_text(text)
    
    #print(ref_sentences)
    ref_sentences = [re.findall('[\w\\-]+', s['body']) for s in ref_sents]

    #ffminput
    ffinput = ffmpeg.input(stream_file).audio
    if begin_time is not None or end_time is not None:
        ffinput = ffinput.filter('atrim', start = begin_time, end = end_time)
        
    wav_s16le_32k_mono, err = (ffinput.output('-', format='wav', acodec='pcm_s16le', ac=1, ar='32k')\
        .overwrite_output().run(capture_stdout=True))
    #print(f'Got {len(wav_s16le_32k_mono) - 44} bytes of 32k audio.')

    # recognizespeech recongnition section
    if in_rec:
        with open(in_rec, "r") as infile:
            rec_result = json.load(infile)
    else:
        process = (ffmpeg.input('pipe:').output('-', format='wav', acodec='pcm_s16le', ac=1, ar='16k')\
            .overwrite_output().run_async(pipe_stdin=True, pipe_stdout=True))
        wav_s16le_16k_mono, err = process.communicate(input=wav_s16le_32k_mono)
        process.wait()

        with BytesIO(wav_s16le_16k_mono) as wav_to_rec:
            recognizer = SpeechRecognizer(model_path)
            rec_result = recognizer.recognize(wav_to_rec)
        if out_rec:
            with open(path.join(output_dir, out_rec), "w") as outfile:
                json.dump(rec_result, outfile)

    rec_words = [rec_word['word'] for rec_word in rec_result['result']]
    
    #match sentences and recgnized text
    matcher = SentenceMatcher()
    min_sentence_length = 0
    stat = matcher.indexRecSentences(ref_sentences, rec_words, min_sentence_length)

    #input stream cutting and saving
    sentences_with_pts = []
    for k, v in stat.items():
        ref_idx = v['ref_index']
        rec_pos = v['rec_positions'][0]
        start_word = rec_result['result'][rec_pos]
        start_pts = start_word['start']
        sent_len = len(v['ref_words'])
        end_word = rec_result['result'][rec_pos + sent_len - 1]
        end_pts = end_word['end']
        sentences_with_pts.append((ref_sents[ref_idx[0]], start_pts, end_pts))

    with wave.open(BytesIO(wav_s16le_32k_mono), 'rb') as in_wav,\
    open(path.join(output_dir,'index.csv'), 'w', encoding='utf-8') as index_file:
        nchannels, sampwidth, framerate, nframes, comptype, compname = in_wav.getparams()
        for i in range(0, len(sentences_with_pts)):
            sentence, start_pts, end_pts = sentences_with_pts[i]
            sent_text = sentence['body'] + sentence['stopper']
            #cut and save a wav and write an index file entry
            file_name = f'{i}.wav'
            index_entry = '|'.join([file_name, sent_text])
            index_file.write(index_entry + '\n')
            start = int(start_pts * framerate)
            end = int(end_pts * framerate)
            in_wav.setpos(start)

            nframes = end - start
            data = in_wav.readframes(nframes)
            file_path = path.join(output_dir, file_name)
            with wave.open(file_path, 'wb') as out_wav:
                out_wav.setparams((nchannels, sampwidth, framerate, nframes, comptype, compname))
                out_wav.writeframes(data)
 
__main__()

