import sys
import json
import re

statement_reg = re.compile('^([○◆◎])(.*（.*）)　(.*)')
sentence_reg = re.compile('^　([^　].*)')

statements = []
statement = dict()
in_statement = False

kinds = {'○': 'non_topic', '◆': 'question', '◎': 'answer'}

line = sys.stdin.readline()
while line:
    line = line.rstrip()
    statement_result = re.match(statement_reg, line)
    sentence_result = re.match(sentence_reg, line)
    if statement_result:
        result = statement_result
        if bool(statement):
            statements.append(statement)
        statement = dict()
        statement['kind'] = kinds[result.group(1)]
        statement['speaker'] = result.group(2)
        statement['paragraphs'] = [[sent + '。' for sent in result.group(3).split('。') if sent != '']]
        in_statement = True
    elif sentence_result and in_statement:
        statement['paragraphs'] = statement['paragraphs'] + [[sent + '。' for sent in sentence_result.group(1).split('。') if sent != '']]
    else:
        in_statement = False
    line = sys.stdin.readline()

if bool(statement):
    statements.append(statement)

print(json.dumps({'statements': statements}))
