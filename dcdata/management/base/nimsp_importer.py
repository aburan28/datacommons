import os, fnmatch, logging, logging.handlers, time, datetime

from settings import LOGGING_EMAIL
from django.core.management.base import BaseCommand, CommandError
from optparse import make_option


class BaseNimspImporter(BaseCommand):

    IN_DIR       = None # '/home/datacommons/data/auto/nimsp/raw/IN'
    DONE_DIR     = None # '/home/datacommons/data/auto/nimsp/raw/DONE'
    REJECTED_DIR = None # '/home/datacommons/data/auto/nimsp/raw/REJECTED'
    OUT_DIR      = None # '/home/datacommons/data/auto/nimsp/IN'
    FILE_PATTERN = None # bash-style, ala '*.sql'

    LOG_PATH = None # '/home/datacommons/data/auto/log/nimsp_my_command.log'

    PID_DIR = '/home/datacommons/data/auto/tmp'

    option_list = BaseCommand.option_list + (
        make_option('--dry-run', '-d',
            action='store_true',
            dest='dry_run',
            default=False,
            help='Do a test run of the command, only printing what would be done.'
        ),
    )


    def __init__(self):
        super(BaseNimspImporter, self).__init__()
        self.class_name = self.__class__.__name__
        self.set_up_logger()
        self.pid_file_path = os.path.join(self.PID_DIR, self.__module__)


    def set_up_logger(self):
        # create logger
        self.log = logging.getLogger(self.class_name)
        self.log.setLevel(logging.DEBUG)
        # create console handler and set level to debug
        ch = logging.FileHandler(self.LOG_PATH)
        ch.setLevel(logging.DEBUG)

        # create email handler and set level to warn
        eh = logging.handlers.SMTPHandler(
            (LOGGING_EMAIL['host'], LOGGING_EMAIL['port']), # host
            LOGGING_EMAIL['username'], # from address
            ['arowland@sunlightfoundation.com'], # to addresses
            'Unhappy NIMSP Loading App', # subject
            (LOGGING_EMAIL['username'], LOGGING_EMAIL['password']) # credentials tuple
        )
        eh.setLevel(logging.WARN)

        # create formatter
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        ch.setFormatter(formatter)
        eh.setFormatter(formatter)
        self.log.addHandler(ch)
        self.log.addHandler(eh)


    def handle(self, *args, **options):
        """
            Will run the do_for_file operation from a subclass on every
            eligible file found in the IN_DIR, or will log what it would
            do if the dry_run option is specified.
        """

        self.die_if_already_running()
        self.set_pid_file()

        self.log.info('Starting {0}'.format(self.class_name))

        self.dry_run = options['dry_run']

        try:
            for (file, file_path) in self.find_eligible_files():
                if not self.dry_run:
                    self.do_for_file(file, file_path)
                else:
                    self.dry_run_for_file(file, file_path)
        except Exception, e:
            self.log.error('Fatal error: {0}'.format(e.msg))

        self.log.info('Finished.')


    # define this in the derived classes
    def do_for_file(self, file, file_path):
        """
            The meat of the operation happens here.

            Takes the input file basename and its location/path as arguments.
        """
        pass


    # define this in the derived classes
    def dry_run_for_file(self, file, file_path):
        pass


    def find_eligible_files(self):
        """
            Goes through the IN_DIR and finds files matching the FILE_PATTERN to act on
        """
        files = os.listdir(self.IN_DIR)

        if len(files) > 0:
            for file in os.listdir(self.IN_DIR):
                file_path = os.path.join(self.IN_DIR, file)
                self.log.info('Found file {0}'.format(file))
                if fnmatch.fnmatch(file, self.FILE_PATTERN):
                    # make sure the file has downloaded completely (hasn't been modified in the last minute)
                    now_epoch = time.time()
                    last_modified_epoch = os.path.getmtime(file_path)
                    if now_epoch - last_modified_epoch > 60:
                        yield file, file_path
                    else:
                        self.log.info('File last modified time is too recent. Skipping.')
                else:
                    self.log.warning('{0} doesn\'t match the file pattern. Rejecting.'.format(file))
                    self.reject_file(file)
        else:
            self.log.info('No files found.')


    def reject_file(self, name):
        if not self.dry_run:
            os.rename(os.path.join(self.IN_DIR, name), os.path.join(self.REJECTED_DIR, name))


    def archive_file(self, name, timestamp=False):
        if not self.dry_run:
            new_name = name

            if timestamp:
                new_name = '_'.join([datetime.datetime.now().strftime('%Y%m%d_%H%M'), name])

            os.rename(os.path.join(self.IN_DIR, name), os.path.join(self.DONE_DIR, new_name))


    def die_if_already_running(self):
        """
            Make sure this script is not already running in another process.
        """
        if os.path.exists(self.pid_file_path):
            raise CommandError("This script is already running in a separate process. (Check {0})".format(self.pid_file_path))


    def set_pid_file(self):
        fh = open(self.pid_file_path, 'w')
        fh.write(str(os.getpid()))
        fh.close()


    def destroy_pid_file(self):
        os.remove(self.pid_file_path)

