from selenium.webdriver.firefox.options import Options
import bs4 as bs
import requests, lxml
from selenium.webdriver import Firefox
import re
import random
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed
import os,time
#import threading
# import multiprocessing
from typing import List
import importlib
import numpy as np
import pickle

def check_reddit_class(someString):
    if re.match('class=" thing id-t3_f[\d|a-z]{5}', someString):
        # print("{} matched".format(someString))
        return True
    else:
        # print("{} not matched".format(someString))
        # print(".",end="---")
        return False

def get_comment_data(url) :

    res = requests.get(url,  headers={'User-agent': 'No a bot I swear'})
    if res.status_code == 200:
        b_soup = bs.BeautifulSoup(res.text, features="lxml")
        # a = b_soup.find_all('div', {"id": "thing_t1_cwds4nk"})
        a = re.findall('form-t1_[\d|a-z]{10}', str(b_soup))
        # print(f"{url[20:]} has {len(a)} comments")
        word_matrix = []
        for i in a:
            current_comment = b_soup.select('form', {'id': i})
            for para in current_comment:
                for i in para.findAll('p'):
                    # print(".",end="|")
                    word_matrix.append(i.text)
        return word_matrix

    else:
        print(res.text)
        print(f"couldn't get in for some unknown reason : {res.status_code} ")
        return ["couldn't grab shit"]
def make_data():
    """
        the main function I guess goes to reddit gets the top 25 post and collects the first page comment of the the page and give you a pickled file....
    """
    
    op = Options()
    op.headless = True
    brow = Firefox(executable_path = 'geckodriver.exe',options = op)

    brow.set_page_load_timeout('10')
    brow.get("https://old.reddit.com/")  # think there might be a function that is much better solution than sleeping but oh welllllll
    table = brow.find_element_by_xpath("//div[@id='siteTable']").get_attribute("innerHTML")    
    alist = re.split("<div | div>",table)
    
    feed_list = []
    for i in alist:
        if len(i) > 30:
            if check_reddit_class(i[0:26]):
                feed_list.append(i)
            else:
                pass
        else:
            pass
    content_list =[]
    for i in feed_list:
        a = re.findall('data-permalink="/r/[\d|a-z|A-Z|-|_]+/comments/[\d|a-z|A-Z|-|_]+/[\d|a-z|A-Z|-|_]+/', i)
        content_list.append(f"http://old.reddit.com{a[0][16:]}")
    brow.quit()    
    threads = [] 
    time_a = time.perf_counter()
    # for i in content_list:
    #     thread = threading.Thread(target=get_comment_data,args=[i])
    #     thread.start()
    #     threads.append(thread)
    # for thread in threads:
    #      thread.join()
    #syncro took 36 secs || threading is more efficient way
    # for i in content_list:
    #     get_comment_data(i)
    comment_list = []
    time_list = []
    with ThreadPoolExecutor(max_workers=10) as exe:
        futures = [exe.submit(get_comment_data, url) for url in content_list]
        for future in as_completed(futures):
            print("***DONZOO***", end="_|_")
            print(time.perf_counter()-time_a)
            time_list.append(time.perf_counter()-time_a)
            comment_list.append(future.result())

    with open("data.txt", "a", encoding="utf-8") as data_file:
        for i in comment_list:
            data_file.write(str(i))
    print(f"{(time.perf_counter()-time_a)/60} mins || {len (content_list)}")
if __name__ == "__main__":
    sel_as = importlib.util.find_spec("selenium")
    bs4_as = importlib.util.find_spec("bs4")
    lxml_as = importlib.util.find_spec("lxml")
    if (sel_as is not None or bs4_as is not None or lxml_as is not None):
        print(sel_as)
        print(bs4_as)
        print(lxml_as)
        # get_comment_data("https://old.reddit.com/r/worldnews/comments/f0v18s/buried_in_trumps_peace_plan_a_proposal_that_could/")
        make_data()
    else:
        os.system("python -m pip install -r requirements.txt")
        
        

