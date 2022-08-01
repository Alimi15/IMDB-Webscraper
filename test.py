import unittest
from scraper import scraper
import os.path

class WebscraperTestCase(unittest.TestCase):

    def test_load(self):
        driver = scraper.IMDbScraper()
        driver.load()
        current_url = driver.session.current_url
        test_string = current_url.startswith("https://www.imdb.com/search/keyword/?keywords=superhero")
        driver.exit()
        self.assertTrue(test_string)

    def test_get_links_returns_list(self):
        driver = scraper.IMDbScraper()
        driver.load()
        test_list = driver.get_links()
        driver.exit()
        self.assertIsInstance(test_list, list)

    def test_get_links_returns_list_of_str(self):
        driver = scraper.IMDbScraper()
        driver.load()
        test_list = driver.get_links()
        driver.exit()
        test_url = True
        for element in test_list:
            if isinstance(element, str):
                if not element.startswith('https://www.imdb.com/title/'):
                    test_url = False
            else:
                test_url = False
        self.assertTrue(test_url)

    def test_next(self):
        driver = scraper.IMDbScraper()
        driver.load()
        driver.next()
        current_url = driver.session.current_url
        driver.exit()
        test_string = current_url.startswith("https://www.imdb.com/search/")
        self.assertTrue(test_string)

    def test_crawl(self):
        driver = scraper.IMDbScraper()
        driver.load()
        links = ["https://www.imdb.com/title/tt9419884/", "https://www.imdb.com/title/tt10648342/"]
        list_dict_film = driver.crawl(links)
        driver.exit()
        dict_film1 = {'Unique ID': list_dict_film[0]['Unique ID'], 'ID': links[0], 'Name': 'Doctor Strange in the Multiverse of Madness', 'Rating': '7.0', 'Year': '2022', 'Image URL': 'https://m.media-amazon.com/images/M/MV5BNWM0ZGJlMzMtZmYwMi00NzI3LTgzMzMtNjMzNjliNDRmZmFlXkEyXkFqcGdeQXVyMTM1MTE1NDMx._V1_QL75_UX190_CR0,0,190,281_.jpg'}
        dict_film2 = {'Unique ID': list_dict_film[1]['Unique ID'], 'ID': links[1], 'Name': 'Thor: Love and Thunder', 'Rating': '6.8', 'Year': '2022', 'Image URL': 'https://m.media-amazon.com/images/M/MV5BMmExZTlmNGMtMTVhYy00N2U5LTg2MzYtNThjNDM2YjM4YjRhXkEyXkFqcGdeQXVyNTA3MTU2MjE@._V1_QL75_UX190_CR0,0,190,281_.jpg'}
        list_dict = [dict_film1, dict_film2]
        self.assertEqual(list_dict_film, list_dict)
        

    def test_download_images(self):
        test_dict = [{'Unique ID': 'test', 'Image URL': 'https://m.media-amazon.com/images/M/MV5BMmExZTlmNGMtMTVhYy00N2U5LTg2MzYtNThjNDM2YjM4YjRhXkEyXkFqcGdeQXVyNTA3MTU2MjE@._V1_QL75_UX380_CR0,0,380,562_.jpg'}]
        try:       
            os.mkdir("/Users/aliilt/Documents/IMDB-Webscraper/raw_data/test")
        except FileExistsError:
            pass
        scraper.download_images(test_dict)
        self.assertTrue(os.path.exists('/Users/aliilt/Documents/IMDB-Webscraper/raw_data/test/poster.jpg'))


if __name__ == '__main__':
    unittest.main()