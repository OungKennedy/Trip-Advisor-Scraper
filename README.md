# Trip-Advisor-Scraper
A website scraper for trip advisor

Program name: tascraper.py

  The program refers to a list of url, and scrapes information off the pages.
The data is then written to a csv file , for easy readability by excel, and a database file for use in SQL database handling. (database table name is ‘reviews’)
	
  The information is split into the hotel name, subject of review, username, review text, date, home location of user, and review id. 

	Currently the program is only scraping from a provided list of url. Review text is also incomplete due to the nature of coding of webpage, making it cumbersome to scrape full review text. 
