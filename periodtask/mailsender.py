from email.message import EmailMessage
import ssl
import smtplib
import logging
from threading import Thread


logger = logging.getLogger('periodtask.mailsender')


class MailSender:
    def __init__(
        self, host, port, from_email, recipient_list,
        timeout=10, use_ssl=False, use_tls=False, username=None, password=None,
    ):
        self.host, self.port = host, port
        self.from_email, self.recipient_list = from_email, recipient_list
        self.timeout, self.use_ssl, self.use_tls = timeout, use_ssl, use_tls
        self.username, self.password = username, password

        self.connection_class = smtplib.SMTP_SSL if use_ssl else smtplib.SMTP
        if isinstance(recipient_list, str):
            self.recipient_list = [recipient_list]

    def _send(self, message):
        logger.debug('message sender starts')
        msg = '(%s) to %s' % (message['Subject'], message['To'])
        try:
            conn = self.connection_class(
                self.host, self.port, timeout=self.timeout
            )
            if self.use_tls:
                conn.starttls()
            logger.debug('starttls ok')
            if self.username and self.password:
                conn.login(self.username, self.password)
            logger.debug('login ok')

            try:
                refused = conn.send_message(message)
            except Exception:
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
        except Exception:
            logger.exception('Error sending e-mail: %s' % msg)

    def send_mail(
            self, subject, message, html_message=None
    ):
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = self.from_email
        msg['To'] = ', '.join(self.recipient_list)
        msg.set_content(message)
        if html_message:
            msg.add_alternative(html_message, subtype='html')
        Thread(target=self._send, args=(msg,)).start()
