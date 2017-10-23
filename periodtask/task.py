import time
import logging

from . import mailsender


logger = logging.getLogger('periodtask.task')


class Task:
    def __init__(self):
        pass

    def start(self):
        logger.info('task started')
        mailsender.send_mail(
            'árvíztűrő tükörfúrógép',
            'hello',
            'richardbann@gmail.com',
            ['richard.bann@vertis.com']
        )
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        logger.info('task stopped')
