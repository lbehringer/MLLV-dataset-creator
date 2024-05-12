"""
Copyright 2024 Lyonel Behringer

This file is based on code from https://github.com/iisys-hof/HUI-Audio-Corpus-German
and is licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import bs4 as bs
import pandas as pd
from huiAudioCorpus.utils.PathUtil import PathUtil
import requests
import json
from tqdm import tqdm
from joblib import Parallel, delayed
from urllib.parse import quote
from typing import Union
import time
from huiAudioCorpus.utils.whisper_utils import get_language_expanded

class AudiosFromLibrivoxPersistence:

    def __init__ (self, 
                  book_name: str, 
                  save_path: str, 
                  chapter_path: str, 
                  reader: str = None,
                  hifi_qa_save_path: str = None,
                  url: str = 'https://librivox.org/', 
                  solo_reading: bool = None, 
                  sections: Union[list, str] = None, 
                  limit_per_iteration: int = 1000,
                  max_iterations: int = 20,
                  max_chapters_per_reader: int = None,
                  start_timestamp: int = None):
        self.reader = reader
        self.book_name = book_name
        self.url = url
        self.save_path = save_path
        self.solo_reading = solo_reading
        self.sections = sections
        self.chapter_path = chapter_path
        self.hifi_qa_save_path = hifi_qa_save_path
        self.path_util = PathUtil()
        self.limit_per_iteration = limit_per_iteration
        self.max_iterations = max_iterations
        self.max_chapters_per_reader = max_chapters_per_reader
        self.start_timestamp = start_timestamp
        if self.start_timestamp is None:
            self.start_timestamp = int(time.time()) - 2_592_000 # 30 days prior to current time

    def save(self):
        if self.reader is None:
            raise Exception("Reader must be specified for saving Hifi QA stats!")
        chapters, download_link_dict = self.get_chapters(self.book_name, get_download_links=True)
        Parallel(n_jobs=1)(delayed(self.path_util.copy_file_from_url) \
                        (download_link_dict[key], self.save_path + '/' + download_link_dict[key].split('/')[-1]) for key in sorted(download_link_dict)[:self.max_chapters_per_reader])
        chapters.to_csv(self.chapter_path)

        # save hifi_qa stats (reader specific)
        hifi_qa_stat_dict = {key: [download_link_dict[key].split("/")[-1].split(".")[0], self.book_name, key, self.reader, self.solo_reading] for key in sorted(download_link_dict)[:self.max_chapters_per_reader]}
        hifi_qa_df = pd.DataFrame.from_dict(hifi_qa_stat_dict, orient='index', columns=['id', 'book_name', 'section', 'reader', 'solo_reading'])
        hifi_qa_df.to_csv(self.hifi_qa_save_path, sep="|", index=False)      
        
    def get_chapters(self, book_name: str, get_download_links):
        search_url = self.get_search_url(book_name, self.url)
        response = self.load_search_book(search_url)
        chapter_url = self.extract_chapter_url(response)
        if chapter_url == "":
            return None, None
        chapter_download_link_dict = self.get_chapter_links(chapter_url) if get_download_links else None
        chapters = pd.read_html(chapter_url)
        return chapters[0], chapter_download_link_dict

    def get_catalog_date(self, search_url: str):
        search_result = requests.get(search_url)
        search_result.encoding = "UTF-8"
        soup = bs.BeautifulSoup(search_result.text, 'html.parser')
        try:
            production_details = soup.find("dl", class_="product-details")
            catalog_date = production_details.find_all("dd")[2].text
        except:
            catalog_date = "0000-00-00" # placeholder as `oldest` book
        return int(catalog_date.replace("-", ""))

    def load_search_book(self, url: str):
        search_result = requests.get(url)
        return search_result.text

    def get_search_url(self, book_name: str, url: str):
        search_url = url + 'api/feed/audiobooks/?format=json&title=' + quote(book_name)
        return search_url

    def extract_chapter_url(self, response: str):
        json_input = json.loads(response)['books']
        book = json_input[0]
        url_zip_file = book['url_librivox']
        return url_zip_file

    def extract_zip_url(self, response: str):
        json_input = json.loads(response)['books']
        book = json_input[0]
        url_zip_file = book['url_zip_file']
        return url_zip_file

    def get_chapter_links(self, url: str):
        search_result = requests.get(url)
        search_result.encoding = "UTF-8"
        # retrieve the chapter-download table for the current book
        soup = bs.BeautifulSoup(search_result.text, 'html.parser')
        parsed_table = soup.find_all('table')[0] 
        # get 5 elements per row: low-quality chapter link, high-quality chapter link, author link, source text link, reader link
        data = [[td.a['href'] if td.find('a') else 
                ''.join(td.stripped_strings)
                for td in row.find_all('td')]
                for row in parsed_table.find_all('tr')]
        # for each row, the section number is the key, and index 1 (the high-quality chapter link) is the value
        # row 0 is an empty list, so we ignore it
        if self.solo_reading:
            download_link_dict = {idx: chapter[1] for idx, chapter in enumerate(data) if len(chapter) > 0}
        else:
            download_link_dict = {idx: chapter[1] for idx, chapter in enumerate(data) if idx in set(self.sections) and len(chapter) > 0}
        return download_link_dict

    def get_ids(self, language, request_url=None):
        books = []
        if request_url:
            print("Using custom request URL for metadata retrieval.")
            page = requests.get(request_url)
            page.encoding = "UTF-8"
            try:
                result = json.loads(page.text)
                if 'books' in result:
                    for idx, book in enumerate(result['books']):
                        if is_book_useable(book, language):
                            result['books'][idx]['catalog_date'] = self.get_catalog_date(book['url_librivox'])
                    books.extend(result['books'])
                else:
                    print(result)
                    print("Stopping download of overview metadata.")
            except ValueError as e:
                print(f"caught ValueError: {e}")
                print("Stopping download of overview metadata.")
        else:
            limit = self.limit_per_iteration
            for i in tqdm(range(self.max_iterations), desc=f"Performing retrieval in max. {self.max_iterations} iterations"):
                request_url = f'https://librivox.org/api/feed/audiobooks/?limit={limit}&offset={i*limit}&since={self.start_timestamp}&format=json'
                page = requests.get(request_url)
                page.encoding = "UTF-8"
                try:
                    result = json.loads(page.text)
                    if 'books' in result:
                        for idx, book in enumerate(tqdm(result['books'], desc=f"Getting catalog dates for usable books, iteration {i+1}")):
                            if is_book_useable(book, language):
                                result['books'][idx]['catalog_date'] = self.get_catalog_date(book['url_librivox'])
                        books.extend(result['books'])
                    else:
                        print(result)
                        print("Stopping download of overview metadata.")
                        break
                except ValueError as e:
                    print(f"Error in iteration {i}: {e}")
                    print("Stopping download of overview metadata.")
                    break
        return books

def is_book_useable(book, language):
    """Determines whether or not a book is usable for dataset creation.
    Returns a boolean."""
    if book['totaltimesecs']<=0:
        return False
    if book['language'] not in [language, get_language_expanded(language)]:
        return False
    return True