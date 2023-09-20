import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def scrape_video_page():
    # Get the video URL from the query parameters
    video_url = request.args.get('video_url')

    if not video_url:
        return "Please provide a video URL by appending ?video_url=YOUR_URL to the URL."

    # Make a request to the video URL
    response = requests.get(video_url)

    if response.status_code == 200:
        video_page = BeautifulSoup(response.text, 'html.parser')

        # Find the div element with class "download-links-div"
        download_links_div = video_page.find('div', class_='download-links-div')

        if download_links_div:
            # Find all <a> tags within the "download-links-div" and extract relevant information
            items = []
            for a_tag in download_links_div.find_all('a', class_='btn'):
                title = a_tag.find_previous('h4').get_text()
                language = a_tag.find_previous('span').get_text()
                quality = a_tag.find_previous('h4').get_text()
                link = a_tag['href']
                items.append({'title': title, 'language': language, 'quality': quality, 'link': link})

            # Render the HTML template with the extracted data
            return render_template('template.html', items=items)
        else:
            return "Could not find the 'download-links-div' element."
    else:
        return "Failed to retrieve the video page."

if __name__ == '__main__':
    app.run()
