import re
from text_splitter import SentenceSplitter

class SentenceMatcher:
    def __init__(self, min_word_len = 0) -> None:
        self.min_word_len = min_word_len

    def _sort_sentence_index(self, sentence_list):
        '''sort sentences in order of increasing length'''

        idx_len_dicts = []
        for i in range(0, len(sentence_list)):
            if len(sentence_list[i]) > self.min_word_len:
                idx_len_dicts.append((i, len(sentence_list[i])))
        idx_len_dicts.sort(key = lambda item: item[1], reverse=True)
        return idx_len_dicts

    @staticmethod
    def _find_sentence_positions(ref_sentence, recog_text):
        '''finds all subsequence occurencies'''

        positions = []
        for pos in range(0, max(0, len(recog_text) - (len(ref_sentence) - 1))):
            if ref_sentence == recog_text[pos:pos + len(ref_sentence)]:
                positions.append(pos)
        return positions

    @staticmethod
    def _check_sync(ref_sentence, recog_text):
        '''check if sentence occurs in the text'''
        pass
   
    def _get_sync(self, ref_sentences, recog_text):
        '''TODO: implement'''
        pass
        idxes = self._sort_sentence_index(self, ref_sentences)
        sync_idx = 0
        for i in idxes:
            index = i[0]
            if _check_sync(ref_sentences[index], ):
                sync_idx = index
                break
        return sync_idx
    
def __main__():
    input_file = r'/media/alf/storage1/ml/voice/data_pile/books/Stajery_cut.txt'
    splitter = SentenceSplitter()
    with open(input_file, 'rb') as f:
        text = f.read().decode()
        sentences = splitter.tokenize_text(text)

    word_lists = [re.findall('[\w\\-]+', s['body']) for s in sentences]
    matcher = SentenceMatcher(2)
    sen_idx = matcher._sort_sentence_index(word_lists)
    print(sen_idx)

    
    all_words = []
    for lst in word_lists:
        all_words = all_words + lst
    print(word_lists[3], all_words)
    print(matcher._find_sentence_positions(word_lists[3], all_words))

__main__()