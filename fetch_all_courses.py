import requests
import json

"""
    THIS SHOULD NOT BE DONE BY ANYONE IN THE WEBSITE. THIS WILL TAKE A FEW MINUTES, AND GATHERS ABOUT 11K ENTRIES
    FROM ALL OF UW-MADISON HISTORY!!!
"""

def fetch_all_courses(base_url, token):
    # List to store all course data
    all_courses = []
    
    # Start with the first page of the courses
    url = base_url
    headers = {
        'Authorization': f'Token token={token}'
    }

    while url:
        # Make a request to the current page URL
        #print(f"Requesting: {url}")  
        response = requests.get(url, headers=headers)
        response.raise_for_status()  
        
        # Parse the JSON response
        data = response.json()
        
        # Append the 'results' (list of courses) to the all_courses list
        all_courses.extend(data.get('results', []))
        
        # Update the URL to the next page, if it exists
        url = data.get('nextPageUrl')  # This assumes the API uses 'next' as the key for pagination
        
        # Debug print to check if the next page URL is correct
        #print("Next page URL:", url)
    
    # Save the collected course data to a JSON file
    with open('all_courses.json', 'w', encoding='utf-8') as file:
        json.dump(all_courses, file, ensure_ascii=False, indent=4)
    
    print(f"Fetched {len(all_courses)} courses and saved to 'all_courses.json'")
    return all_courses

#base_url = 'https://api.madgrades.com/v1/courses'
#all_courses = fetch_all_courses(base_url, TOKEN_I_WON'T_GIVE_U)