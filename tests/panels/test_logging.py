from __future__ import absolute_import, unicode_literals

import logging

from debug_toolbar.panels.logging import (
    collector, MESSAGE_IF_STRING_REPRESENTATION_INVALID)
from django.test.utils import override_settings

from ..base import BaseTestCase


@override_settings(DEBUG=True)
class LoggingPanelTestCase(BaseTestCase):

    def setUp(self):
        super(LoggingPanelTestCase, self).setUp()
        self.panel = self.toolbar.get_panel_by_id('LoggingPanel')
        self.logger = logging.getLogger(__name__)
        # DEBUG may be set to False initially, preventing the default tracking
        # from executing. Force an enable here to ensure that logging is activated.
        collector.enable_logging()
        collector.clear_collection()

    def test_happy_case(self):
        self.logger.info('Nothing to see here, move along!')

        self.panel.process_response(self.request, self.response)
        records = self.panel.get_stats()['records']

        self.assertEqual(1, len(records))
        self.assertEqual('Nothing to see here, move along!',
                         records[0]['message'])

    def test_formatting(self):
        self.logger.info('There are %d %s', 5, 'apples')

        self.panel.process_response(self.request, self.response)
        records = self.panel.get_stats()['records']

        self.assertEqual(1, len(records))
        self.assertEqual('There are 5 apples',
                         records[0]['message'])

    def test_failing_formatting(self):
        class BadClass(object):
            def __str__(self):
                raise Exception('Please not stringify me!')

        # should not raise exception, but fail silently
        self.logger.debug('This class is misbehaving: %s', BadClass())

        self.panel.process_response(self.request, self.response)
        records = self.panel.get_stats()['records']

        self.assertEqual(1, len(records))
        self.assertEqual(MESSAGE_IF_STRING_REPRESENTATION_INVALID,
                         records[0]['message'])
