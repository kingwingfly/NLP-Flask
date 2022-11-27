import os
import json


def parse(file_path):
    f = open(file_path, 'r', encoding='utf-8')
    dic = {}
    dic_save = {}
    for i in f:
        if i == '\n' and dic:
            dic_save |= {dic['Title-题名']: dic}
            dic = {}
            continue
        temp = (t.strip() for t in i.split(':'))
        label = next(temp)
        if label in [
            'SrcDatabase-来源库',
            'Title-题名',
            'Source-文献来源',
            'Summary-摘要',
            'PubTime-发表时间',
            'Year-年',
            'DOI-DOI',
        ]:
            dic[label] = ':'.join(temp)
        elif label in [
            'Author-作者',
            'Organ-单位',
        ]:
            dic[label] = next(temp).split(';')[:-1:]
        elif label in [
            'Keyword-关键词',
        ]:
            dic[label] = next(temp).split(';;')
    if dic:
        dic_save |= {dic['Title-题名']: dic}
    f.close()
    return dic_save

def save_result(result):
    f_save = open('./cnki_parser/output/output.json', 'w', encoding='utf-8')
    json.dump(result, f_save, ensure_ascii=False)

input_path = './cnki_parser/input'
dic_result = {}
for dirpath, _, filenames in os.walk(input_path):
    for filename in filenames:
        if not filename.endswith('.txt'):
            continue
        file_path = os.path.join(dirpath, filename)
        dic_result |= parse(file_path)
save_result(dic_result)
print('Finished!')