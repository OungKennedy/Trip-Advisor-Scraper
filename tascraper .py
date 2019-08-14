from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup
import csv
import sqlite3
import os

url_list = ['https://www.tripadvisor.com.sg/Hotel_Review-g294265-d302294-Reviews-Pan_Pacific_Singapore-Singapore.html', 
'https://www.tripadvisor.com.sg/Hotel_Review-g294265-d306192-Reviews-PARKROYAL_on_Beach_Road-Singapore.html', 
'https://www.tripadvisor.com.sg/Hotel_Review-g294265-d300850-Reviews-Mandarin_Orchard_Singapore-Singapore.html']

def scrape_page(url):
    '''
    scrape_page downloads a given url and returns a list of reviews.
    '''
    page_html = download(url)
    data = parse(page_html)
    return data
def download(url):
    with uReq(url) as uClient:
        page_html = uClient.read()
    return page_html

def parse(page_html):
    page_soup = soup(page_html, 'html.parser')
    containers = page_soup.findAll('div',{'class':'review-container'})
    hotel_name = page_soup.findAll('div',{'class':'hotelDescription'})[0].h1.text
    reviews = []
    for container in containers:
        review = parse_container(container)
        reviews.append(review)
        reviews[-1].insert(0,hotel_name)

    return reviews 

def parse_container(container):

    subject = container.findAll('a',{'class': 'title'})[0].span.text
    
    username = container.findAll('div',{'class':'info_text'})[0].div.text
    
    review = container.findAll('div',{'class','entry'})[0].p.text
    #formatting reviews
    review = review.replace('\r\n','')
      
    if review[-4:] == 'More':
        review=review.rsplit('.',1)[0]

    date = container.findAll('span',{'class':'ratingDate'})[0]['title']

    try:
        location = container.findAll('div',{'class':'userLoc'})[0].strong.text
      
    except IndexError: # some users don't display location
        location = ''

    review_id = container['data-reviewid']
    return [subject, username, review, date, location, review_id]

def check_repeat(reader, review):
    for row in reader:
        if row[-1]==review[-1]:
            return True
    return False

def needs_header():
    with open('tareview.csv','r', encoding='utf-8-sig') as f:
        reader = csv.reader(f, delimiter=',', quoting=csv.QUOTE_MINIMAL)
        headers = ['hotel name', 'subject','username','review','date','location','review_id']
        return os.stat('tareview.csv').st_size==0 or next(reader)!=headers  
        
def check_csv_and_db():
    #checks for existing 'tareview.csv' and 'tareview.db', creates one if not present
    #check csv
    
    with open('tareview.csv','a', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f, delimiter = ',', quoting = csv.QUOTE_MINIMAL)
        headers = ['hotel name', 'subject','username','review','date','location','review_id']
        if needs_header():
            #detects and writes headers
            headers = ['hotel_name', 'subject','username','review','date','location','review_id']
            writer.writerow(headers)
    #check db        
    conn = sqlite3.connect('tareview.db')
    c = conn.cursor()
    #create table if none in place
    c.execute('''CREATE TABLE IF NOT EXISTS reviews
        (hotel TEXT, subject TEXT, username TEXT, review TEXT, date TEXT, location TEXT, id INTEGER)''')
    conn.close()


def main():
    check_csv_and_db()            
    for my_url in url_list:
        reviews = scrape_page(my_url)
        #read csv file
        with open('tareview.csv','r',newline='', encoding='utf-8-sig') as f:
            reader = csv.reader(f, delimiter = ',')

            #check csv file for repeat reviews
            final_review_list=[]
            for i in range(len(reviews)-1,-1,-1):
                if not check_repeat(reader, reviews[i]):
                    final_review_list.append(reviews[i])
                    

        #break if there are no new reviews
        if len(reviews) == 0:
            break
                    
        #write csv file                    
        with open('tareview.csv','a',newline='', encoding='utf-8-sig') as f:                                  
            writer = csv.writer(f, delimiter = ',', quoting = csv.QUOTE_MINIMAL)           
            writer.writerows(final_review_list)

        #write to database
        conn = sqlite3.connect('tareview.db')
        c = conn.cursor()
        #insert data into database
        c.executemany('INSERT INTO reviews VALUES (?,?,?,?,?,?,?)', final_review_list)
        conn.commit()
        conn.close()


if __name__ == '__main__':
    main()




