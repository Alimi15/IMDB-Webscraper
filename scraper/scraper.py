from selenium.webdriver.common.by import By
from selenium import webdriver
import time
import uuid
import json
import os
import urllib.request

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
                time.sleep(2)
                unique_id = uuid.uuid4()
                name = d.session.find_element(By.XPATH, '//h1[@data-testid="hero-title-block__title"]').text
                rating = d.session.find_element(By.XPATH, '//span[@class="sc-7ab21ed2-1 jGRxWM"]').text
                year = d.session.find_element(By.XPATH, '//a[@class="ipc-link ipc-link--baseAlt ipc-link--inherit-color sc-8c396aa2-1 WIUyh"]').text
                image_tag = d.session.find_element(By.XPATH, '//img[@class="ipc-image"]')
                image_url = image_tag.get_attribute('src')
                dict_film = {'Unique ID': str(unique_id), 'ID': link, 'Name': name, 'Rating': rating, 'Year': year, 'Image URL': image_url}
                list_dict.append(dict_film)
                try:
                    os.mkdir("/Users/aliilt/Documents/IMDB-Webscraper/raw_data/"+str(unique_id))
                except FileExistsError:
                    pass
                with open("/Users/aliilt/Documents/IMDB-Webscraper/raw_data/"+str(unique_id)+"/data.json", "w") as write_file:
                    json.dump(dict_film, write_file, indent=4)
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

def download_images(list_dict):
    """Downloads the film poster using the image URL scraped
    
    Parameters
    ----------
    list_dict: list of dict
        List of dictionaries where data on each film is stored

    """
    for film in list_dict:
        url = film['Image URL']
        urllib.request.urlretrieve(url, "/Users/aliilt/Documents/IMDB-Webscraper/raw_data/"+film['Unique ID']+"/poster.jpg")

if __name__ == "__main__":
    driver = IMDbScraper()
    driver.load()
    big_list = []
    for i in range(3):
        big_list.extend(driver.get_links())
        driver.next()
    try:
        os.mkdir("/Users/aliilt/Documents/IMDB-Webscraper/raw_data")
    except FileExistsError:
        pass
    list_dict_film = driver.crawl(big_list)
    driver.exit()
    download_images(list_dict_film)