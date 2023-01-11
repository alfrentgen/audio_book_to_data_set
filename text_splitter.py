import string
import regex as re

_ellipse = '\u2026'
_long_hyphen = '\u2014'

class SentenceSplitter:
    def __init__(self) -> None:
        self.stoppers = '?!', '...', _ellipse, '.', '!', '?'

    @staticmethod
    def _replace_eols(text: str):
        '''remove word hyphenation at EOLs and EOLs'''
        sub_function = lambda match_obj: None if match_obj.group(2) is None else match_obj.group(1) + '-' + match_obj.group(3)
        text = re.sub(re.compile('(\w)(\p{Pd}\n\p{Pd}?)(\w)'), sub_function, text) #remove word and dashed-word hyphenations
        return re.sub(re.compile('[\n\t\r]'), ' ', text) # remove EOLS

    def _split_into_sentences(self, text: str):
        '''split retaining delimeters in separate items'''
        pattern = '(' + '|'.join(map(re.escape, self.stoppers)) + ')'
        return re.split(pattern, text)

    @staticmethod
    def _cleanup_sentence(sentence: str):
        '''remove excessive spaces and littering characters, but retain some punctuation'''
        for pattern, sub in ('[\p{Zs}]', ' '), ('\p{Pd}+', '-'), ('[^\w\s\\-,:;`]*', ''),\
                            ('^\s*-*\s*|\s*$', ''),\
                            ('\s*,', ','), ('\s*:', ':'), ('\s*;', ';'), ('\s{2,}', ' '):
            sentence = re.sub(re.compile(pattern), sub, sentence)
        return sentence

    def split(self, text: str):
        '''produces a list of dicts {'body' : text, 'stopper' : sentence_stopper}'''
        text = self._replace_eols(text)
        sentences = self._split_into_sentences(text)
        for i in range(0, len(sentences)):
            s = sentences[i]
            if s in self.stoppers:
                continue
 
            s = self._cleanup_sentence(s)
            sentences[i] = s

        if sentences[0] in [self.stoppers]:
            sentences = sentences[1:]
        if sentences[-1] not in [self.stoppers]:
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
        sentences = splitter.split(text)
    print(sentences)
    for s in sentences:
        print(re.findall('[\w-]+', s['body']))
        print(s['stopper'])

#__main__()
