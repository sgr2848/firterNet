from selenium.webdriver.firefox.options import Options
import bs4 as bs
import requests, lxml
from selenium.webdriver import Firefox
import re
import random
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import ProcessPoolExecutor
from concurrent.futures import as_completed
import os, time
import tensorflow as tf
from tensorflow.keras.preprocessing.text import text_to_word_sequence, hashing_trick
from tensorflow.keras.preprocessing.text import Tokenizer
import pickle
from typing import List
import importlib
import logging
import numpy as np
import pickle
logging.basicConfig(filename="newfile.log",
                    format='%(asctime)s %(message)s',
                    filemode='w')
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
# create a file handler
########dont run...... code is a memory hog at the moment will change how this function

def process_text(text_to_process):
    '''
    this function take in a str and returns out a multidimensional array 
    '''
    token_list = [] 

    with tf.device(':/device:GPU:0'):
        tkn = Tokenizer(num_words=2)
        for i in text_to_process:        
            if match_words(i):            
                logger.info(f"{i}")
                tkn.fit_on_texts(i)
                enoded_docs = tkn.texts_to_matrix(i, mode='count')
                token_list.append([enoded_docs, [1]])
            else:            
                tkn.fit_on_texts(i)
                enoded_docs = tkn.texts_to_matrix(i, mode='count')
                token_list.append([enoded_docs, [0]])
        return token_list
def match_words(input_string: str) -> bool:
    '''
    function that return true if those words appears in the input string
    '''
    return_val = False
    string_list = text_to_word_sequence(input_string)
    for i in string_list:
        if re.match("(fuck)+|(cunt)+|(suck a dick)+",i):
            return_val = True
        else:
            pass
    return return_val
   
def check_reddit_class(someString):
    '''
    not needed | will delete in refactoring
    '''                
    if re.match('class=" thing id-t3_f[\d|a-z]{5}', someString):
        # print("{} matched".format(someString))
        return True
    else:
        # print("{} not matched".format(someString))
        # print(".",end="---")
        return False

def get_comment_data(url:str) -> List:
    

    res = requests.get(url,  headers={'User-agent': 'No a bot I swear'})
    if res.status_code == 200:
        b_soup = bs.BeautifulSoup(res.text, features="lxml")
        # a = b_soup.find_all('div', {"id": "thing_t1_cwds4nk"})
        a = re.findall('form-t1_[\d|a-z]{10}', str(b_soup))
        # print(f"{url[20:]} has {len(a)} comments")
        word_matrix = []
        new_matrix = []
        for i in a:
            current_comment = b_soup.select('form', {'id': i})
            for para in current_comment:
                for i in para.findAll('p'):
                    # print(".",end="|")
                    word_matrix.append(i.text)
                
            with ProcessPoolExecutor(max_workers=2) as exe:
                futures = [exe.submit(process_text, text) for text in word_matrix]
                for future in as_completed(futures):
                    new_matrix.append(future.result()) 
        return new_matrix

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
    with ThreadPoolExecutor(max_workers=1) as exe:
        futures = [exe.submit(get_comment_data, url) for url in content_list[0:1]]
        for future in as_completed(futures):
            # print("***DONZOO***", end="_|_")
            print(time.perf_counter()-time_a,end = ",")
            time_list.append(time.perf_counter()-time_a)
            comment_list.append(future.result())

    with open("data.pkl", "rb", encoding="utf-8") as data_file:
        for i in comment_list:
            pickle.dump(i,data_file)
    print(f"{(time.perf_counter()-time_a)/60} mins || {len (content_list)}")

if __name__ == "__main__":
    sel_as = importlib.util.find_spec("selenium")
    bs4_as = importlib.util.find_spec("bs4")
    lxml_as = importlib.util.find_spec("lxml")
    if (sel_as is not None or bs4_as is not None or lxml_as is not None):
        a = ["GO fuck yourself", "just spent some time with them in SOHO",
             "Walk out and gather stuff", "would you stop being a cunt", "it is fucking useless that you"]
        # print(sel_as)
        # print(bs4_as)
        # print(lxml_as)
        # get_comment_data("https://old.reddit.com/r/worldnews/comments/f0v18s/buried_in_trumps_peace_plan_a_proposal_that_could/")
        make_data()
        # ar = process_text(a)
        # logger.info(f" the len is --->{len(ar)}")
        # for i in ar:
        #     print(np.shape((i)[0]))      
        
        
    else:
        os.system("python -m pip install -r requirements.txt")
        
        

