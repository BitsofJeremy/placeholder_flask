from flask import Flask, request, \
    render_template, redirect, url_for
import logging
from logging.config import dictConfig
import os
import requests

# define logging dict
dictConfig({
    'version': 1,
    'formatters': {
        'default': {
            'format': '{"date": "%(asctime)s", '
                      '"log_level": "%(levelname)s", '
                      '"module": "%(module)s", '
                      '"message": "%(message)s"}'
         }
    },
    'handlers': {
        'wsgi': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://flask.logging.wsgi_errors_stream',
            'formatter': 'default'
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'default',
            'filename': 'app.log',
            'maxBytes': 1024000,
            'backupCount': 3
        }
    },
    'root': {
        'level': 'INFO',
        'handlers': [
            'wsgi',
            'file'
        ]
    }
})


app = Flask(__name__)
logger = logging.getLogger(__name__)

# Version
APP_VERSION = '0.0.1'

app.config['DEBUG'] = False

# Name of the app
app.config['APP_NAME'] = 'app'
app.config['HOST'] = '127.0.0.1'
app.config['PORT'] = '5050'

# Threads
app.config['THREADS_PER_PAGE'] = 2

# Enable protection agains *Cross-site Request Forgery (CSRF)*
app.config['CSRF_ENABLED'] = True

# Use a secure, unique and absolutely secret key for
# signing the data.
# Secret key for signing cookies
app.config['CSRF_SESSION_KEY'] = os.getenv('CSRF_SESSION_KEY')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

# Mailgun config
DOMAIN_NAME = os.getenv('DOMAIN_NAME')
ADMIN_EMAIL = os.getenv('ADMIN_EMAIL')
MAILGUN_API_KEY = os.getenv('MAILGUN_API_KEY')


def send_simple_message(name, email):
    """
    Taken from Mailgun docs to send from /contact form
    """
    url = f"https://api.mailgun.net/v3/{DOMAIN_NAME}/messages"
    data = {
        "from": f"{email}",
        "to": [f"{ADMIN_EMAIL}"],
        "subject": f"[placeholder.2024] Website Request",
        "text": f"Message:  \n\nName:  {name} \n\nEmail:  {email}"}
    logger.debug(url)
    logger.debug(data)
    res = requests.post(
        url,
        auth=("api", MAILGUN_API_KEY),
        data=data
    )
    logger.info(res.text)
    return True


@app.route('/')
def index():
    """
    Renders the index page
    """
    logger.debug(app.config)
    video_url = url_for(
        'static',
        filename='videos/background_video.mp4'
    )
    return render_template(
        'index.html',
        version=APP_VERSION,
        video_url=video_url,
    )


@app.route('/contact', methods=['POST'])
def contact():
    """
    Sends info from /contact POST form to
    admin email via Mailgun.
    """
    # get post args
    data = request.form
    name = data['name']
    email = data['email']

    logger.info(f"Someone Entered: {name}, \
          {email}")
    _res = send_simple_message(name, email)
    if _res:
        logger.info("Message Sent!")
    else:
        logger.info("Something went wrong with message.")
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run()
