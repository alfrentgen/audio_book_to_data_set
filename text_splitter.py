import string
import re

class SentenceSplitter:
    def __init__(self) -> None:
        self.delimiters = '?!', '...', '\u2026', '.', '!', '?' #U+2026 - is UTF ellipse symbol.

    def replace_eols(self, text: str):
        '''remove word hyphenation at EOLs and EOLs'''
        text = re.sub(re.compile('-\n-'), '-', text) #remove dashed-word hyphenation
        text = re.sub(re.compile('-\n'), '', text) #remove word hyphenation
        return re.sub(re.compile('[\n\t\r]'), ' ', text) # remove EOLS

    def split_into_sentences(self, text: str):
        '''split retaining delimeters in separate items'''
        pattern = '(' + '|'.join(map(re.escape, self.delimiters)) + ')'
        return re.split(pattern, text)

    def remove_punctuation(self, sentence: str, retain_punc=[',', '-']):
        '''remove all the punctuation besides "," and "-"'''
        punct = string.punctuation
        for rp in retain_punc:
            punct = punct.replace(rp, '')
        sentence = sentence.translate(str.maketrans('', '', punct))
        return re.sub(re.compile(' - | -\b'), ' ', sentence) # remove punctuation hypens

    def cleanup_sentence(self, sentence: str):
        '''remove excessive spaces and littering characters'''
        for pattern, sub in ('[^\w\\-\s,]*', ''), ('^\s*|\s*$', ''), ('\s*,', ','), ('\s{2,}', ' '):
            sentence = re.sub(re.compile(pattern), sub, sentence)
        return sentence

    def tokenize_text(self, text: str):
        '''produces a list of dicts {'body' : text, 'stopper' : sentence_stopper}'''
        text = self.replace_eols(text)
        sentences = self.split_into_sentences(text)
        for i in range(0, len(sentences)):
            s = sentences[i]
            if s in self.delimiters:
                continue
            s = self.remove_punctuation(s)
            s = self.cleanup_sentence(s)
            sentences[i] = s

        if sentences[0] in [self.delimiters]:
            sentences = sentences[1:]
        if sentences[-1] not in [self.delimiters]:
            sentences.append('.')
    
        assert(len(sentences) % 2 == 0)

        sentence_tuples = []        
        for i in range(0, len(sentences), 2):
            if not re.match('^\s*$', sentences[i]): # omit empty sentences
                sentence_tuples.append({'body' : sentences[i], 'stopper' : sentences[i+1]})

        return sentence_tuples


def __main__():
    input_file = r'/media/alf/storage1/ml/voice/data_pile/books/Stajery.txt'
    splitter = SentenceSplitter()
    with open(input_file, 'rb') as f:
        text = f.read().decode()
        sentences = splitter.tokenize_text(text)
    print(sentences)
    for s in sentences:
        print(re.findall('[\w-]+', s['body']))
        print(s['stopper'])

#__main__()
