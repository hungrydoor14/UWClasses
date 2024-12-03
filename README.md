# Description
UWClasses is a personal project to build a web application that scrapes and displays department and course information for the University of Wisconsin-Madison. Users can browse a list of departments and view the courses offered by each department based on the latest scraped data. A click of a button will fetch grade data from MadGrades' API, if available, and present it to the user. 

The project began as a simple web scraper for UW-Madison's departments and courses and evolved to include integration with MadGrade's API, allowing users to gather detailed course information efficiently, without going to both websites. Originally, the scraper would access MadGrades automatically when opening the department site for every course, but this in turn made the site slow and unresponsive. After implementing a button to fetch only on the user's request, this was fixed. 

# Goals
This project, started on November 25, 2024, is a learning opportunity to:
- Gain experience with Flask for web development.
- Learn and apply web scraping techniques.
- Practice HTML for building a basic user interface.
- Practice using API with Python (using MadGrades API, see source 3).
- Produce my own json datasets for use on the project
- Produce scripts within HTML, combining knowledge from my previous CS classes.

# Features
Website features
- Homepage (/): Displays a list of all departments at UW-Madison.
- Department Page (/department/DEPARTMENT-ID): Shows available courses for a selected department based on scraped data. 
- Debug Page (/scrape): Used to verify the success of the scraping process.
- Course Madgrades Fetch (/fetch_madgrades/ABBREV/int:CODE): called when Madgrades button is pressed. Fetches info

Other features
- all_courses.json : JSON file produced by me holding MadGrade's dataset of all UW-Madison courses (as of Nov. 30, 2024)
- fetch_all_courses(base_url, token) : used to create all_courses.json
- MadGrades API implementation: Pressing a button will allow the user to fetch the information for the specific course

# Routes
| **Route**                 | **Description**                                   | **Example Usage**       |
|---------------------------|------------------------------------------------|------------------------|
| `/`                       | Displays a list of all departments.              | Visit the homepage.     |
| `/department/DEPARTMENT-ID` | Shows courses for a specific department.        | `/department/comp_sci`        |
| `/scrape`                 | Verifies if scraping is successful.   | `/scrape`               |
| `/fetch_madgrades/ABBREV/int:CODE` | Fetches MadGrades data for a specific course. | `/fetch_madgrades/COMP%20SCI/200` |

# Requirements
- Flask
- BeautifulSoup4
- Requests
- Pandas
- html
- json

# Notes
The use of MadGrades made the project go very slow, which is something I will try to improve later, perhaps by turning the entries I'm fetching into a JSON file, similarly to all_course.json. 

## Credits
Every source will be listed below, and a comment highlighting what source was used at the time will be on the files.
- **Source 1**: [StackOverflow: How do I unescape HTML entities in a string in Python 3.1?](https://stackoverflow.com/questions/2360598/how-do-i-unescape-html-entities-in-a-string-in-python-3-1/3796917)
- **Source 2**: Gurmail Singh, class example on Flask (CS320, Fa2024)
- **Source 3**: [MadGrade API](https://api.madgrades.com)
- **Source 4**: Javascript fetch exmaple from UW-Madison (CS571, Fa2024)