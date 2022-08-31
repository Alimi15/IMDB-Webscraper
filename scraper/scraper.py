from operator import truediv
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver import ChromeOptions
import upload_to_bucket as upl
import time
import uuid
import json
import os
import urllib.request
import psycopg2
import sqlalchemy as db
import pandas as pd
DATABASE_TYPE = 'postgresql'
DBAPI = 'psycopg2'
HOST = 'scraper-db.cdoruy3qj9zl.us-east-1.rds.amazonaws.com'
USER = 'postgres'
PASSWORD = 'imdbwebscraper'
DATABASE = 'initial_scraper_db'
PORT = 5432

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
        chromeOptions = ChromeOptions()
        # chromeOptions.add_argument('--no-sandbox')
        chromeOptions.add_argument('--window-size=1920, 1080')
        chromeOptions.add_argument('--disable-gpu')
        chromeOptions.add_argument('--headless')
        chromeOptions.add_argument("--disable-dev-shm-usage")
        chromeOptions.add_argument("--crash-dumps-dir=/tmp")
        chromeOptions.add_argument("--start-maximized")
        chromeOptions.headless = True
        self.session = webdriver.Chrome(options=chromeOptions)
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
            if not check_rescrape(link):
                try:
                    time.sleep(2)
                    d.session.get(link)
                    unique_id = uuid.uuid4()
                    name = d.session.find_element(By.XPATH, '//h1[@data-testid="hero-title-block__title"]').text
                    rating = d.session.find_element(By.XPATH, '//span[@class="sc-7ab21ed2-1 jGRxWM"]').text
                    year = d.session.find_element(By.XPATH, '//a[@class="ipc-link ipc-link--baseAlt ipc-link--inherit-color sc-8c396aa2-1 WIUyh"]').text
                    image_tag = d.session.find_element(By.XPATH, '//img[@class="ipc-image"]')
                    image_url = image_tag.get_attribute('src')
                    dict_film = {'uniqueid': str(unique_id), 'friendlyid': link, 'name': name, 'rating': rating, 'year': year, 'imageurl': image_url}
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
            dir_path = os.path.join(curr_dir, "raw_data/"+film['uniqueid'])
            os.mkdir(dir_path)
        except FileExistsError:
                pass
        with open(os.path.join(dir_path, "data.json"), "w") as write_file:
            json.dump(film, write_file, indent=4)
        image_url = film['imageurl']
        urllib.request.urlretrieve(image_url, os.path.join(dir_path, "poster.jpg"))

def check_rescrape(link):
    """Checks if the data from a given link has been scraped or not
    
    Parameters
    ----------
    link: str
        The link from which data will be scraped

    Returns
    -------
    bool
        True if the link has already been scraped

    """
    engine = db.create_engine(f"{DATABASE_TYPE}+{DBAPI}://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}")
    connection = engine.connect()
    metadata = db.MetaData()
    films = db.Table('films', metadata, autoload_with=engine)
    query = db.select(films.columns.friendlyid)
    ResultSet = connection.execute(query).fetchall()
    for id in ResultSet:
        if link[:38] in id:
            return True
    return False

def load_data_from_local_computer(list_of_dict_of_film):
    """Loads any data currently saved on the local computer
    
    Parameters
    ----------
    list_of_dict_of_film: list of dict
        The list of dictionaries of film data that is currently stored in the environment

    Returns
    -------
    list_of_dict_of_film: list of dict
        An updated version of the parameter passed in, now containing the data that was stored locally

    """
    curr_dir = os.getcwd()
    dir_list = []
    path_of_the_directory= os.path.join(curr_dir, 'raw_data')
    for dir_name in os.listdir(path_of_the_directory):
        if "." not in dir_name:
            f = os.path.join(path_of_the_directory,dir_name)
            filename = os.path.join(f,'data.json')
            if os.path.isfile(filename):
                dir_list.append(filename)
    for file in dir_list:
        with open(file, 'r') as json_file:
            json_load = json.load(json_file)
        list_of_dict_of_film.append(json_load)
    return list_of_dict_of_film

def scrape_data():
    """Scrapes the data using Selenium Chrome Driver

    Returns
    -------
    new_list_dict: list of dict
        A list of dictionaries of film data that has just been scraped

    """
    driver = IMDbScraper()
    driver.load()
    big_list = []
    while len(big_list) < 10:
        big_list.extend(driver.get_links())
        for index, item in enumerate(big_list[1:]):
            for i in range(index+1):
                if item[:38] == big_list[i][:38]:
                    del big_list[index+1]
                    break
        driver.next()
    try:
        os.mkdir(os.path.join(curr_dir, "raw_data"))
    except FileExistsError:
        pass
    new_list_dict = driver.crawl(big_list)
    driver.exit()
    return new_list_dict

def upload_data_to_bucket(list_of_dict_of_film):
    """Uploads data currently stored in environment to an AWS S3 Bucket

    Parameters
    ----------
    list_of_dict_of_film: list of dict
        The list of dictionaries of film data that is currently stored in the environment

    """
    curr_dir = os.getcwd()
    try:
        os.mkdir(os.path.join(curr_dir, "tmp"))
    except FileExistsError:
        pass
    for film in list_of_dict_of_film:
        if not upl.folder_exists(film["uniqueid"]):
            filepath = os.path.join(curr_dir, "tmp")
            with open(os.path.join(filepath, "data.json"), "w") as write_file:
                json.dump(film, write_file, indent=4)
            urllib.request.urlretrieve(film["imageurl"], os.path.join(filepath, "poster.jpg"))
            upl.create_bucket_directory(film["uniqueid"])
            upl.upload_to_bucket(os.path.join(filepath, "data.json"), film["uniqueid"]+"/data.json")
            upl.upload_to_bucket(os.path.join(filepath, "poster.jpg"), film["uniqueid"]+"/poster.jpg")
    
def upload_data_to_rds():
    """Uploads data currently stored in environment to an AWS RDS
    """
    engine = db.create_engine(f"{DATABASE_TYPE}+{DBAPI}://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}")
    connection = engine.connect()
    metadata = db.MetaData()
    films = db.Table('films', metadata, autoload=True, autoload_with=engine)
    query = db.insert(films)
    values_list = list_dict_film
    connection.execute(query,values_list)

if __name__ == "__main__":
    curr_dir = os.getcwd()
    list_dict_film = []
    while True:
        print("1. Load Data")
        print("2. Scrape Data")
        print("3. Download Data")
        print("4. Upload to Bucket")
        print("5. Upload to RDS")
        print("0. Quit")
        choice = input("Choose an option from above: ")
        if choice == "1":
            list_dict_film = load_data_from_local_computer(list_dict_film)
        elif choice == "2":
            list_dict_film.extend(scrape_data())
        elif choice == "3":
            download_data(list_dict_film)
        elif choice == "4":
            upload_data_to_bucket(list_dict_film)
        elif choice == "5":
            upload_data_to_rds()
        elif choice == "0":
            break
