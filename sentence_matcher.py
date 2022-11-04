import re
from text_splitter import SentenceSplitter
from speech_recognizer import SpeechRecognizer

class SentenceMatcher:
    def __init__(self) -> None:
        pass

    def _sort_sentence_index_by_len(self, sentence_list, descending = True, min_word_len = 0):
        '''sort sentences in order of increasing length'''

        assert(min_word_len >= 0)
        idx_len_dicts = []
        for i in range(0, len(sentence_list)):
            sentence = sentence_list[i]

            if min_word_len == 0:
                sentence_len = len(sentence)
            else:
                sentence_len = 0
                for word in sentence:
                    if len(word) > min_word_len:
                        sentence_len += 1
 
            idx_len_dicts.append({"idx" : i, "len" : sentence_len})

        idx_len_dicts.sort(key = lambda item: item["len"], reverse=descending)
        return [item["idx"] for item in idx_len_dicts]

    @staticmethod
    def _find_sentence_positions(ref_sent_words, rec_text_words):
        '''finds all subsequence occurencies'''

        positions = []
        ref_sent_len = len(ref_sent_words)

        for pos in range(0, max(0, len(rec_text_words) - ref_sent_len + 1)):
            if ref_sent_words == rec_text_words[pos:pos + ref_sent_len]:
                positions.append(pos)

        return positions

    @staticmethod
    def _gather_text_stat(ref_sentences, rec_text_words):
        '''returns {sentence_text_lower_case : {'ref_words' : [...], 'ref_index' : [indeces_in_ref_text], 'rec_positions' : [positions_in_rec_text]}}'''

        sentence_stat = {}
        rec_text = [word.lower() for word in rec_text_words]
        ref_sentences = [[word.lower() for word in rs] for rs in ref_sentences]

        for ref_sent_idx in range(0, len(ref_sentences)):
            ref_sentence = ref_sentences[ref_sent_idx]
            ref_sentence_txt = ' '.join(ref_sentence)

            if ref_sentence_txt in sentence_stat:
                sentence_stat[ref_sentence_txt]["ref_index"].append(ref_sent_idx)
            else:
                positions = SentenceMatcher._find_sentence_positions(ref_sentence, rec_text)
                sentence_stat[ref_sentence_txt] = {"ref_words" : ref_sentence, 'ref_index' : [ref_sent_idx], 'rec_positions' : positions}

        return sentence_stat

    @staticmethod
    def indexRecSentences(reference_sentences, recognized_words, min_sent_length = 0):
        '''Rederence sentences are lists of strings, recognized text is a list of words.
        Returns ref sentence index in terms of words, e.g. '''

        stat = SentenceMatcher._gather_text_stat(reference_sentences, recognized_words)
        #print(stat)
        unique_sent_stat = { k : v for k, v in stat.items() if len(v['ref_index']) == 1 and len(v['rec_positions']) == 1 and len(v['ref_words']) >= min_sent_length}

        return unique_sent_stat

def __main__():
    #reference texеt sentece tokenizing section
    input_file = r'/media/alf/storage1/ml/voice/data_pile/books/Stajery_cut.txt'
    splitter = SentenceSplitter()
    with open(input_file, 'rb') as f:
        text = f.read().decode()
        ref_sentences = splitter.tokenize_text(text)

    ref_sentences = [re.findall('[\w\\-]+', s['body']) for s in ref_sentences]
    #print(ref_sentences)
    #exit(0)

    #speech recongnition section
    model_path = "models/vosk-model-ru-0.22"
    recognizer = SpeechRecognizer(model_path)
    filename = 'TraineesStrugRU.mp4_cut'
    audio_filename = '../data_pile/' + filename + '.wav'
    rec_result = recognizer.recognize(audio_filename)
#    exit(0)
    rec_words = [rec_word['word'] for rec_word in rec_result['result']]

    matcher = SentenceMatcher()
    min_sentence_lenght = 0
    stat = matcher.indexRecSentences(ref_sentences, rec_words, min_sentence_lenght)
    print(stat)
 
#__main__()

