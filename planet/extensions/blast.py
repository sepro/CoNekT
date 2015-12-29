from threading import Thread
from queue import Queue
from time import sleep

import os
import sys
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
            print(" * Starting Blast thread...", file=sys.stderr)
            self.start()

    def add_job(self, blast_type, blast_input, blast_output):
        job = {'type': blast_type,
               'in': blast_input,
               'out': blast_output}
        print(" * Blast thread : Adding job..." + str(job), file=sys.stderr)
        self.queue.put(job)

    def __process_job(self, job):
        print(" * Blast thread : Processing: " + str(job), file=sys.stderr)
        if job['type'] == 'blastp':
            command = self.commands['blastp'].replace('<IN>', job['in']).replace('<OUT>', job['out'])
            # subprocess.call(shlex.split(command)) # good case
            subprocess.call(command, shell=True)
        else:
            print("Type not found")
            pass

    def run(self):
        """
        Function that runs when the thread is started, checks the queue and acts accordingly
        """
        print(" * Started Blast thread...", file=sys.stderr)
        while True:
            if self.queue.empty():
                sleep(0.1)
            else:
                job = self.queue.get()
                self.__process_job(job)
