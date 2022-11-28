import json
from spider import run as spider_run

baike_path = 'spider_results/results.json'
cnki_path = 'cnki_parser/output/output.json'
cooperation_path = 'cooperation_analyse/output/output.json'

def load_data(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def cnki_extension(path):
    data = load_data(path)
    for type_ in ["Author-作者", "Organ-单位", "Keyword-关键词", "Keyword_of_abstract"]:
        info_extension(data,type_)

def info_extension(data,type_):
    gotten = []
    urls = {}
    for item in (item for info in data.values() for item in info.get(type_, [])):
        if item in gotten:
            continue
        gotten.append(item)
        url = f'https://baike.baidu.com/item/{item}?fromModule=lemma_search-box'
        urls[item] = url
    save_json(urls, type_)
    print(f"{type_} Finished!")


def save_json(data, type_):
    with open(f'./info_extension/output/{type_}.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)

if __name__ == '__main__':
    cnki_extension(path=cnki_path)
    print("Finished!")

