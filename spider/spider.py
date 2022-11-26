import httpx
import asyncio
import re
from parsel import Selector
from urllib import parse
import json


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
        response = Selector(r.text)
        keys = response.css('dt.basicInfo-item::text').getall()
        keys = [first_parse(i) for i in keys if i != '\n']
        values = response.css('dd.basicInfo-item').getall()
        values = [first_parse(i) for i in values if i != '\n']
        values = second_parse(values)
        print(dict(zip(keys, values)))
        await queue.put({target: dict(zip(keys, values))})


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

async def save_result():
    with open('./spider/result.txt', 'a', encoding='utf-8') as f:
        while result := await queue.get():
            f.write(str(result) + '\n')
    print('Finished!')


async def run():
    batch_size = 2
    urls = {
        '数字孪生': 'https://baike.baidu.com/item/%E6%95%B0%E5%AD%97%E5%AD%AA%E7%94%9F/22197545?fr=aladdin'
    }
    urls_loader = UrlsLoader(urls, batch_size)
    for batch in urls_loader:
        await asyncio.gather(*(spider(target, url) for target, url in batch))
    await queue.put(None)

def main():
    loop = asyncio.new_event_loop()
    coros = [run(), save_result()]
    coro = asyncio.wait(coros)
    loop.run_until_complete(coro)



if __name__ == '__main__':
    queue = asyncio.Queue()
    main()
    