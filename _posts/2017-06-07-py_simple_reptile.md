---
layout: post
title: 简单的python爬虫
description: 简单的python爬虫。

---

#ruby增强型日志封装。

{% highlight python linenos %}
# -*- coding: utf-8 -*-
import os
import time
import asyncio
import aiohttp
from lxml import etree
import requests
import urllib.request


# noinspection PyBroadException
async def download(url, timeout_min):
    file_name = urllib.request.unquote(url.split('/')[-1])
    target_name = os.path.join('d:/xxx/', file_name)
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=60*timeout_min) as r:
                with open(target_name, 'wb') as f:
                    print(f'?[{file_name}]')
                    a_time = time.clock()
                    f.write(await r.read())
                    b_time = time.clock()
                    print(f'![{file_name}]:{b_time-a_time:.3f}s')
    except Exception as e:
        print(f'{file_name}:{repr(e)}')


def get_url_list():
    url_base = 'http://base_url/'
    html = requests.get(f'{url_base}xxx.html').content.decode('utf-8')
    result = []
    for i in etree.HTML(html).xpath("//*[@class='download']"):
        result += [f'{url_base}{x}' for x in i.xpath('@href')]
    return result


if __name__ == '__main__':
    begin_time = time.clock()
    url_list = get_url_list()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.gather(*[download(url, len(url_list)) for url in url_list]))
    loop.close()
    end_time = time.clock()
    print(f'cost time:{end_time-begin_time}')
{% endhighlight %}
