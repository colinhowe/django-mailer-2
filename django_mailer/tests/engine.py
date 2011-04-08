from django.core.mail import EmailMessage
from django.test import TestCase
from django_mailer import constants, engine, settings
from django_mailer.lockfile import FileLock
from django_mailer.tests.base import FakeConnection, MailerTestCase
from django_mailer.engine import send_queued_message, send_message
from django_mailer.models import Message, QueuedMessage
from socket import error as SocketError
from StringIO import StringIO
import logging
import time


class LockTest(TestCase):
    """
    Tests for Django Mailer trying to send mail when the lock is already in
    place.
    """

    def setUp(self):
        # Create somewhere to store the log debug output. 
        self.output = StringIO()
        # Create a log handler which can capture the log debug output.
        self.handler = logging.StreamHandler(self.output)
        self.handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(message)s')
        self.handler.setFormatter(formatter)
        # Add the log handler.
        logger = logging.getLogger('django_mailer')
        logger.addHandler(self.handler)
        
        # Set the LOCK_WAIT_TIMEOUT to the default value.
        self.original_timeout = settings.LOCK_WAIT_TIMEOUT
        settings.LOCK_WAIT_TIMEOUT = 0

        # Use a test lock-file name in case something goes wrong, then emulate
        # that the lock file has already been acquired by another process.
        self.original_lock_path = engine.LOCK_PATH
        engine.LOCK_PATH += '.mailer-test'
        self.lock = FileLock(engine.LOCK_PATH)
        self.lock.unique_name += '.mailer_test'
        self.lock.acquire(0)

    def tearDown(self):
        # Remove the log handler.
        logger = logging.getLogger('django_mailer')
        logger.removeHandler(self.handler)

        # Revert the LOCK_WAIT_TIMEOUT to it's original value.
        settings.LOCK_WAIT_TIMEOUT = self.original_timeout

        # Revert the lock file unique name
        engine.LOCK_PATH = self.original_lock_path
        self.lock.release()

    def test_locked(self):
        # Acquire the lock so that send_all will fail.
        engine.send_all()
        self.output.seek(0)
        self.assertEqual(self.output.readlines()[-1].strip(),
                         'Lock already in place. Exiting.')
        # Try with a timeout.
        settings.LOCK_WAIT_TIMEOUT = .1
        engine.send_all()
        self.output.seek(0)
        self.assertEqual(self.output.readlines()[-1].strip(),
                         'Waiting for the lock timed out. Exiting.')

    def test_locked_timeoutbug(self):
        # We want to emulate the lock acquiring taking no time, so the next
        # three calls to time.time() always return 0 (then set it back to the
        # real function).
        original_time = time.time
        global time_call_count
        time_call_count = 0
        def fake_time():
            global time_call_count
            time_call_count = time_call_count + 1
            if time_call_count >= 3:
                time.time = original_time
            return 0
        time.time = fake_time
        try:
            engine.send_all()
            self.output.seek(0)
            self.assertEqual(self.output.readlines()[-1].strip(),
                             'Lock already in place. Exiting.')
        finally:
            time.time = original_time


class TestErrorHandling(MailerTestCase):
    def test_queued_message_socket_error(self):
        '''If a socket error is raised then the standard handling
        is that the message should be deferred'''
        def raise_socket_error(*args, **kwargs):
            raise SocketError()
        FakeConnection.set_overrides([ raise_socket_error ])

        message = Message.objects.create(
            from_address='from@test.test',
            to_address='to@test.test',
            subject='Test',
            encoded_message='Test message'
        )
        queued_message = QueuedMessage.objects.create(message=message)

        send_queued_message(queued_message, self.connection)

        queued_message = QueuedMessage.objects.get(id=queued_message.id)
        self.assertTrue(queued_message.deferred != None)

    def test_queued_message_custom_handler(self):
        '''A custom error should be able to pick up any random exception'''
        def raise_exception(*args, **kwargs):
            raise_exception.result = Exception('Random exception')
            raise raise_exception.result
        FakeConnection.set_overrides([ raise_exception ])

        def error_handler(exception):
            self.assertEquals(raise_exception.result, exception)
            error_handler.called = True
            return constants.RESULT_FAILED

        settings.CUSTOM_ERROR_HANDLER = error_handler

        message = Message.objects.create(
            from_address='from@test.test',
            to_address='to@test.test',
            subject='Test',
            encoded_message='Test message'
        )
        queued_message = QueuedMessage.objects.create(message=message)

        send_queued_message(queued_message, self.connection)
    
        self.assertTrue(error_handler.called)

    def test_send_message_socket_error(self):
        '''If a socket error is raised then the standard handling
        is to return the error'''
        def raise_socket_error(*args, **kwargs):
            raise SocketError()
        FakeConnection.set_overrides([ raise_socket_error ])

        message = EmailMessage(
            'Subject',
            'Message',
            'from@test.test',
            ['to@test.test'])

        result = send_message(message, self.connection)

        self.assertEquals(constants.RESULT_FAILED, result)

    def test_send_message_custom_handler(self):
        '''A custom error should be able to pick up any random exception'''
        def raise_exception(*args, **kwargs):
            raise_exception.result = Exception('Random exception')
            raise raise_exception.result
        FakeConnection.set_overrides([ raise_exception ])

        def error_handler(exception):
            self.assertEquals(raise_exception.result, exception)
            error_handler.called = True
            return constants.RESULT_FAILED

        settings.CUSTOM_ERROR_HANDLER = error_handler

        message = EmailMessage(
            'Subject',
            'Message',
            'from@test.test',
            ['to@test.test'])

        result = send_message(message, self.connection)

        self.assertEquals(constants.RESULT_FAILED, result)
