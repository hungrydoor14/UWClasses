# Description
UWClasses is a personal project aimed at building a web application that scrapes and displays department and course information for the University of Wisconsin-Madison. Users can browse a list of departments and view the courses offered by each department, based on the latest scraped data.

# Goals
This project, started on November 25, 2024, is a learning opportunity to:
- Gain experience with Flask for web development.
- Learn and apply web scraping techniques.
- Practice HTML for building a basic user interface.

# Features
- Homepage (/): Displays a list of all departments at UW-Madison.
- Department Page (/department/DEPARTMENT-ID): Shows available courses for a selected department based on scraped data.
- Debug Page (/scrape): Used to verify the success of the scraping process.

# Routes
| **Route**                 | **Description**                                   | **Example Usage**       |
|---------------------------|:------------------------------------------------:|------------------------:|
| `/`                       | Displays a list of all departments.              | Visit the homepage.     |
| `/department/DEPARTMENT-ID` | Shows courses for a specific department.        | `/department/comp_sci`        |
| `/scrape`                 | Verifies if scraping is successful.   

## Credits
Every source will be listed below, and a comment highlighting what source was used at the time will be on the files.
- Source 1 : https://stackoverflow.com/questions/2360598/how-do-i-unescape-html-entities-in-a-string-in-python-3-1/3796917
- Source 2 : Gurmail Singh, class example on Flask (CS320, Fa2024)