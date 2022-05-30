#*Warning: This app is still under heavy development. Use at your own risk.*
# CampusVision
### A Lightweight Digital Signage Management Solution
CampusVison is a digital signage manager designed to run on minimal hardware to maximize deployment options to devices such as micro-computers, raspberry pis, smart TVs, and other display devices.

## Installation
Before installing, ensure that Docker is installed and that the application files are copied to /var/www/signage on your server/workstation.

#### Configuration
Next, create a configuration at path `/instance/config.py`. Copy and paste the below variables into the file. Please note that you *must* change the lines noted in the comments for the software to run.

`Code here`

#### Running via Docker
Once you've confugured the application, run the bash script `start.sh` to configure the docker container and begin the docker process. If all is well, you should be able to visit the site at `localhost:56733`. If the app fails to start, check the DockerFile and ensure that all of your paths match with the directories you copied over.

Once you can connect to the site, you can login with the default admin user.
