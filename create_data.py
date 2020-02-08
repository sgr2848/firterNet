from selenium.webdriver.firefox.options import Options
import bs4 as bs
import requests, lxml
from selenium.webdriver import Firefox
import re
import random
# import concurrent.futures
import threading,os,time
# import multiprocessing
from typing import List
import importlib

def check_reddit_class(someString):
    if re.match('class=" thing id-t3_f[\d|a-z]{5}', someString):
        # print("{} matched".format(someString))
        return True
    else:
        # print("{} not matched".format(someString))
        # print(".",end="---")
        return False

def get_comment_data(url):

    res = requests.get(url,  headers={'User-agent': 'No a bot I swear'})
    if res.status_code == 200:
        b_soup = bs.BeautifulSoup(res.text, features="lxml")
        # a = b_soup.find_all('div', {"id": "thing_t1_cwds4nk"})
        a = re.findall('form-t1_[\d|a-z]{10}', str(b_soup))
        print(f"{url[20:]} has {len(a)} comments")
     
    else:
        print(res.text)
        print(f"colund't get in for some unknown reason {res.status_code}")
def make_data():
    """
        the main function I guess goes to reddit gets the top 25 post and collects the first page comment of the the page and give you a pickled file....
    """
    
    op = Options()
    op.headless = True
    brow = Firefox(options = op)

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
    for i in content_list:
        thread = threading.Thread(target=get_comment_data,args=[i])
        thread.start()
        threads.append(thread)
    for thread in threads:
         thread.join()
    #syncro took 36 secs || threading is more efficient way
    # for i in content_list:
    #     get_comment_data(i)
    print(f"{time.perf_counter()-time_a} secs || {len(content_list)} ")
if __name__ == "__main__":
    sel_as = importlib.util.find_spec("selenium")
    bs4_as = importlib.util.find_spec("bs4")
    lxml_as = importlib.util.find_spec("lxml")
    if (sel_as is not None or bs4_as is not None or lxml_as is not None):
        print(sel_as)
        print(bs4_as)
        print(lxml_as)
        make_data()
    else:
        os.system("python -m pip install -r requirements.txt")
        
        

