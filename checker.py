#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 24 15:46:28 2023

@author: odanylchenko
"""

import hashlib                                             #used to make md5 hash
import os                                                  #used to work with files
import requests                                            #used to get the web page
import json                                                #used to work with config files in JSON format
import re                                                  #used to change URL to something we can use as file name
from bs4 import BeautifulSoup                              #used to parse HTML and get the text out
from datetime import datetime                              #used to get date-time to timestamp files

config_file = "checker.json"                               #name of the config file we use

def send_slack_notification(webhook_url, message):         #function to send notification to slack web hook
    data = {
        "text": message
    }

    headers = {
        "Content-Type": "application/json"
    }

    response = requests.post(webhook_url, data=json.dumps(data), headers=headers)

    if response.status_code != 200:
        raise Exception(f"Error sending Slack notification: {response.text}")

def read_file(filename):                                    #function to read a file in a local directory
    current_directory = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_directory, filename)
    with open(file_path, 'r') as file:
        content = file.read()
    return content

def get_new_ps(old_content, content_to_save, header):      #compare old and new content to find new paragraphs
    slack_message = ''
    old_paragraphs = old_content.split('\n')
    new_paragraphs = content_to_save.split('\n')
    slack_message = str(header) + '\n'

    new_paragraphs_only = [paragraph for paragraph in new_paragraphs if paragraph not in old_paragraphs]
    if new_paragraphs_only:
        for paragraph in new_paragraphs_only:
            slack_message = slack_message + '\n' + paragraph
        slack_message = slack_message + '\n' + 'More details here: ' + url
# REMOVE COMMENT BELOW TO START SENDING THE SLACK NOTIFICATIONS
#       send_slack_notification(slack_webhook_url,slack_message)
        print(slack_message)
    else:
        print("No new paragraphs found in the file.")

if os.path.isfile(config_file):                             # Check for presence of the config file
    with open(config_file, 'r') as file:
        config_data = json.load(file)
        url = config_data["url"]
        div_class = config_data["div_class"]
        slack_webhook_url = config_data["slack_webhook_url"]
else:                                                       # File does not exist, prompt for information and write them to the config file
    url = input("What web page do you want to track?\n")
    div_class = input("What is the <div> class of the main content?\n")
    slack_webhook_url = input("What is the slack web hook you want to use for this notification?\n")

    config_data = {
        "url": url,
        "div_class": div_class,
        "slack_webhook_url": slack_webhook_url
    }

    with open(config_file, 'w') as file:
        json.dump(config_data, file)
        print("Data written to", config_file)

response = requests.get(url)                                  #gets content of the URL

if response.status_code == 200:                               #parses out main content and header of the page
    soup = BeautifulSoup(response.content, 'html.parser')
    main_content = soup.find('div', class_=div_class)
    header_raw = soup.find('title')
    header = header_raw.get_text()
    content_to_save = main_content.get_text()

file_name = re.sub(r'[^\w\-_.]', '', url)
old_md5_filename = file_name + '-md5.txt'                     #file name for the MD5 of the content received during latest check
latest_article = file_name + '-latest.txt'                       #content of the latest check

if os.path.isfile(latest_article):                               #check if the latest.txt file is there and make an empty one if not
    print()
else:
    with open(latest_article, 'w') as f:
        f.write("")

old_content = read_file(latest_article)                          #reads content of the latest check

if os.path.isfile(old_md5_filename):                          #reads MD5 of the latest check
    with open(old_md5_filename, 'r') as f:
        old_md5 = f.read().strip()


with open(latest_article, 'w') as f:                             #saves the content to the new latest check
    f.write(content_to_save)

with open(latest_article, 'rb') as f:                            #reads the new content and calculates md5 hash
    content_bytes = f.read()
    md5_hash = hashlib.md5(content_bytes).hexdigest()

now = datetime.now()
date_string = now.strftime("%Y-%m-%d")

md5_filename = file_name + f'{date_string}-md5.txt'
content_filename = file_name + f'{date_string}-whats-new.txt'

with open(md5_filename, 'w') as f:                            #saves current MD5 hash into a separate file with date
    f.write(md5_hash)
    
with open(old_md5_filename, 'w') as f:                        #saves current MD5 hash into a latest md5 file
    f.write(md5_hash)

with open(content_filename, 'w') as f:                        #saves the content to a separate file with date
    f.write(content_to_save)

if md5_hash == old_md5:                                       #compares new MD5 and old MD5 to check for content change
    print("Article Didn't Change")

else:                                                         # Provide the filenames of the old and new files
    get_new_ps(old_content, content_to_save, header)
    print("Article Changed")
