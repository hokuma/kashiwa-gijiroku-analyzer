import sys
import MeCab
import json

def convert_morph(morph):
    surface, rest = morph.split('\t')
    details = rest.split(',')
    pos = details[0]
    pos_sub = details[1]
    lemma = details[6]
    if lemma == '*':
        lemma = surface
    return {
        'base_form': lemma,
        'pos': pos,
        'pos_sub': pos_sub,
        'surface': surface
    }


def tokenize(sentence):
    morphs = tokenizer.parse(sentence.replace('　', '')).split('\n')
    return [convert_morph(morph) for morph in morphs if morph != 'EOS' and morph != '']


def tokenize_doc(doc):
    tokenized_doc = {'statements': []}
    for statement in doc['statements']:
        paragraphs = statement['paragraphs']
        statement['paragraphs'] = [
            [
                {
                    'raw': sentence,
                    'tokenized': tokenize(sentence)
                } for sentence in paragraph
            ] for paragraph in paragraphs
        ]
        tokenized_doc['statements'].append(statement)
    return tokenized_doc


tokenizer = MeCab.Tagger('mecabrc')
target_doc = json.loads(sys.stdin.read())
result = tokenize_doc(target_doc)
print(json.dumps(result))
