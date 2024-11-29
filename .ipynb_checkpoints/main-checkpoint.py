from flask import Flask, jsonify, request
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import html

app = Flask(__name__)

# DF to use
df = pd.DataFrame()

"""
SOURCES USED:
    Source 1 : https://stackoverflow.com/questions/2360598/how-do-i-unescape-html-entities-in-a-string-in-python-3-1/3796917
    Source 2 : Gurmail Singh, class example on Flask

"""

def scrape_departments_and_courses():
    """
    This will grab the info from the "courses" site, which will be the departments that the classes
    go into. 
    """
    global df
    url = "https://guide.wisc.edu/courses/"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Get the lists (ul) from the website
        # The lists are inside <div id="atozindex"> == $0

    data = [] 

    atoz_div = soup.find('div', id='atozindex')

    # Gathers id, abbreviations, name
    if atoz_div:
        ul_elements = atoz_div.find_all('ul')
        # The site is set up from A-Z with each letter having a ul for the courses
        for ul in ul_elements:
            items = ul.find_all('li')
            for item in items:
                # this will grab the info inside the href (that holds name and course abbreviations)
                    # <li><a href="/courses/acct_i_s/">Accounting and Information Systems (ACCT I S)</a></li>
                pattern = r'<li><a href="/courses/(.*?)/">(.+?) \(([^)]+)\)</a></li>'
                match = re.match(pattern, str(item))
                #print(item)            

                if match:
                    dep_id = match.group(1) # used for website nav
                    dep_name = match.group(2) # naming 
                    dep_abbrev = match.group(3) # full name

                    # SOURCE 1: Fix issue with amps like "ANAT&amp;PHY"
                    dep_abbrev = html.unescape(dep_abbrev)
                    dep_name = html.unescape(dep_name)
                    
                    dep_url = f"https://guide.wisc.edu/courses/{dep_id}/"

                    data.append({"ID" : dep_id, "ABBREV": dep_abbrev, "DEPARTMENT": dep_name, "URL" : dep_url})

    df = pd.DataFrame(data)
    
def gather_courses(department):
    """
    Gathers courses for the given department from its URL.

    Parameters:
        department (str): Name of the department to scrape.

    Returns:
        DataFrame: Contains details of courses for the specified department.
    """
    # First, check if the department name is actually in the datafram
    if department in df["DEPARTMENT"].values:
        info = df.loc[df["DEPARTMENT"] == department]
                
        # Get the html loaded from new url
        url = info["URL"].iloc[0]
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        courses = []
        course_blocks = soup.find_all(class_="courseblock")
        
        for course in course_blocks:
            course_details = {}
            
            # TITLE and ID 
            course_title = course.find('p', class_='courseblocktitle').text.strip()
            
            # found issue with Zero Width Space, this is how to fix
            course_title = course_title.replace("\u200B", "")    
            
            pattern = r"([A-Za-z&\/\s0-9]+)\s*(\d{3})\s*—\s*(.+)"
            match = re.match(pattern, course_title)
            
            if match:
                #course_details["DEP_COURSE"] = match.group(1)
                course_details["ABBREV"] = str(info["ABBREV"].iloc[0]) + " " + match.group(2)
                course_details["NAME"] = match.group(3)
                course_details["ID"] = int(match.group(2))
            
            # CREDITS (range)
            course_credits = course.find('p', class_='courseblockcredits').text.strip()
            pattern = r"([0-9\-]+)\scredit"
            match = re.match(pattern, course_credits)
            if match:
                course_details["CREDITS"] = match.group(1)
                
            # More info section
                # Load "cb-extras" class from course
            course_extras = course.find_all('p', class_='courseblockextra noindent clearfix')
            #print(course_extras)
                
            # DESC - Not sure if I should include in df
            course_details["DESCRIPTION"] = course.find("p", class_="courseblockdesc noindent").text.strip()
           
            # append course
            courses.append(course_details)
        
        # return courses
        return pd.DataFrame(courses)
        
    else:
        print("Not in DataFrame")
    
@app.route('/')
def home():
    global df
    scrape_departments_and_courses()
    
    with open("homepage.html") as f:
        html = f.read()
        
    # provide dept and id as thats all I need here for now
    departments = df.to_dict(orient="records")
    print(df)

    department_list = ""
    
    # This will be the 'format' of each dept
    for dept in departments:
        department_list += f"""
        <li><a href='/department/{dept["ID"]}'>{dept["DEPARTMENT"]}</a></li>
        """
    html = html.replace("{{ departments }}", department_list)
    
    return html

@app.route('/department/<dept_id>')
def department_page(dept_id):
    global df

    # Ensure scrape_departments_and_courses() is called
    if df.empty:
        scrape_departments_and_courses()

    # Check if the department ID exists in the DataFrame
    department_info = df.loc[df["ID"] == dept_id]
    if department_info.empty:
        return f"Error: Department with ID '{dept_id}' not found.", 404

    # Extract department details
    department_name = department_info["DEPARTMENT"].iloc[0]
    department_abbrev = department_info["ABBREV"].iloc[0]

    # Scrape courses for the department
    courses = gather_courses(department_name)

    # Create the course list HTML
    course_list = ""
    for _, course in courses.iterrows():
        course_list += f"""
        <li>
            <strong>{course['ABBREV']}</strong>: {course['NAME']} ({course['CREDITS']} credits)
        </li>
        """

    # Load the department template
    with open("department.html") as f:
        html = f.read()

    # Replace placeholders in the template
    html = html.replace("{{ department_name }}", department_name)
    html = html.replace("{{ course_list }}", course_list)

    return html

# Way to confirm that scraping worked - DEBUG
@app.route('/scrape', methods=['GET'])
def scrape():
    scrape_departments_and_courses()
    return jsonify({"message": "Scraping complete.", "departments": len(df)})
    
# SOURCE 2: setup for Flask site
if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, threaded=False) # don't change this line!
# NOTE: app.run never returns (it runs for ever, unless you kill the process)
# Thus, don't define any functions after the app.run call, because it will
# never get that far.
