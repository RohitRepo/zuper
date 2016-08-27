import requests
import logging

logger = logging.getLogger(__name__)

api_key = "key-de111767d356538b10357135ac640f7c"
api_sandbox = "zuperfast.com"


def send_email(to_email, from_email, subject, body):
    request_url = 'https://api.mailgun.net/v2/{0}/messages'.format(api_sandbox)
    request = requests.post(request_url, auth=('api', api_key), data={
        'from': from_email,
        'to': to_email,
        'subject': subject,
        'text': body
    })

    logger.info("Sending email to %s - %s", to_email, subject)

    if request.status_code == 200:
        logger.info("Email sent successful")
        return True
    else:
        logger.error("Sending email failed")
        return False
