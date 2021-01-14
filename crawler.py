from urllib.parse import urljoin, urlparse
from functools import reduce
import posixpath
import requests
from bs4 import BeautifulSoup
from PIL import Image
import sys
import os

BASE_URL = 'https://baohanhone.com/'


def getDir(base, dept=2):
    raw = BeautifulSoup(requests.get(base).text, "lxml")
    lst = raw.find_all('a', href=True)
    href = [base]
    href += list(set([urljoin(base, x['href']) for x in lst if x['href'].startswith(
        '/') and not x['href'].startswith('/account')]))
    if dept == 1:
        return href
    else:
        return list(set(reduce(lambda acc, ele: acc + getDir(ele, dept - 1), href, [])))


def getTotalDir(lstUrl):
    lst = list(filter(lambda x: '?page=' in x, lstUrl))
    heads = set([x[:x.index('?page=')] for x in lst])
    for head in heads:
        urls = list(filter(lambda x: head in x, lst))
        max_page = max([int(x[x.index('?page=')+6:]) for x in urls])
        for i in urls:
            if i in lstUrl:
                lstUrl.remove(i)
        for i in range(max_page):
            lstUrl.append(head + '?page=' + str(i+1))
    res = list(set(lstUrl))
    res.sort()
    return res

def removeEmptyFolders(root):
    folders = os.walk(root)[1]
    for folder in folders:
        if not folder[2]:
            os.rmdir(folder[0])

if __name__ == '__main__':
    if len(sys.argv) > 1:
        raw = getDir(sys.argv[1])
        urls = getTotalDir(raw)
        # urls = [sys.argv[1]]

        if os.path.isdir('Images'):
            os.system('rm -rf Images')
        os.system('mkdir Images')
        id = 0
        for url in urls:
            raw = BeautifulSoup(requests.get(url).text, 'lxml')
            for link in raw.findAll('img'):
                # get title
                title = link.get('alt')
                if not title:
                    title = 'noname'
                title = title.replace('/',' ')

                # get image
                img_link = urljoin('http:', link.get('data-src'))
                if not link.get('data-src'):
                    img_link = urljoin('http:', link.get('src'))
                    
                try:
                    img = Image.open(requests.get(img_link, stream=True).raw)
                    if img.mode != 'RGB':
                        img = img.convert('RGB')
                    img.save(f"Images/{str(id)}_{title}.jpeg")
                    id += 1
                except Exception:
                    pass
        removeEmptyFolders('Images')

    else:
        #demo
        raw = getDir(BASE_URL)
        urls = getTotalDir(raw)

        if os.path.isdir('products'):
            os.system('rm -rf products')
        os.system('mkdir products')
        id = 0
        for url in urls:
            path = 'products/' + url.split('/')[-1].split('?')[0]
            if not os.path.isdir(path):
                os.system(f'mkdir {path}')

            raw = BeautifulSoup(requests.get(url).text, 'lxml')
            for link in raw.findAll('div', {'class': 'product-box'}):
                # get title
                title = link.find('h3', {'class': 'product-name'}).find('a')['title']
                title = title.replace('/', '-')

                # get price
                price = link.find('div', {'class': 'special-price'}).find('span').text[:-1]

                # get image
                img_link = 'http:' + link.find('img')['data-src']
                img = Image.open(requests.get(img_link, stream=True).raw)
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                img.save(f"{path}/{price}_{title}.jpeg")

                id += 1
        removeEmptyFolders('products')
            
        
        
        
