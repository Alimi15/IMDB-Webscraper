# IMDB-Webscraper

## Milestone 1

Created a webscraper class using Selenium with methods to cover all necessary funtionality to navigate the webpage and collect data. The website used was IMDB and the data was collected from the top 150 best rated superhero feature films. Getting the description for each film was attempted but the xpath for where the description is contained seems to vary depending on length of description and size of window.

```python
from selenium.webdriver.common.by import By
from selenium import webdriver
import time

class IMDBScraper:

    def __init__(self):
        self.session = webdriver.Chrome()
        self.URL = "https://www.imdb.com/search/keyword/?keywords=superhero&pf_rd_m=A2FGELUUNOQJNL&pf_rd_p=a581b14c-5a82-4e29-9cf8-54f909ced9e1&pf_rd_r=WCKJ24NKVMM6G468NPWT&pf_rd_s=center-5&pf_rd_t=15051&pf_rd_i=genre&ref_=kw_ref_typ&mode=detail&page=1&sort=user_rating,desc&title_type=movie"

    def load(self):
        driver = self.session.get(self.URL)
        return driver

    def get_links(d: webdriver.Chrome) -> list:
        film_container = d.session.find_element(By.XPATH, '//*[@class="lister-list"]')
        film_list = film_container.find_elements(By.XPATH, './div')
        link_list = []

        for film in film_list:
            a_tag = film.find_element(By.TAG_NAME, 'a')
            link = a_tag.get_attribute('href')
            link_list.append(link)

        return link_list
    
    def crawl(d: webdriver.Chrome):
        for link in big_list:
            try:
                time.sleep(2)
                d.session.get(link)
                time.sleep(2)
                name = d.session.find_element(By.XPATH, '//h1[@data-testid="hero-title-block__title"]').text
                dict_properties['Name'].append(name)
                rating = d.session.find_element(By.XPATH, '//span[@class="sc-7ab21ed2-1 jGRxWM"]').text
                dict_properties['Rating'].append(rating)
                li_tag = d.session.find_elements(By.XPATH, '//li[@class="ipc-inline-list__item ipc-chip__text"]')
                genres =[]
                for li in li_tag:
                    genres.append(li.text)
                dict_properties['Genres'].append(genres)
                year = d.session.find_element(By.XPATH, '//a[@class="ipc-link ipc-link--baseAlt ipc-link--inherit-color sc-8c396aa2-1 WIUyh"]').text
                dict_properties['Year'].append(year)
                # if d.session.find_elements(By.XPATH, '//a[@data-testid="plot-read-all-link"]').Count() > 0:
                #     a_tag = d.session.find_element(By.XPATH, '//a[@data-testid="plot-read-all-link"]')
                #     read_all_link = a_tag.get_attribute('href')
                #     d.session.get(read_all_link)
                #     description = d.session.find_element(By.XPATH, '//li[@id="summary-po6521717"]//p').text
                # else:
                #     description = d.session.find_element(By.XPATH, '//div[@data-testid="plot"//span').text
                # print(description)
                # dict_properties['Description'].append(description)
            except:
                pass

    def next(d: webdriver.Chrome):
        next_button = d.session.find_element(By.XPATH, '//a[@class="lister-page-next next-page"]')
        next_link = next_button.get_attribute('href')
        d.session.get(next_link)

    def exit(d: webdriver.Chrome):
        d.session.quit()

if __name__ == "__main__":
    driver = IMDBScraper()
    driver.load()
    big_list = []
    dict_properties = {'Name': [], 'Rating': [], 'Genres': [], 'Year': []}
    for i in range(3):
        big_list.extend(driver.get_links())
        driver.next()
    driver.crawl()
    driver.exit()
```
