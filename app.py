import os
import requests
from bs4 import BeautifulSoup
from flask import Flask, request
from flask_cors import CORS

app = Flask(__name__)

# Configure CORS to allow requests only from www.movielink.xyz and https://movizart.blogspot.com/
cors = CORS(app, resources={r"/": {"origins": ["https://www.movielink.xyz", "https://movizart.blogspot.com/"]}})

@app.route('/')
def scrape_video_page():
    try:
        # Get the video URL from the query parameters
        video_url = request.args.get('video_url')

        if not video_url:
            return "Please provide a video URL by appending ?video_url=YOUR_URL to the URL."

        # Make a request to the video URL
        response = requests.get(video_url)
        response.raise_for_status()  # Raise an exception for 4xx and 5xx status codes

        video_page = BeautifulSoup(response.text, 'html.parser')

        # Find the div element with class "download-links-div"
        download_links_div = video_page.find('div', class_='download-links-div')

        if download_links_div:
            # Add a 'style' attribute to set 'text-align: center'
            download_links_div['style'] = 'text-align: center'

            # Remove all <img> tags within the "download-links-div"
            for img_tag in download_links_div.find_all('img'):
                img_tag.extract()

            # Find all <a> tags within the "download-links-div" and extract relevant information
            items = []
            for a_tag in download_links_div.find_all('a', class_='btn'):
                title = a_tag.find_previous('h4').get_text()
                language = a_tag.find_previous('span').get_text()
                quality = a_tag.find_previous('h4').get_text()
                link = a_tag['href']
                items.append({'title': title, 'language': language, 'quality': quality, 'link': link})

            # Create an HTML response directly in Python
            html_response = "<html><body>"
            for item in items:
                html_response += f"<h4>{item['title']}<span>{item['language']}</span>{item['quality']}</h4>"
                html_response += f"<div class='downloads-btns-div'><a class='btn' href='{item['link']}' rel='nofollow noopener noreferrer' target='_blank'>Download Links</a></div>"
            html_response += "</body></html>"

            return html_response
        else:
            return "Could not find the 'download-links-div' element."
    except requests.exceptions.RequestException as e:
        return f"Failed to retrieve the video page. Error: {str(e)}"
    except Exception as e:
        return f"An error occurred: {str(e)}"

if __name__ == '__main__':
    # Use the PORT environment variable provided by Heroku, or default to 5000 if running locally
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
