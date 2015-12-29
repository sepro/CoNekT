from threading import Thread
from queue import Queue
from time import sleep

import os
import subprocess
import shlex


class BlastThread(Thread):
    def __init__(self, app=None):
        """
        Sets up thread, empty queue and register with app
        :param app: flask-app to register with
        """
        Thread.__init__(self)
        self.daemon = True
        self.queue = Queue()
        self.running = False

        self.commands = {'blastp': '', 'blastn': ''}
        self.temp_dir = ''

        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """
        Register blast thread with app
        :param app: Flask application
        :type app: Flask
        """

        # register extension with app
        app.extensions = getattr(app, 'extensions', {})
        app.extensions['flask-blast'] = self

        # Check this to make sure the Werkzeug reloader doesn't spawn an extra thread !
        if os.environ.get('WERKZEUG_RUN_MAIN') == 'true' or not app.config['DEBUG']:
            self.commands['blastp'] = app.config['BLASTP_CMD']
            self.commands['blastn'] = app.config['BLASTN_CMD']
            self.temp_dir = app.config['BLAST_TMP_DIR']

            print(self.temp_dir)

            print("Starting Blast thread...")
            self.start()

    def process_job(self, job):
        if job['type'] == 'blastp':
            command = self.commands['blastp'].replace('<IN>', job['in']).replace('<OUT>', job['out'])
            subprocess.call(shlex.split(command))

    def run(self):
        """
        Function that runs when the thread is started, checks the queue and acts accordingly
        """
        while True:
            if self.queue.empty():
                sleep(0.1)
            else:
                job = self.queue.get()
                self.process_job(job)
