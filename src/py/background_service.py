"""Basically a "frontend" for the pyseoanalyzer
with additional support to analyze links.

Currently, the results were cached since pyseoanalyzer itself
is quite expensive to call (thus I disabled the follow_links).
"""


from gevent import monkey
monkey.patch_all()

from bs4 import BeautifulSoup  # noqa: E402

import asyncio          # noqa: E402
import cache            # noqa: E402
import gevent           # noqa: E402
import json             # noqa: E402
import requests         # noqa: E402
import seoanalyzer      # noqa: E402
import websockets       # noqa: E402


lock = gevent.lock.BoundedSemaphore()
cache_ttl = 60 * 10
cache_maxsize = 1024 * 10


@cache.AsyncTTL(time_to_live=cache_ttl, maxsize=cache_maxsize)
async def analyzeLinks(target_url):
    """Analyze internal, external, and broken links.

    This function solely depends on the status code.
    """
    brokenLinkStatus = [404]
    result = {
        'internal_links': 0,
        'external_links': 0,
        'broken_links': 0,
    }
    try:
        initialPage = requests.get(target_url)
        soup = BeautifulSoup(initialPage.text, features='lxml')

        if initialPage.status_code in brokenLinkStatus:
            # Avoid wasting resource to check another link
            return result, False

        for link in soup.find_all('a'):
            url = link.get('href')

            if url[0] == '#':
                continue

            if not url.startswith('http'):
                url = target_url + url

            response = requests.get(url)
            if response.status_code not in brokenLinkStatus:
                if url.startswith(target_url):
                    # Could also be indentified by host and domain
                    result['internal_links'] += 1
                else:
                    result['external_links'] += 1
            else:
                result['broken_links'] += 1

    except (requests.exceptions.SSLError,
            requests.exceptions.ConnectionError):
        pass

    return result, True


@cache.AsyncTTL(time_to_live=cache_ttl, maxsize=cache_maxsize)
async def findSitemap(target_url):
    endpoints = ['/sitemap.xml', '/robots.txt']
    for endpoint in endpoints:
        response = requests.get(target_url + endpoint)

        if response.status_code == 200 and endpoint == '/sitemap.xml':
            return target_url + '/sitemap.xml'

        elif response.status_code == 200 and endpoint == 'robots.txt':
            sitemapKeyword = 'Sitemap:'
            try:
                index = response.text.index(sitemapKeyword)
            except ValueError:
                return None

            sitemap = (
                response.text[index + len(sitemapKeyword) + 1:]
                .split('\n')[0]
                .strip())

            return sitemap

    return None


@cache.AsyncTTL(time_to_live=cache_ttl, maxsize=cache_maxsize)
async def analyze(target_url):
    """"""
    result = seoanalyzer.analyze(target_url, follow_links=False)
    pageResult = result['pages'][0]

    finalResult = {}
    finalResult['page_title'] = pageResult['title']
    finalResult['word_count'] = pageResult['word_count']
    finalResult['meta_description'] = pageResult['description']
    finalResult['keywords'] = [f'{keyword[1]}: {keyword[0]}'
                               for keyword in pageResult['keywords']]

    missingImgAltCounter = 0

    links, analyze_success = await analyzeLinks(target_url)

    for warning in result['pages'][0]['warnings']:
        if warning.startswith('Image missing alt tag'):
            missingImgAltCounter += 1
        # could add another warning counter

    finalResult['missing_img_alt'] = missingImgAltCounter
    finalResult['sitemap'] = await findSitemap(target_url)

    return {**finalResult, **links}


async def recvHandler(conn):
    while True:
        try:
            data = await conn.recv()
            print('received:', data)
            print('processing...')
            # Follow links is expensive
            output = await analyze(data)
            print('done')
            await conn.send(json.dumps(output))
        except websockets.exceptions.ConnectionClosed:
            print('connection closed')
            break


async def handler(conn):
    loop = asyncio.get_running_loop()
    print('connection accepted')
    data = await conn.recv()
    print(data)

    await asyncio.wait([
        loop.create_task(recvHandler(conn)),
    ])


async def main():
    async with websockets.serve(handler, '0.0.0.0', 8888):
        print('server running')
        await asyncio.Future()


if __name__ == '__main__':
    asyncio.run(main())
