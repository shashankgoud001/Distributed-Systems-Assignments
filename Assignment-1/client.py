# import requests

# from time import perf_counter

# start=perf_counter()


# for x in range(1,25000):
#     r = requests.get("http://localhost:6060/home")
#     print(r.json())

# stop=perf_counter()

# "threading is for working in parallel, and async is for waiting in parallel".


import asyncio
from time import perf_counter

import aiohttp


async def fetch(s, url):
    async with s.get('http://localhost:5000/home') as r:
        if r.status != 200:
            r.raise_for_status()
        res=await r.text()
        print(res)
        return res


async def fetch_all(s, urls):
    tasks = []
    for url in urls:
        task = asyncio.create_task(fetch(s, url))
        tasks.append(task)
    res = await asyncio.gather(*tasks)
    return res


async def main():
    urls = range(1, 10000)
    async with aiohttp.ClientSession() as session:
        htmls = await fetch_all(session, urls)
        # print(htmls)


if __name__ == '__main__':
    start = perf_counter()
    asyncio.run(main())
    stop = perf_counter()
    # print("time taken:", stop - start)


#time taken: 25.523571709000862
#time taken: 