from seleniumbase import SB
from bs4 import BeautifulSoup
import time
import csv

csv_file = 'scraped_data.csv'

def extract_links(content):
    soup = BeautifulSoup(content, "html.parser")
    articles = soup.find_all('article', class_='GTuVU XJlaI')
    links = []
    for article in articles:
        a_tag = article.find('a', href=True)
        if a_tag:
            links.append('https://www.tripadvisor.it' + a_tag['href'])
    return links

def get_all_links():
    all_links = []
    for x in range(0, 16001, 30):
        url = f'https://www.tripadvisor.it/Attractions-g187829-Activities-oa{x}-Lombardy.html'
        with SB(uc=True, test=True) as sb:
            sb.open(url)
            content = sb.get_page_source()
        if content:
            links = extract_links(content)
            print(f"Extracted {len(links)} links from page {x}")
            all_links.extend(links)
        else:
            break
        time.sleep(2)
    with open('extracted_links.txt', 'w') as file:
        for link in all_links:
            file.write(f"{link}\n")

def scrap_comments(soup):
    comments = []
    review_elements = soup.find_all('div', class_='_c')
    for review_element in review_elements:
        comment_element = review_element.find('div', class_='yCeTE')  #
        if comment_element:
            comment = comment_element.get_text(strip=True)
        else:
            comment = "N/A"
        comments.append(comment)
    return comments


def get_data(link):
    with SB(uc=True, test=True) as sb:
        sb.open(link)
        content = sb.get_page_source()
    if content:
        soup = BeautifulSoup(content, "html.parser")
        try:
            name = soup.find('h1', class_='biGQs _P fiohW eIegw').text.strip()
        except AttributeError:
            name = "N/A"
        try:
            review = soup.find('div', class_='biGQs _P fiohW hzzSG uuBRH').text.strip()
        except AttributeError:
            review = "N/A"
        try:
            nb_reviews = soup.find('span', class_='biGQs _P pZUbB KxBGd').text.strip()
        except AttributeError:
            nb_reviews = "N/A"
        try:
            location = soup.find('span', class_='biGQs _P XWJSj Wb').get_text(strip=True)
        except AttributeError:
            location = "N/A"
        try:
            Category = soup.find('span', class_='eojVo').get_text(strip=True)
        except AttributeError:
            Category = "N/A"
        return [name, review, nb_reviews, location, Category, link]
    else:
        print(f"Unable to fetch content from {link}")
        return None

def main():
    get_all_links()
    with open('extracted_links.txt', 'r') as file:
        links_from_file = file.readlines()
    for link in links_from_file:
        with open(csv_file, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            try:
                data = get_data(link.strip())
                if data:
                    writer.writerow(data)
                    print(f"Scraped data: {data}")  # Print each scraped data instantly
            except Exception as e:
                print(f"Error scraping {link}: {e}")

if __name__ == "__main__":
    main()
