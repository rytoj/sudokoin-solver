import urllib

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import sudoku_handler
import tweet_handler
import re
import time

class Init:
    def __init__(self, website):
        self.driver = webdriver.Firefox()
        self.website = website
        self.close_timeout = 3

    def start_browser(self):
        self.driver.get(self.website)
        return driver

    def get_html(self):
        return self.driver.page_source

    def close(self):
        self.driver.close()


class Parse:
    def __init__(self, html):
        self.html = html

    def make_file_soup(self):
        """
        Create bsoup object from file or string
        """
        soup = BeautifulSoup(self.html, 'html.parser')
        return soup

    def make_soup(self):
        """
        Create bsoup object from url
        """
        req = urllib.request.Request(
            url,
            data=None,
            headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
            }
        )
        f = urllib.request.urlopen(self.html)
        soupdata = BeautifulSoup(f, "html.parser")
        return soupdata


def press_key(driver_, xpath,  msg):
    """
    Send message to forma field
    :param msg: text message
    """
    chat = driver_.find_element_by_xpath('//*[@id="{}"]'.format(xpath))
    chat.send_keys(msg)
    chat.send_keys(Keys.RETURN)


def get_sudoku_data():
    """
    Get sudoku data
    :return:
    """
    parser = Parse(html_data)
    parsed_html = parser.make_file_soup()
    result = ""
    sudoku_data = parsed_html.select("html body main form table.board tbody")[0]
    for rows in sudoku_data.find_all("tr"):
        for element in rows.find_all("td"):
            cell_value = element.text.strip()
            if not cell_value:
                cell_value = "."
            print(cell_value, end="")
            result += cell_value
        print()
        result += "\n"
    return result


def fill_form_data(firefox, xpath, key):
    twiter_username = firefox.driver.find_element_by_xpath(xpath)
    twiter_username.send_keys(key)


def get_url():
    """
    Find urls in text
    """
    urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
                      new_tweet)
    return urls


if __name__ == "__main__":

    twitter_account = 'sudokoin'
    while True:

        newTweets = tweet_handler.getNewTweets(twitter_account)
        if newTweets is not None:
            new_tweet = newTweets[0][2]
            date = newTweets[0][1]
            print("--NEW TWEET--: Date: {}\nText: {} ".format(date, new_tweet))
            urls = get_url()
            url = urls[0]
            try:
                driver = Init(url)
            except:
                print("Downaload firefox driver fromm \n https://github.com/mozilla/geckodriver/releases")
                raise
            firefox = driver.start_browser()
            html_data = driver.get_html()

            sudoku_file = "unsolved.txt"
            unsolved_sudoku_data = get_sudoku_data()
            with open(sudoku_file, 'w') as f:
                f.write(unsolved_sudoku_data)

            print("-" * 10)
            S = sudoku_handler.Sudoku(sudoku_file)
            S.process_all_sets()
            for cell in  S.cells:
                counter = 1
                while not cell.is_solved():
                    S.process_all_sets()
                    print(S)
                    print("Itteration {}: ".format(counter))
                    counter += 1
            counter = 0
            firt_row = True
            for element in  range(00,89):
                print(element)
                if element % 9 == 0 and element != 0:
                    counter += 1
                if element == 9:
                    cell_number = str(element + counter)
                    firt_row = False
                if len(str(element)) == 1 and firt_row:
                    cell_number = "0" + str(element)
                else:
                    cell_number = str(element+counter)
                if "90" in cell_number:
                    break
                if not firefox.driver.find_element_by_id("td{}".format(cell_number)).text:
                    firefox.driver.find_element_by_id("td{}".format(cell_number)).click()

                    cell_solution = str(S.cells[element])
                    firefox.driver.find_element_by_id("choice{}".format(cell_solution)).click()

            final_message = firefox.driver.find_element_by_xpath("/html/body/main/form/table[2]/thead/tr/td").text
            if final_message:
                if "claimed it first" in final_message:
                    print("This sudoku is claimed")
                    exit()
                if "Claim sudokoin" in final_message:
                    print("Claiming token")
                    # Claim token
                    firefox.driver.find_element_by_xpath("/html/body/main/form/table[2]/thead/tr/td/a").click()
                    fill_form_data(firefox, xpath='//*[@id="twitter"]',  key="La1kas")
                    fill_form_data(firefox, xpath='//*[@id="stellar"]',  key="GAETU2OVM5FZUUUDAVJEFCGTOEI2IJ25KCRBAUWJQXZEITSERR2ZGLCI")
                    firefox.driver.find_element_by_xpath('//*[@id="submit"]').click()
                    firefox.driver.close()
        else:
            tweet_handler.getNewTweets(twitter_account, latest=True)
        time_sleep = 3600
        print("Sleeping: {}".format(time_sleep))
        time.sleep(time_sleep)
