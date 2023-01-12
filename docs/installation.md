## Installation
Before installing, ensure that Docker is installed and that the application files are copied to /var/www/signage on your server/workstation.

#### Configuration
Next, create a configuration at path `/instance/config.py`. Copy and paste the below variables into the file. Please note that you *must* change the lines noted in the comments for the software to run.

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

#### Running via Docker
Once you've confugured the application, run the bash script `start.sh` to configure the docker container and begin the docker process. If all is well, you should be able to visit the site at `localhost:56733`. If the app fails to start, check the DockerFile and ensure that all of your paths match with the directories you copied over.

Once you can connect to the site, you can log in with the default admin user.
