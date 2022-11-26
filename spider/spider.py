import httpx
import asyncio
import re
from parsel import Selector
from urllib import parse
import os
import json


class UrlsLoader():
    def __init__(self, urls: dict, batch_size):
        self.urls = list(urls.items())
        self.batch_size = batch_size
        self.cur = 0
        self.len = len(urls)

    def __iter__(self):
        while True:
            if self.cur + self.batch_size < self.len:
                yield (self.index_urls(self.cur + i)for i in range(self.batch_size))
            else:
                yield (self.index_urls(i) for i in range(self.cur, self.len))
                break
            self.cur += self.batch_size
    
    def index_urls(self, index_num):
        return self.urls[index_num]

def first_parse(t: str):
    try:
        t = t.replace('\xa0', '')
        t = t.replace('\n', '')
    except:
        pass
    return t.strip('\n')

def second_parse(values: list):
    pattern = re.compile(r'>([\w|\s|、|（|）|.|,|，|。|、|-]+?)<')
    results = []
    for i in values:
        result = re.findall(pattern, i)
        results.append(result)
    values = [''.join(i) for i in results]
    return values


async def spider(target, url):
    async with httpx.AsyncClient() as client:
        r = await client.get(url)
        if r.status_code != 200:
            print(f'{target} failed')
            with open('./spider/log.txt', 'a', encoding='utf-8') as f:
                f.write(f'{{{target}: {url}}}\n')
                return
        response = Selector(r.text)
        keys = response.css('dt.basicInfo-item::text').getall()
        keys = [first_parse(i) for i in keys if i != '\n']
        values = response.css('dd.basicInfo-item').getall()
        values = [first_parse(i) for i in values if i != '\n']
        values = second_parse(values)
        await queue.put({target: dict(zip(keys, values))})
        await queue_schedule.put(target)
      

async def save_result():
    results = {}
    while result := await queue.get():
        results |= result
        # print(results)
    with open('./spider/results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False)
    print('Finished!')

async def schedule():
    while source := await queue_schedule.get():
        print(f'{source} finished')


def load_urls():
    with open('./spider/related_things.json', 'r', encoding='utf-8') as f:
        return json.load(f)
    

async def run():
    batch_size = 8
    # todo Auto get urls
    urls = load_urls()
    urls_loader = UrlsLoader(urls, batch_size)
    for batch in urls_loader:
        await asyncio.gather(*(spider(target, url) for target, url in batch))
    await queue.put(None)
    await queue_schedule.put(None)

def main():
    loop = asyncio.new_event_loop()
    coros = [run(), save_result(), schedule()]
    coro = asyncio.wait(coros)
    loop.run_until_complete(coro)


if __name__ == '__main__':
    queue = asyncio.Queue()
    queue_schedule = asyncio.Queue()
    main()
    