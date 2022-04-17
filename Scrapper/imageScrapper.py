from selenium import  webdriver
import time
import requests
import os
from dbOperation.mongodb import  mongodbOperation


class imageScrapping:
    def __init__(self):
        try:
            self.driver_path='./chromedriver'
            self.dbOps=mongodbOperation(username='image', password='image')
            self.dbName='image_scrapper'
        except Exception as e:
            raise e

    def fetch_image_urls(self, query, max_links_to_fetch, wd, available_img_urls=[], sleep_between_interactions = 1):
        '''
        Method Name:fetch_image_urls
        Description : Returns urls
        Output: a set
        On Failure: Exception

        Written By: Sayan Saha
        Version:1
        Revision: None
        '''
        try:

            def scroll_to_end(wd):
                wd.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(sleep_between_interactions)

                # build the google query

            search_url = "https://www.google.com/search?safe=off&site=&tbm=isch&source=hp&q={q}&oq={q}&gs_l=img"

            # load the page
            wd.get(search_url.format(q=query))

            image_urls = set()
            image_count = 0
            results_start = 0
            while image_count < max_links_to_fetch:
                scroll_to_end(wd)

                # get all image thumbnail results
                thumbnail_results = wd.find_elements_by_css_selector("img.Q4LuWd")
                number_results = len(thumbnail_results)


                for img in thumbnail_results[results_start:number_results]:
                    # try to click every thumbnail such that we can get the real image behind it
                    try:
                        img.click()
                        time.sleep(sleep_between_interactions)
                    except Exception:
                        continue

                    # extract image urls
                    actual_images = wd.find_elements_by_css_selector('img.n3VNCb')
                    for actual_image in actual_images:
                        if actual_image.get_attribute('src') and 'http' in actual_image.get_attribute('src'):
                            url=actual_image.get_attribute('src')
                            if url not in available_img_urls:
                                image_urls.add(url)

                    image_count = len(image_urls)

                    if len(image_urls) >= max_links_to_fetch:
                        break
                else:
                    time.sleep(30)
                    # return
                    load_more_button = wd.find_element_by_css_selector(".mye4qd")
                    if load_more_button:
                        wd.execute_script("document.querySelector('.mye4qd').click();")

                # move the result startpoint further down
                results_start = len(thumbnail_results)

            return image_urls
        except Exception as e:
            raise e

    def StoreImageToDB(self, search_term, url):
        '''
        Method Name: StoreImageToDB
        Description: It stores image to database in binary format
        Output: None
        On Failure: Exception

        Written By: Sayan Saha
        Version: 1.0
        Revision: None
        '''
        try:
            image_content = requests.get(url).content

        except Exception as e:
            raise e

        try:
            image_data = {
                'image': image_content,
                'url': url
            }
            self.dbOps.insertOneData(dbName=self.dbName, collectionName=search_term,data=image_data)
        except Exception as e:
            raise e

    def search_and_download(self, search_term, expected_img_number):
        '''
        Method Name: search_and_download
        Description: It searchs query, store images into db and creates a folder in directory to download
        Output: None
        On Failure: Exception

        Written By: Sayan Saha
        Version: 1.0
        Revision: None
        '''
        try:
            if self.dbOps.isCollectionPresent(dbName=self.dbName, collectionName=search_term):
                available_img_number=self.dbOps.CountOfDataInCollection(dbName=self.dbName, collectionName=search_term)
                if expected_img_number<=available_img_number:
                    self.CreateFolderToDownload(dbName=self.dbName, collectioName=search_term, img_number=expected_img_number, folderName=search_term)
                else:
                    required_img_number=expected_img_number-available_img_number
                    available_img_urls=self.dbOps.getFromOneField(dbName=self.dbName, collectionName=search_term, fieldName='url')
                    available_img_urls=[img_url['url'] for img_url in available_img_urls]
                    with webdriver.Chrome(executable_path=self.driver_path) as wd:
                        res = self.fetch_image_urls(query=search_term, max_links_to_fetch=required_img_number, wd=wd, available_img_urls=available_img_urls, sleep_between_interactions=0.5)
                    for elem in res:
                        try:
                            self.StoreImageToDB(search_term, elem)
                        except Exception as e:
                            continue
                    self.CreateFolderToDownload(dbName=self.dbName, collectioName=search_term, img_number=expected_img_number, folderName=search_term)


            else:
                with webdriver.Chrome(executable_path=self.driver_path) as wd:
                    res = self.fetch_image_urls(query=search_term, max_links_to_fetch=expected_img_number, wd=wd, sleep_between_interactions=0.5)
                self.dbOps.createCollection(dbName=self.dbName, collectionName=search_term)
                for elem in res:
                    try:
                        self.StoreImageToDB(search_term, elem)
                    except Exception as e:
                        continue

                self.CreateFolderToDownload(dbName=self.dbName, collectioName=search_term, img_number=expected_img_number,folderName=search_term)
        except Exception as e:
            raise e


    def CreateFolderToDownload(self, dbName, collectioName, img_number, folderName):
        '''
        Method Name: CreateFolderToDownload
        Description: It creates a folder in current directory to give user option to download
        Output: None
        On Failure: Exception

        Written By: Sayan Saha
        Version: 1.0
        Revision: None
        '''
        try:
            if not os.path.exists(folderName):
                os.mkdir(folderName)
            binary_images=self.dbOps.getFromOneField(dbName=dbName, collectionName=collectioName, fieldName='image', limit=img_number)
            binary_images=[i['image'] for i in binary_images]
            counter=1
            for img in binary_images:
                with open(os.path.join(folderName, f'{folderName}_{str(counter)}.jpg'), 'wb') as f:
                    f.write(img)
                counter+=1
        except Exception as e:
            raise e



