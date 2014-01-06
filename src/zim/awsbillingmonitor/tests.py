##############################################################################
#
# Copyright (c) Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

from zope.testing import setupstack

import datetime
import doctest
import mock
import unittest

def assert_(cond, mess="Assertion Failed"):
    if not cond:
        raise AssertionError(mess)

class Metric:

    start = datetime.datetime(2013, 12, 12, 14, 1, 12, 362069)
    end =   datetime.datetime(2013, 12, 13, 14, 1, 12, 362069)

    def __init__(self, dimensions):
        self.dimensions = dimensions

    def query(self, start, end, stat, unit, period):
        assert_(start == self.start)
        assert_(end == self.end)
        assert_(stat == "Maximum")
        assert_(unit is None)
        assert_(period == 300)

        return self.dimensions['data']

class Connection:

    def __init__(self, region):
        assert_(region == 'test-region')

    metrics = tuple(
        Metric(d) for d in (
            {u'ServiceName': [u'AmazonEC2']},
            {u'ServiceName': [u'AmazonRoute53']},
            {u'ServiceName': [u'AmazonSimpleDB']},
            {u'ServiceName': [u'AWSQueueService']},
            {u'ServiceName': [u'AmazonCloudFront'],
             'data': [{u'Maximum': 377.54000000000002,
                       u'Timestamp': datetime.datetime(2013, 12, 12, 14, 36),
                       u'Unit': u'None'},
                      {u'Maximum': 400.19999999999999,
                       u'Timestamp': datetime.datetime(2013, 12, 13, 6, 36),
                       u'Unit': u'None'},
                      {u'Maximum': 382.94999999999999,
                       u'Timestamp': datetime.datetime(2013, 12, 12, 18, 36),
                       u'Unit': u'None'},
                      {u'Maximum': 392.77999999999997,
                       u'Timestamp': datetime.datetime(2013, 12, 13, 2, 36),
                       u'Unit': u'None'},
                      {u'Maximum': 382.94999999999999,
                       u'Timestamp': datetime.datetime(2013, 12, 12, 22, 36),
                       u'Unit': u'None'}]
             },
            {u'ServiceName': [u'AWSDataTransfer']},
            {u'ServiceName': [u'AmazonSNS']},
            {u'ServiceName': [u'AmazonS3']},
            {u'ServiceName': [u'AmazonSES']},
            {'data': [{u'Maximum': 3275.1300000000001,
                       u'Timestamp': datetime.datetime(2013, 12, 12, 14, 36),
                       u'Unit': u'None'},
                      {u'Maximum': 3497.9499999999998,
                       u'Timestamp': datetime.datetime(2013, 12, 13, 6, 36),
                       u'Unit': u'None'},
                      {u'Maximum': 3337.8699999999999,
                       u'Timestamp': datetime.datetime(2013, 12, 12, 18, 36),
                       u'Unit': u'None'},
                      {u'Maximum': 3427.1399999999999,
                       u'Timestamp': datetime.datetime(2013, 12, 13, 2, 36),
                       u'Unit': u'None'},
                      {u'Maximum': 3337.8699999999999,
                       u'Timestamp': datetime.datetime(2013, 12, 12, 22, 36),
                       u'Unit': u'None'}]
             },
            )
        )

    def list_metrics(self, metric_name, namespace):
        assert_(metric_name=="EstimatedCharges")
        assert_(namespace=="AWS/Billing")
        return self.metrics

def setUp(test):
    setupstack.setUpDirectory(test)
    dt = setupstack.context_manager(test, mock.patch("datetime.datetime"))
    dt.now = lambda : Metric.end
    setupstack.context_manager(
        test,
        mock.patch("boto.ec2.cloudwatch.connect_to_region",
                   side_effect = Connection),
        )


def test_suite():
    return doctest.DocFileSuite(
        "main.test", setUp = setUp, tearDown = setupstack.tearDown)
