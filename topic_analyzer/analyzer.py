import sys
import re
import json
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer

def load_stop_words():
    stop_word_file = open('stopwords.txt', 'r')
    stop_words = []

    line = stop_word_file.readline()
    while line:
        line = line.rstrip('\r\n')
        stop_words.append(line)
        line = stop_word_file.readline()

    return stop_words


def top_words(component, feature_names, topn=10):
    sorted_idx = np.argsort(component)[:-topn - 1:-1]
    return [(feature_names[idx], component[idx].item()) for idx in sorted_idx if component[idx].item() > 0]


giin_seitou_map = {
        '柏清風': [
            '阿比留義顯',
            '石井昭一',
            '後藤浩一郎',
            '佐藤勝次郎',
            '助川忠弘',
            '円谷憲人',
            '日暮栄治',
            '古川隆史',
            '山内弘一',
            '山田一一',
            '山中一男'
        ],
        '公明党': [
            '小泉文子',
            '小松幸子',
            '田中晋',
            '塚本竜太郎',
            '中島俊',
            '橋口幸生',
            '林伸司'
        ],
        '日本共産党': [
            '日下みや子',
            '平野光一',
            '武藤美津江',
            '矢澤英雄',
            '渡部和子',
        ],
        '柏愛倶楽部': [
            '岡田智佳',
            '永野正敏',
            '山下洋輔',
            '吉田進'
        ],
        '市民サイド・ネット': [
            '林紗絵子',
            '松本寛道',
            '宮田清子'
        ],
        '護憲市民会議': [
            '末永康文',
            '本池奈美枝'
        ],
        '無所属': [
            '内田博紀',
            '上橋泉',
            '北村和之',
            '高松健太郎'
        ]
}

def find_party(name):
    for party, names in giin_seitou_map.items():
        if name in names:
            return party


def extract_noun(token):
    base_form = token['base_form']
    pos = token['pos']
    pos_sub = token['pos_sub']
    if pos != '名詞' or pos_sub == '非自立':
        return None
    else:
        return base_form


statements = {}

speaker_reg = re.compile('^(.*)（(.*)君）$')
seitou_reg = re.compile('(柏清風|公明党|日本共産党|柏愛倶楽部|市民サイド・ネット|護憲市民会議|無所属)')
number_noun_reg = re.compile('^\d+$')

stop_words = load_stop_words()
target_doc = json.loads(sys.stdin.read())
speaker_freq = dict()

for statement in target_doc['statements']:
    if statement['kind'] != 'question':
        continue

    speaker = statement['speaker']
    result = re.match(speaker_reg, speaker)
    speaker_name = result.group(2)
    if speaker_name in speaker_freq:
        speaker_freq[speaker_name] += 1
    else:
        speaker_freq[speaker_name] = 1
    
    words = []
    for paragraph in statement['paragraphs']:
        for sentence in paragraph:
            tokens = sentence['tokenized']
            nouns = [extract_noun(token) for token in tokens]
            words.extend([noun for noun in nouns if noun and number_noun_reg.match(noun) is None])

    if speaker_name in statements:
        statements[speaker_name].extend(words)
    else:
        statements[speaker_name] = words

docs = []
doc_names = []
for speaker_name in statements:
    docs.append(' '.join(statements[speaker_name]))
    doc_names.append(speaker_name)

#vectorizer = TfidfVectorizer(max_df=.95, min_df=2, stop_words=stop_words)
vectorizer = CountVectorizer(max_df=.95, min_df=2, stop_words=stop_words)
tfidf = vectorizer.fit_transform(docs)
top_words_for_giin = [top_words(tfidf[i].toarray().squeeze(), vectorizer.get_feature_names(), topn=200) for i in range(tfidf.shape[0])]

result = {}
for index, name in enumerate(doc_names):
    result[name] = {
            'name': name,
            'party': find_party(name),
            'count': speaker_freq[name],
            'tfidf': top_words_for_giin[index],
    }


print(json.dumps(result))
