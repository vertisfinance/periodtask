from threading import Thread
from email.message import EmailMessage
import os
import ssl
import smtplib
import logging


logger = logging.getLogger('mailsender')


def send_mail(subject, message, from_email, recipient_list):
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = ', '.join(recipient_list)
    msg.set_content(message)
    MailSender(msg).start()


class MailSender(Thread):
    def __init__(self, message):
        self.smtp_username = os.environ.get('SMTP_USERNAME', None)
        self.smtp_password = os.environ.get('SMTP_PASSWORD', None)

        self.host = 'smtp.gmail.com'
        self.port = 587
        self.timeout = 10
        self.use_ssl = False
        self.use_tls = True

        self.message = message

        # self.REPLACE_RECIPIENT_FOR_TESTING = os.environ.get(
        #     'REPLACE_RECIPIENT_FOR_TESTING', None)

        super(MailSender, self).__init__()

    @property
    def connection_class(self):
        return smtplib.SMTP_SSL if self.use_ssl else smtplib.SMTP

    def run(self):
        msg = '(%s) to %s' % (self.message['Subject'], self.message['To'])
        try:
            conn = self.connection_class(
                self.host, self.port,
                timeout=self.timeout
            )
            if self.use_tls:
                conn.starttls()
            logger.debug('starttls ok')
            if self.smtp_username and self.smtp_password:
                conn.login(self.smtp_username, self.smtp_password)
            logger.debug('login ok')

            try:
                refused = conn.send_message(self.message)
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
