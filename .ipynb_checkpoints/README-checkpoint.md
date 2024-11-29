# UWClasses

## Description
This is a personal project where I implement a website scraper that gathers all departments for UW-Madison, and selecting one of them will fetch the classes tied to the department. 

Project started November 25th, 2024, and worked on whenever I have free time. My goal is to learn more about Flask, website scraping, and basic HTML usage. 

## Routes
### /
Homepage. Will have a list of all available departments UW-Madison has. 

### /department/DEPARTMENT-ID
Will have the specific department's courses that are available as of time of scraping. 

### /scrape
Debug - used to see if scraping was done correctly or not. 

## Credits
Every source will be listed below:
- Source 1 : https://stackoverflow.com/questions/2360598/how-do-i-unescape-html-entities-in-a-string-in-python-3-1/3796917
- Source 2 : Gurmail Singh, class example on Flask (CS320, Fa2024)