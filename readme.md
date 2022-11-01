# CampusVision
![Issues](https://badgen.net/badge/Status/Work-in-Progress/red)
[![Azure Demo](https://github.com/JohnsonLM/CampusVision/actions/workflows/main_campusvisionapp.yml/badge.svg?branch=main)](https://github.com/JohnsonLM/CampusVision/actions/workflows/main_campusvisionapp.yml)
![Status](https://badgen.net/github/open-issues/JohnsonLM/CampusVision)
![Commits](https://badgen.net/github/commits/JohnsonLM/CampusVision/main)
![License](https://badgen.net/badge/license/GPL/blue)

CampusVison is a digital signage Management solution designed to run on minimal hardware to maximize deployment options to devices such as micro-computers, raspberry pis, smart TVs, and other display devices.

## Features
- Web interface for content management.
    - Add, schedule, edit, and remove slides.
    -  Contributor and administrator accounts.
    - Moderate slides
- Client interface for displaying slides
    - Display slides and graphic content.
    - Display video  looping content.
    - Display date and time and live weather.
    - Display emergency alerts
    - Display messages and "ticker" content
    - Customizable sidebar content and fullscreen modes.
- Runs on any web-based device with a network connection.

## Built with
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Flask](https://img.shields.io/badge/flask-%23000.svg?style=for-the-badge&logo=flask&logoColor=white)
![PyCharm](https://img.shields.io/badge/pycharm-143?style=for-the-badge&logo=pycharm&logoColor=black&color=black&labelColor=green)
![GitHub](https://img.shields.io/badge/github-%23121011.svg?style=for-the-badge&logo=github&logoColor=white)
![Affinity Designer](https://img.shields.io/badge/affinity%20designer-%231B72BE.svg?style=for-the-badge&logo=affinity-designer&logoColor=white)

## Installation

#### Configuration

First, update the configuration at path `/instance/config.py` based om your project needs. Please note that you *must* change the lines noted in the comments for the software to run.

```
'''config.py basic configuration'''

# add a secure 256-bit key here using a key generator such as allkeysgenerator.com
SECRET_KEY = 'SuperSecureK3yHere'

# points the app the the primary database
SQLALCHEMY_DATABASE_URI = 'sqlite:///db.sqlite'

# points the app to the uploads folder within the static directory.
UPLOAD_FOLDER = '/uploads'

# sets the maximum bit length of uploads. For static slides anything above 16MB is wildly excessive. 
MAX_CONTENT_LENGTH = 16 * 1000 * 1000

# Allows template updates to be loaded without restarting the app.
TEMPLATES_AUTO_RELOAD = True

# Should be set to false to prevent warnings.
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Insert an OpenWeatherMap API key here.
WEATHER_KEY = 'OpenWeatherMapAPIKeyHere'

# Sets what file types can be uploaded as slides
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# For pagination of the slide manager
POSTS_PER_PAGE = 10
```
#### Azure Install
First, setup the Azure web app in Azure.

**Create Repository Secret**
In your Github repo, create a reposiroty secret to share with the Azure installation. This will allow the app to conect ot your reposotroy and rebuild the project when changes are pushed to the branch. Once you have the secret, copy it to Azure in the Deployment Center.

**Setup custom Azure start command**
In your web app configuration, create a custom startup command as follows: 

`gunicorn --bind=0.0.0.0 --timeout 600 main:app`

#### Docker Install
Before installing, ensure that Docker is installed and that the application files are copied to /var/www/signage on your server/workstation.

Once you've configured the application, run the bash script `start.sh` to configure the docker container and begin the docker process. If all is well, you should be able to visit the site at `localhost:56733`. If the app fails to start, check the DockerFile and ensure that all of your paths match with the directories you copied over.

Once you can connect to the site, you can login with the default admin user:

username: first.last@domain.com
password: password

## URL Generatation
CampusVision uses url parameters to control the look and functionality of feeds. Below are the options available to append to urls. Declaring all parameters is recommended.

`?weather=False&interval=000&reload=000&fullscreen=False`
