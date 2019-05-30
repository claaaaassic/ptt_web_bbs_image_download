#-*- coding: utf-8 -*-
import requests
from lxml import etree
import shutil
import time
import sys
import os
from multiprocessing import Pool
from contextlib import closing

PROCESS_QUANTITY = 64
ENCODING = "utf-8"
PTT_SITE = "https://www.ptt.cc/"
PTT_BEAUTY_SITE = PTT_SITE + "/bbs/Beauty/index2338.html"


def download_image(image_url):
    url = "https:" + image_url + ".jpg"
    filename = url[18:]
    script_dir = os.path.dirname(__file__)
    try:
        res = requests.get(url, stream=True, timeout=10.0)
        rel_path = "images\\" + filename
        abs_file_path = os.path.join(script_dir, rel_path)
        f = open(abs_file_path, 'wb')
        shutil.copyfileobj(res.raw, f)
        f.close()
        del res
    except:
        a, b, c = sys.exc_info()
        rel_path = "err\\" + time.strftime('%Y%m%d_%H%M%S') + '.txt'
        abs_file_path = os.path.join(script_dir, rel_path)
        log = open(abs_file_path, 'w')
        log.write(time.strftime('%Y/%m/%d_%H:%M:%S') + '\n')
        log.write('例外類型 : ' + str(a) + '\n')
        log.write('例外訊息 : ' + str(b) + '\n')
        log.write('traceback物件 : ' + str(c) + '\n')
        log.write('filename : ' + str(filename) + '\n')
        log.write('url : ' + str(url))
        log.close()


def get_image_urls(article_link):
    article_response = requests.get(PTT_SITE + article_link)
    article_response.encoding = ENCODING
    html = etree.HTML(article_response.text)
    image_urls = html.xpath(
        "//div[@id='main-content']/div[@class='richcontent']/blockquote/a/@href")
    return image_urls

def createFolder():
    dir_name1 = "images"
    dir_name2 = "err"

    if not os.path.exists(dir_name1):
        os.mkdir(dir_name1)
        print("Directory " , dir_name1 ,  " Created ")
    else:
        print("Directory " , dir_name1 ,  " already exists")

    if not os.path.exists(dir_name2):
        os.mkdir(dir_name2)
        print("Directory " , dir_name2 ,  " Created ")
    else:
        print("Directory " , dir_name2 ,  " already exists")


def main():
    start_time = time.time()
    print("Ptt Web BBS Beauty images Download with %s process" % PROCESS_QUANTITY)

    createFolder()

    response = requests.get(PTT_BEAUTY_SITE)
    response.encoding = ENCODING
    if "批踢踢實業坊" not in response.content.decode():
        print("ERROR : cant connect to %s" % PTT_BEAUTY_SITE)
        print("url : %s, status_code : %s" %
              (response.url, response.status_code))
        sys.exit(0)

    html = etree.HTML(response.text)
    title = html.xpath("//div[@class = 'title']/a")
    article_links = html.xpath("//div[@class='title']/a/@href")

    # To search images url from all single page
    # return [[image_urls_list], [image_urls_list],...[image_urls_list]]
    with closing(Pool(processes=PROCESS_QUANTITY)) as pool:
        image_urls_list_list = pool.map(get_image_urls, article_links)
        pool.terminate()

    # To Concatenation all image urls in a list
    image_urls = list()
    for image_urls_list in image_urls_list_list:
        if len(image_urls_list) is 0:
            continue
        image_urls.extend(image_urls_list)

    # To download image with multiprocessing
    with closing(Pool(processes=PROCESS_QUANTITY)) as pool:
        pool.map(download_image, image_urls)
        pool.terminate()

    print("Download %s images execution time : %s sec" %
          (len(image_urls), str(time.time() - start_time)))

if __name__ == '__main__':
    main()
