# CampusVision
### A Lightweight Digital Signage Management Solution
![Issues](https://badgen.net/badge/Status/Work-in-Progress/red)
![License](https://badgen.net/badge/license/MIT/blue)
![Status](https://badgen.net/github/issues/JohnsonLM/CampusVision)

CampusVison is a digital signage manager designed to run on minimal hardware to maximize deployment options to devices such as micro-computers, raspberry pis, smart TVs, and other display devices.

## Features
- Web interface for content management.
    - Add, schedule, edit, and remove slides.
    -  Contributor and administrator accounts.
    - Moderate slides
- Client interface for displaying slides
    - Display date and time and live weather.
    - Display emergency alerts
    - Display messages and "ticker" content
    - Customizable sidebar content
- Runs on any web-based device with a network connection.

## Built with
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Flask](https://img.shields.io/badge/flask-%23000.svg?style=for-the-badge&logo=flask&logoColor=white)
![PyCharm](https://img.shields.io/badge/pycharm-143?style=for-the-badge&logo=pycharm&logoColor=black&color=black&labelColor=green)
![GitHub](https://img.shields.io/badge/github-%23121011.svg?style=for-the-badge&logo=github&logoColor=white)
![Affinity Designer](https://img.shields.io/badge/affinity%20desginer-%231B72BE.svg?style=for-the-badge&logo=affinity-designer&logoColor=white)

## Installation
Before installing, ensure that Docker is installed and that the application files are copied to /var/www/signage on your server/workstation.

#### Configuration
Next, create a configuration at path `/instance/config.py`. Copy and paste the below variables into the file. Please note that you *must* change the lines noted in the comments for the software to run.

`Code here`

#### Running via Docker
Once you've confugured the application, run the bash script `start.sh` to configure the docker container and begin the docker process. If all is well, you should be able to visit the site at `localhost:56733`. If the app fails to start, check the DockerFile and ensure that all of your paths match with the directories you copied over.

Once you can connect to the site, you can login with the default admin user.

### Support or Contact

Having trouble with CampusVision?Contact @johnsonLM and I'll help you sort it out.
