# Digital Signage System
This is a digital signage manager designed to replace Concerto.

## Installation
Before installing, ensure that Docker is installed and that the application files are copied to /var/www/signage on your server/workstation.

Next, run the bash script start.sh to configure the docker container and begin the docker process. If all is well, you should be able to visit the site at localhost:56733

If you run into configuration issues, start with the DockerFile and ensure that all of your paths match with the directories you copied over.

Once you can connect to the site, you can login with the default admin user.

### Roadmap
- Finalize feed layout.
- Finish slide editing process.
- Add Pagination to slide manager and moderator.
- Expose openweathermap api key.
- Allow admins to create feeds.
