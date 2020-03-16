from selenium.webdriver.firefox.options import Options
import bs4 as bs
import  lxml
from selenium.webdriver import Firefox
import re
import sys
import time
import gc
import requests
from random import randint
from time import perf_counter
from os import system
# import resource #for linux
from concurrent.futures import ThreadPoolExecutor,ProcessPoolExecutor,as_completed
import tensorflow as tf
from tensorflow.keras.preprocessing.text import text_to_word_sequence, hashing_trick, Tokenizer
import pickle
from typing import List
import importlib
import logging
from collections import deque
import numpy as np

root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
handler = logging.FileHandler("sameNoe.log", "w", "utf-8")
handler.setFormatter(logging.Formatter('%(name)s %(message)'))
root_logger.addHandler(handler)

# create a file handler
########dont run...... code is a memory hog at the moment will change how this function
#for linux 
# def limit_memory(size):
#     soft, hard = resource.getrlimit(resource.RLIMIT_AS)
#     resource.setrlimit(resource.RLIMIT_AS,(size,hard))

def process_text(text_to_process):
    '''
    this function take in a str and returns out a multidimensional array 
    '''

    token_list = []
    de = deque(text_to_process.split(" "))
    del text_to_process
    
    with tf.device(':/device:GPU:0'):
        tkn = Tokenizer(num_words=2)
        while len(de) != 0:            
            if match_words(de[0]):
                    # somefile.write(de[0])      
                # root_logger.info(f"{de[0]}")
                tkn.fit_on_texts(de[0])
                enoded_docs = tkn.texts_to_matrix(de[0], mode='count')
                token_list.append([enoded_docs, [1]])
                de.popleft()
            else:
                    # somefile.write(de[0])
                    # print(de[0])   
                # root_logger.info(f"{de[0]}")
                tkn.fit_on_texts(de[0])
                enoded_docs = tkn.texts_to_matrix(de[0], mode='count')
                token_list.append([enoded_docs, [0]])
                
                de.popleft()
    

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
    if re.match('class=" thing id-t3_f[\d|a-z]{5} even', someString) or re.match('class=" thing id-t3_f[\d|a-z]{5} odd', someString):
        # print("{} matched".format(someString))
        return True
    else:
        # print("{} not matched".format(someString))
        # print(".",end="---")
        return False

def get_comment_data(url:str):
    

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
                for k in para.findAll('p'):
                    # print(".",end="|")
                    word_matrix.append(k.text)
            # print(word_matrix)
            with ProcessPoolExecutor(max_workers=2) as exe:
                futures = [exe.submit(process_text, word) for word in word_matrix]
                for future in as_completed(futures):
                    # print(f"{np.array(future.result()).shape} the shape is  \n \n")
                    new_matrix.append(future.result())
                    astitwa = len(new_matrix)
                    print(astitwa)    
                    if astitwa == 1500:
                        a = randint(0,200)              
                        with open(f"file{a}.pkl", 'wb') as pick_file:
                            pickle.dump(new_matrix, pick_file)
                        new_matrix = []
        del new_matrix                      
                

    else:
        print(res.text)
        print(f"couldn't get in for some unknown reason : {res.status_code} ")
      
def make_data():
    """
        the main function I guess goes to reddit gets the top 25 post and collects the first page comment of the the page and give you a pickled file....
    """
    
    op = Options()
    # op.headless = True
    brow = Firefox(executable_path = 'geckodriver.exe',options= op)

    brow.set_page_load_timeout('10')
    brow.get("https://old.reddit.com/")  # think there might be a function that is much better solution than sleeping but oh welllllll
    table = brow.find_element_by_xpath("//div[@id='siteTable']").get_attribute("innerHTML")    
    alist = re.split("<div | div>",table)
    print(f"{len(alist)}")
    feed_list = []
    for i in alist:
        if len(i) > 30:
            if check_reddit_class(i[0:34]):
                print(i[0:34])
                feed_list.append(i)
            else:
                pass
        else:
            pass
    content_list =[]
    print(f"{len(content_list)}")
    for i in feed_list:
        a = re.findall('/r/[\d|a-z|A-Z|-|_]+/comments/[\d|a-z|A-Z|-|_]+/[\d|a-z|A-Z|-|_]+/', i)
        # print(a[0])
        content_list.append(f"http://old.reddit.com{a[0]}")
    # print(content_list)
    brow.quit()    
    time_a = perf_counter()

    # time_list = []
    with ThreadPoolExecutor(max_workers=1) as exe:
        futures = [exe.submit(get_comment_data, url) for url in content_list[0:1]]
        for future in as_completed(futures):
            pass



    print(f"{(perf_counter()-time_a)/60} mins || {len (content_list)}")

if __name__ == "__main__":
    # limit_memory(1512) # linux limit mem
    try:
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
            # print(check_reddit_class('class=" thing id-t3_f3zad0 even link'))
            
        else:
            system("python -m pip install -r requirements.txt")
    except MemoryError:
        sys.stderr.write('\n\nERROR: Memory Exception\n')
        sys.exit(1)
        

