from threading import Thread
from email.message import EmailMessage
import os
import ssl
import smtplib
import logging


logger = logging.getLogger('mailsender')


SMTP_HOST = os.environ.get('SMTP_HOST')
SMTP_PORT = os.environ.get('SMTP_PORT')
SMTP_TIMEOUT = int(os.environ.get('SMTP_TIMEOUT', 10))
SMTP_USE_SSL = os.environ.get('SMTP_USE_SSL', '') in ('True', 'true')
SMTP_USE_TLS = os.environ.get('SMTP_USE_TLS', '') in ('True', 'true')
SMTP_USERNAME = os.environ.get('SMTP_USERNAME', None)
SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD', None)

CONNECTION_CLASS = smtplib.SMTP_SSL if SMTP_USE_SSL else smtplib.SMTP


def _send(message):
    logger.debug('message sender thread starts')
    msg = '(%s) to %s' % (message['Subject'], message['To'])
    try:
        conn = CONNECTION_CLASS(SMTP_HOST, SMTP_PORT, timeout=SMTP_TIMEOUT)
        if SMTP_USE_TLS:
            conn.starttls()
        logger.debug('starttls ok')
        if SMTP_USERNAME and SMTP_PASSWORD:
            conn.login(SMTP_USERNAME, SMTP_PASSWORD)
        logger.debug('login ok')

        try:
            refused = conn.send_message(message)
        except: # NOQA
            logger.exception('sending error')
        else:
            if refused:
                logger.warning('refused: %s' % msg)
            else:
                logger.info('e-mail sent: %s' % msg)

        try:
            conn.quit()
        except (ssl.SSLError, smtplib.SMTPServerDisconnected):
            # This happens when calling quit() on a TLS connection
            # sometimes, or when the connection was already disconnected
            # by the server.
            conn.close()
        except smtplib.SMTPException:
            logger.exception('error during quit')
    except:  # NOQA
        logger.exception('Error sending e-mail: %s' % msg)


def send_mail(subject, message, from_email, recipient_list, html_message=None):
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = ', '.join(recipient_list)
    msg.set_content(message)
    if html_message:
        msg.add_alternative(html_message, subtype='html')
    Thread(target=_send, args=(msg,)).start()
