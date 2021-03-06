# -*- coding: utf-8 -*-
"""
Presence analyzer unit tests.
"""
from __future__ import unicode_literals

import json
import os.path
import unittest
from datetime import date, time, timedelta

import main  # pylint: disable=relative-import
import utils  # pylint: disable=relative-import
import views  # pylint: disable=relative-import, unused-import


TEST_DATA_CSV = os.path.join(
    os.path.dirname(__file__), '..', '..', 'runtime', 'data', 'test_data.csv'
)
TEST_DATA_XML = os.path.join(
    os.path.dirname(__file__), '..', '..', 'runtime', 'data', 'test_users.xml'
)


# pylint: disable=maybe-no-member, too-many-public-methods
class PresenceAnalyzerViewsTestCase(unittest.TestCase):
    """
    Views tests.
    """

    def setUp(self):
        """
        Before each test, set up a environment.
        """
        main.app.config.update({'DATA_CSV': TEST_DATA_CSV})
        main.app.config.update({'DATA_XML': TEST_DATA_XML})
        self.client = main.app.test_client()

    def tearDown(self):
        """
        Get rid of unused objects after each test.
        """
        pass

    def test_mainpage(self):
        """
        Test main page redirect.
        """
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 302)

    def test_users_api(self):
        """
        Test users listing.
        """
        resp = self.client.get('/api/v1/users')
        data = json.loads(resp.data)

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        self.assertEqual(len(data), 4)
        self.assertDictEqual(data[0], {'name': 'User 176', u'user_id': 176})

    def test_avatar_api(self):
        """
        Test users avatar listing.
        """
        resp = self.client.get('/api/v1/users_xml')
        data = json.loads(resp.data)

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        self.assertDictEqual(
            data[0], {
                'user_id': '141',
                'name': 'Adam P.',
                'avatar': 'https://intranet.stxnext.pl/api/images/users/141'
            }
        )

    def test_overtime_api(self):
        """
        Testing top users overtime.
        """
        resp = self.client.get('/api/v1/overtime/')
        data = json.loads(resp.data)

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, 'application/json')
        self.assertEqual(
            data, [[
                176, {
                    'overtime': 39586,
                    'name': 'Adrian K.'
                }
            ]]
        )

    def test_get_avatar(self):
        """
        Test avatar link by user id.
        """
        bad_resp = self.client.get('/api/v1/get_avatar/10')
        self.assertEqual(bad_resp.status_code, 404)

        resp = self.client.get('/api/v1/get_avatar/141')
        data = json.loads(resp.data)

        self.assertEqual(resp.status_code, 200)
        self.assertDictEqual(
            data, {
                'user_id': 141,
                'avatar': 'https://intranet.stxnext.pl/api/images/users/141'
            }
        )

    def test_mean_time_weekday_view(self):
        """
        Test mean presence time of given user grouped by weekday.
        """
        resp = self.client.get('/api/v1/mean_time_weekday/11')
        data = dict(json.loads(resp.data))

        self.assertEqual(resp.status_code, 200)
        self.assertDictEqual(
            data, {
                'Mon': 24123.0,
                'Tue': 16564.0,
                'Wed': 25321.0,
                'Thu': 22984.0,
                'Fri': 6426.0,
                'Sat': 0,
                'Sun': 0,
            }
        )

    def test_presence_weekday_view(self):
        """
        Test by user id, for existing user and non existing user.
        """
        resp = self.client.get('/api/v1/presence_weekday/11')
        data = dict(json.loads(resp.data))

        self.assertEqual(resp.status_code, 200)
        self.assertDictEqual(
            data, {
                'Weekday': 'Presence (s)',
                'Mon': 24123,
                'Tue': 16564,
                'Wed': 25321,
                'Thu': 45968,
                'Fri': 6426,
                'Sat': 0,
                'Sun': 0
            }
        )

    def test_presence_start_end(self):
        """
        Test calculating average time when user start and end work.
        """
        resp = self.client.get('/api/v1/presence_start_end/11')
        data = dict(json.loads(resp.data))

        self.assertEqual(resp.status_code, 200)
        self.assertDictEqual(
            data, {
                'Thu': {
                    'start': '9:53:22',
                    'end': '16:16:26',
                },
                'Fri': {
                    'start': '13:16:56',
                    'end': '15:04:02',
                },
                'Wed': {
                    'start': '9:13:26',
                    'end': '16:15:27'},
                'Mon': {
                    'start': '9:12:14',
                    'end': '15:54:17',
                },
                'Tue': {
                    'start': '9:19:50',
                    'end': '13:55:54',
                },
                'Sat': {
                    'end': '0:00:00',
                    'start': '0:00:00'
                },
                'Sun': {
                    'end': '0:00:00',
                    'start': '0:00:00'
                },
            }
        )

    def test_dynamic_route(self):
        """
        Testing creating dynamic routes and templates.
        """
        resp = self.client.get('/mean_time_weekday.html')
        self.assertEqual(resp.status_code, 200)

        bad_resp = self.client.get('/something.html')
        self.assertEqual(bad_resp.status_code, 404)


class PresenceAnalyzerUtilsTestCase(unittest.TestCase):
    """
    Utility functions tests.
    """

    def setUp(self):
        """
        Before each test, set up a environment.
        """
        main.app.config.update({'DATA_CSV': TEST_DATA_CSV})
        main.app.config.update({'DATA_XML': TEST_DATA_XML})

    def tearDown(self):
        """
        Get rid of unused objects after each test.
        """
        pass

    def test_cache_decorator(self):
        """
        Test if function has wrapper.
        """
        self.assertTrue(getattr(utils.get_data, '__wrapped__'))
        self.assertEqual(utils.CACHE, {})

        utils.get_data()
        self.assertIn(date(2013, 9, 10), utils.CACHE['get_data']['result'][10])

    def test_get_data(self):
        """
        Test parsing of CSV file.
        """
        data = utils.get_data()
        sample_date = date(2013, 9, 10)

        self.assertIsInstance(data, dict)
        self.assertItemsEqual(data.keys(), [10, 11, 141, 176])
        self.assertIn(sample_date, data[10])
        self.assertItemsEqual(data[10][sample_date].keys(), ['start', 'end'])
        self.assertEqual(data[10][sample_date]['start'], time(9, 39, 5))

    def test_get_user(self):
        """
        Test parsing of XML file.
        """
        data = utils.get_user()
        sample_data = {
            'name': 'Anna D.',
            'avatar': 'https://intranet.stxnext.pl/api/images/users/165'
        }

        self.assertIsInstance(data, dict)
        self.assertItemsEqual(data.keys(), ['176', '26', '170', '165', '141'])
        self.assertEqual(sample_data, data['165'])
        self.assertItemsEqual(data['165'].keys(), ['name', 'avatar'])

    def test_group_by_weekday(self):
        """
        Test groups entries by weekdays.
        """
        self.assertEqual(
            utils.group_by_weekday(utils.get_data()[10]),
            [[], [30047], [24465], [23705], [], [], []],
        )
        self.assertEqual(
            utils.group_by_weekday(utils.get_data()[11]),
            [[24123], [16564], [25321], [22969, 22999], [6426], [], []],
        )

    def test_seconds_since_midnight(self):
        """
        Test amount of seconds since midnight.
        """
        self.assertEqual(
            utils.seconds_since_midnight(time(2, 12, 6)),
            timedelta(hours=2, minutes=12, seconds=6).seconds
        )
        self.assertEqual(
            utils.seconds_since_midnight(time(12, 0, 35)),
            timedelta(hours=12, minutes=0, seconds=35).seconds
        )
        self.assertEqual(
            utils.seconds_since_midnight(time(1, 1, 59)),
            timedelta(hours=1, minutes=1, seconds=59).seconds
        )

    def test_interval(self):
        """
        Test calculating interval between two time objects.
        """
        self.assertEqual(
            25300,
            abs(utils.interval(time(18, 3, 16), time(11, 1, 36)))
        )
        self.assertEqual(
            61300,
            abs(utils.interval(time(18, 3, 16), time(1, 1, 36)))
        )
        self.assertEqual(
            3696,
            abs(utils.interval(time(0, 0, 0), time(1, 1, 36)))
        )

    def test_mean(self):
        """
        Test arithmetic mean.
        """
        self.assertEqual(utils.mean([1, 2, 3, 4, 5, 6]), 3.5)
        self.assertEqual(utils.mean([]), 0)
        self.assertEqual(utils.mean([1, 4, 7]), 4)
        self.assertEqual(utils.mean([1, 99]), 50)

    def test_average_second(self):
        """
        Test calculating average time in seconds.
        """
        self.assertEqual(
            utils.average_seconds(
                {'user': [1, 2, 3, 4, 5]}, 'user'),
            '0:00:03'
        )
        self.assertEqual(
            utils.average_seconds(
                {'user': [1471, 277, 389, 4796, 5678]}, 'user'),
            '0:42:02'
        )
        self.assertEqual(
            utils.average_seconds(
                {'user': []}, 'user'),
            '0:00:00'
        )

    def test_star_end_time(self):
        """
        Test average time when user start the work and when user end the work.
        """
        data = utils.get_data()

        self.assertEqual(
            utils.star_end_time(data, 10), {
                'Wed': {
                    'start': '9:19:52',
                    'end': '16:07:37'
                },
                'Sun': {
                    'start': '0:00:00',
                    'end': '0:00:00'
                },
                'Fri': {
                    'start': '0:00:00',
                    'end': '0:00:00'
                },
                'Tue': {
                    'start': '9:39:05',
                    'end': '17:59:52'
                },
                'Mon': {
                    'start': '0:00:00',
                    'end': '0:00:00'
                },
                'Thu': {
                    'start': '10:48:46',
                    'end': '17:23:51'
                },
                'Sat': {
                    'start': '0:00:00',
                    'end': '0:00:00'
                },
            }
        )
        self.assertEqual(
            utils.star_end_time(data, 11), {
                'Wed': {
                    'start': '9:13:26',
                    'end': '16:15:27'
                },
                'Sun': {
                    'start': '0:00:00',
                    'end': '0:00:00'
                },
                'Fri': {
                    'start': '13:16:56',
                    'end': '15:04:02'
                },
                'Tue': {
                    'start': '9:19:50',
                    'end': '13:55:54'
                },
                'Mon': {
                    'start': '9:12:14',
                    'end': '15:54:17'
                },
                'Thu': {
                    'start': '9:53:22',
                    'end': '16:16:26'
                },
                'Sat': {
                    'start': '0:00:00',
                    'end': '0:00:00'
                },
            }
        )

    def test_get_overtime(self):
        """
        Test get top users overtime.
        """
        data = utils.get_data()

        self.assertEqual(
            utils.get_overtime(data), [(
                176, {
                    'overtime': 39586,
                    'name': 'Adrian K.'
                }
            )]
        )

    def test_bussines_day(self):
        """
        Test for worked seconds in month.
        """
        self.assertEqual(utils.bussines_days((2012, 3)), 633600)
        self.assertEqual(utils.bussines_days((2010, 2)), 576000)


def suite():
    """
    Default test suite.
    """
    base_suite = unittest.TestSuite()
    base_suite.addTest(unittest.makeSuite(PresenceAnalyzerViewsTestCase))
    base_suite.addTest(unittest.makeSuite(PresenceAnalyzerUtilsTestCase))
    return base_suite


if __name__ == '__main__':
    unittest.main()
