import base64
import requests
from google.cloud import vision

def fetch(url):
    return requests.get(url).content

def request(image):
    # request_body = [{"image":{"content":image},"features":[{"type":"LABEL_DETECTION"}]}]
    # r = requests.post("https://vision.googleapis.com/v1/images:annotate?key=AIzaSyBU-oXRg7qo5CTr_IJjYO24x84BSBlcYYs", data=request_body)
    # if r.status_code != 200:
    #     print("Error could fetching image labels: ", str(r.status_code))
    # response = r.json()
    # print(response)
    client = vision.Client()
    image = client.image(content=image)
    labels = image.detect_labels()
    tags = []
    for label in labels:
        tags.append(label.description)

    return tags

def generate_tags(urls):
    tags = []
    for url in urls:
        image = fetch(url)
        image_tags = request(image)
        for tag in image_tags:
            if tag not in tags:
                tags.append(tag)

    return tags
