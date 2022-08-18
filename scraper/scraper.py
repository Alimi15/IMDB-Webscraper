from operator import truediv
from selenium.webdriver.common.by import By
from selenium import webdriver
import time
import uuid
import json
import os
import urllib.request
import psycopg2
import sqlalchemy as db
import pandas as pd
import upload_to_bucket as upl


class IMDbScraper:
    """Webdriver class that has methods to load the IMDb website and scrape data from it.

    Attributes
    ----------
    session: webdriver.Chrome()
        A chromedriver instance which is used to open chrome.
    URL: str
        URL of the specific list from which the data is sraped.

    """

    def __init__(self):
        """Constructor method
        """
        self.session = webdriver.Chrome()
        self.URL = "https://www.imdb.com/search/keyword/?keywords=superhero&pf_rd_m=A2FGELUUNOQJNL&pf_rd_p=a581b14c-5a82-4e29-9cf8-54f909ced9e1&pf_rd_r=WCKJ24NKVMM6G468NPWT&pf_rd_s=center-5&pf_rd_t=15051&pf_rd_i=genre&ref_=kw_ref_typ&mode=detail&page=1&sort=user_rating,desc&title_type=movie"

    def load(self):
        """Loads the initial webpage
        """
        self.session.get(self.URL)

    def get_links(d: webdriver.Chrome) -> list:
        """Gets a list of links to visit in order to scrape the data

        Parameters
        ----------
        d: webdriver.Chrome
            A chromedriver instance

        Returns
        -------
        link_list: list of str
            A list of URLs to each film that will be scraped

        """
        film_container = d.session.find_element(By.XPATH, '//*[@class="lister-list"]')
        film_list = film_container.find_elements(By.XPATH, './div')
        link_list = []

        for film in film_list:
            a_tag = film.find_element(By.TAG_NAME, 'a')
            link = a_tag.get_attribute('href')
            link_list.append(link)

        return link_list
    
    def crawl(d: webdriver.Chrome, list_links):
        """Crawls through the list of URLs given and stores information about each film
        
        Parameters
        ----------
        d: webdriver.Chrome
            A chromedriver instance
        list_links: list of str
            List of URLs to visit to retrieve data
            
        Returns
        -------
        list_dict: list of dict
            List of dictionaries that store information regarding a single film
            
        """
        list_dict = []
        for link in list_links:
            try:
                time.sleep(2)
                d.session.get(link)
                unique_id = uuid.uuid4()
                name = d.session.find_element(By.XPATH, '//h1[@data-testid="hero-title-block__title"]').text
                rating = d.session.find_element(By.XPATH, '//span[@class="sc-7ab21ed2-1 jGRxWM"]').text
                year = d.session.find_element(By.XPATH, '//a[@class="ipc-link ipc-link--baseAlt ipc-link--inherit-color sc-8c396aa2-1 WIUyh"]').text
                image_tag = d.session.find_element(By.XPATH, '//img[@class="ipc-image"]')
                image_url = image_tag.get_attribute('src')
                dict_film = {'UniqueID': str(unique_id), 'FriendlyID': link, 'Name': name, 'Rating': rating, 'Year': year, 'ImageURL': image_url}
                list_dict.append(dict_film)
            except:
                pass
        return list_dict

    def next(d: webdriver.Chrome):
        """Finds the next button and moves to the next page of results
        
        Parameters
        ----------
        d: webdriver.Chrome
            A chromedriver instance

        """
        next_button = d.session.find_element(By.XPATH, '//a[@class="lister-page-next next-page"]')
        next_link = next_button.get_attribute('href')
        d.session.get(next_link)


    def exit(d: webdriver.Chrome):
        """Closes the chromedriver session
        
        Parameters
        ----------
        d: webdriver.Chrome
            A chromedriver instance

        """
        d.session.quit()

def download_data(list_dict):
    """Downloads the film data from the dictionary and downloads image data using URL
    
    Parameters
    ----------
    list_dict: list of dict
        List of dictionaries containing data on films

    """


    for film in list_dict:
        try:
            os.mkdir("/raw_data/"+film['UniqueID'])
        except FileExistsError:
                pass
        with open("/raw_data/"+film['UniqueID']+"/data.json", "w") as write_file:
            json.dump(film, write_file, indent=4)
        image_url = film['ImageURL']
        urllib.request.urlretrieve(image_url, "/raw_data/"+film['UniqueID']+"/poster.jpg")

if __name__ == "__main__":
    list_dict_film = []
    while True:
        print("1. Load Data")
        print("2. Scrape Data")
        print("3. Download Data")
        print("4. Upload to Bucket")
        print("5. Upload to RDS")
        print("0. Quit")
        choice = input("Choose an option from above")
        if choice == "1":
            dir_list = []
            path_of_the_directory= '/raw_data'
            for dir_name in os.listdir(path_of_the_directory):
                f = os.path.join(path_of_the_directory,dir_name)
                if os.path.isfile(f):
                    dir_list.append(f)
            for dir in dir_list:
                filename = os.path.join(dir,'data.json')
                with open(filename, 'r') as json_file:
                    json_load = json.load(json_file)
                list_dict_film.append(json_load)
        elif choice == "2":
            driver = IMDbScraper()
            driver.load()
            big_list = []
            for i in range(3):
                big_list.extend(driver.get_links())
                driver.next()
            try:
                os.mkdir("raw_data")
            except FileExistsError:
                pass
            list_dict_film.extend(driver.crawl(big_list))
            driver.exit()
        elif choice == "3":
            download_data(list_dict_film)
        elif choice == "4":
            for film in list_dict_film:
                upl.create_bucket_directory(film["Unique ID"])
                upl.upload_to_bucket("/raw_data/"+film["UniqueID"]+"/data.json", film["UniqueID"]+"/data.json")
                upl.upload_to_bucket("/raw_data/"+film["UniqueID"]+"/poster.jpg", film["UniqueID"]+"/poster.jpg")
        elif choice == "5":
            DATABASE_TYPE = 'postgresql'
            DBAPI = 'psycopg2'
            HOST = 'scraper-db.cdoruy3qj9zl.us-east-1.rds.amazonaws.com'
            USER = 'postgres'
            PASSWORD = 'imdbwebscraper'
            DATABASE = 'initial_scraper_db'
            PORT = 5432
            engine = db.create_engine(f"{DATABASE_TYPE}+{DBAPI}://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}")
            connection = engine.connect()
            metadata = db.MetaData()
            films = db.Table('films', metadata, autoload=True, autoload_with=engine)
            query = db.insert(films)
            values_list = list_dict_film
            ResultProxy = connection.execute(query,values_list)
        elif choice == "0":
            break
