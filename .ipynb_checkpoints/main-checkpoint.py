from flask import Flask, jsonify, request
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import html
import json

app = Flask(__name__)

# main DF to use
df = pd.DataFrame()

# MadGrades db
with open("all_courses.json", 'r', encoding='utf-8') as file:
    courses = json.load(file)    

# Attempt at using MadGrades API 
API_TOKEN = "9766d059e02f47c4a5fda3ccd4b83eca"

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
            
                # old pattern: unsure why 0-9 was in there
                # pattern = r"([A-Za-z&\-\/\s0-9]+)\s*(\d+)\s*—\s*(.+)"
            
            pattern = r"([A-Za-z&\-\/\s]+)(\d+)\s*[-—]\s*(.+)"
            match = re.match(pattern, course_title)
            #print(course_title)
            
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
                
            # EXTRAS
            course_extras = course.find('div', class_='cb-extras')
            #print(course_extras)
            course_extras = course.find('div', class_='cb-extras')
            if course_extras:
                extras = []
                for extra in course_extras.find_all('p', class_='courseblockextra noindent clearfix'):
                    label = extra.find('span', class_='cbextra-label')
                    data = extra.find('span', class_='cbextra-data')
                    if label and data:
                        #print(label.text.strip())
                        label_text = label.text.strip()
                        if label_text != "Learning Outcomes:":  # Exclude specific extras
                            extras.append(f"<strong>{label_text}</strong> {data.text.strip()}")
                course_details["EXTRAS"] = " \n ".join(extras)
            else:
                course_details["EXTRAS"] = "None"
                
            # DESC 
            course_details["DESCRIPTION"] = course.find("p", class_="courseblockdesc noindent").text.strip()
           
            # append course
            courses.append(course_details)
        
        # return courses
        return pd.DataFrame(courses)
        
    else:
        print("Not in DataFrame")
        return pd.DataFrame()
    
def get_madgrades_course(abbrev, code):
    """
    Searches for courses in the 'courses' list that have a subject with the given abbreviation
    and whose course number matches the given code. Returns course that matches

    Parameters:
    abbrev (str): The abbreviation of the subject to search for.
    code (str or int): The course number to match against the course's number.

    Returns:
    dict: First item of a list of courses where a matching subject with the given abbreviation and code is found.
    """
    found_courses = []
    
    for course in courses:
        number = course.get("number")
        #print(abbrev, code)
        #print(course)
        for subject in course.get('subjects'):
            if int(number) == int(code) and subject.get("abbreviation") == abbrev:
                found_courses.append(course)
                break  
                
    return found_courses[0]

def get_madgrades_grades(course):
    grades_url = course["url"] + "/grades"
    #print(grades_url)
    headers = {
        'Authorization': 'Token token=9766d059e02f47c4a5fda3ccd4b83eca'
    }
    response = requests.get(grades_url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        print(response.status_code)
        return

def filter_grades(grades):
    """
    Barebones implementation of a filtering system to remove unneeded counts from percentages
    """
    filtered = {}
    filtered["aCount"] = grades["aCount"]
    filtered["abCount"] = grades["abCount"]
    filtered["bCount"] = grades["bCount"]
    filtered["bcCount"] = grades["bcCount"]
    filtered["cCount"] = grades["cCount"]
    filtered["dCount"] = grades["dCount"]
    filtered["fCount"] = grades["fCount"]
    
    return filtered

def calculate_gpa(grades):
    """
    Calculate GPA using the GPA scale provided by UW-Madison, using a filtered list ONLY containing the letter
    grades
    """
    # Define the grade points
    grade_points = {
        'aCount': 4.0,
        'abCount': 3.5,
        'bCount': 3.0,
        'bcCount': 2.5,
        'cCount': 2.0,
        'dCount': 1.0,
        'fCount': 0.0
    }

    # Calculate the total weighted points and the total count of grades
    total_points = 0
    total_count = 0
    
    for grade, count in grades.items():
        total_points += count * grade_points[grade]
        total_count += count
    
    # Calculate GPA
    gpa = total_points / total_count if total_count > 0 else 0
    return round(gpa, 2)
    
@app.route('/')
def home():
    global df
    scrape_departments_and_courses()
    
    with open("homepage.html") as f:
        html = f.read()
        
    # provide dept and id as thats all I need here for now
    departments = df.to_dict(orient="records")
    #print(df)

    department_list = ""
    
    # This will be the 'format' of each dept
    for dept in departments:
        department_list += f"""
        <li><a href='/department/{dept["ID"]}'>{dept["DEPARTMENT"]}</a></li>
        """
    html = html.replace("{{ departments }}", department_list)
    html = html.replace("{{ department amount }}", str(len(departments)))
    
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
        extras_list = course["EXTRAS"].split(" \n ") if course["EXTRAS"] != "None" else []
        
        # Convert the extras into a li
        extras_html = ""
        if extras_list:
            extras_html = "<ul>" + "".join(f"<li>{extra}</li>" for extra in extras_list) + "</ul>"
        else:
            extras_html = "<em>No additional information available.</em>"
            
        course_list += f"""
            <h3><strong>{course["ABBREV"]}</strong>: {course["NAME"]} </h3>
            <strong>Credits:</strong> {course['CREDITS']} <br> 
            <strong>Description:</strong> {course["DESCRIPTION"]} <br> 
            <br>
            <strong> More information </strong> <br>
            {extras_html} 
            <button onclick="fetchMadGrades('{department_abbrev}', {course['ID']})">Load MadGrades Data</button>
            <div id="madgrades-{course['ID']}"></div>
        """

    # Load the department template
    with open("department.html") as f:
        html = f.read()

    # Replace placeholders in the template
    html = html.replace("{{ department_name }}", department_name)
    html = html.replace("{{ course_list }}", course_list)
    html = html.replace("{{ courses amount }}", str(len(courses)))

    return html

# Way to confirm that scraping worked - DEBUG
@app.route('/scrape', methods=['GET'])
def scrape():
    scrape_departments_and_courses()
    return jsonify({"message": "Scraping complete.", "departments": len(df)})

@app.route('/fetch_madgrades/<abbrev>/<int:code>', methods=['GET'])
def fetch_madgrades(abbrev, code):
    #print("abbreviation " + str(abbrev))
    #print("code " + str(code))
    try:
        # Fetch the course from the list
        madgrades_course = get_madgrades_course(abbrev, code)
        madgrades_grades = get_madgrades_grades(madgrades_course)

        if madgrades_grades and "cumulative" in madgrades_grades:
            grade_distribution = {}
            for grade in madgrades_grades["cumulative"]:
                total = madgrades_grades["cumulative"].get("total", 1)
                score = round((madgrades_grades["cumulative"][grade] / total) * 100, 2) if total > 0 else 0
                grade_distribution[grade] = score

            filtered_grade_distribution = filter_grades(grade_distribution)
            madgrades_gpa = calculate_gpa(filtered_grade_distribution)

            response_data = {
                "grades": filtered_grade_distribution,
                "gpa": madgrades_gpa
            }
            return jsonify(response_data)
        else:
            return jsonify({"message": "No MadGrades data available."}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    
# SOURCE 2: setup for Flask site
if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, threaded=False) # don't change this line!
# NOTE: app.run never returns (it runs for ever, unless you kill the process)
# Thus, don't define any functions after the app.run call, because it will
# never get that far.
