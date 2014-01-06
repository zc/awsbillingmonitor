"""%prog region METRIC warning_rate error_rate

Check expense rates, in dollars/hour, for a CloudWatch billing metric.

Available metrics: "Total", or any valid CloudWatch billing service name.

Note that rates are only updated every few hours so these checks
aren't really timely or precise, but they're better than nothing.

This monitor wouldn't be needed if CloudWatch had alarms for billing
rates, not just totals.

This monitor works by retrieving maximum-5-minute CloudWatch billing
data for the previous day, and computing a rate for the most recent 2
values.  Because rates are only updated every few hours, it doesn't
make sense to run this monitor more often than about once an hour.

WRT credentials, the monitor can used temprary instance credentials
(instance roles) and if run on an AWS instance, this is the easiest
way to authenticate the monitor.  You can also supply credentials via
a ~/.boto file for the user running the monitor.
"""

import boto.ec2.cloudwatch
import datetime
import sys

def main(args=None):
    if args is None:
        args = sys.argv[1:]

    region, metric_name, warn, error = args
    conn = boto.ec2.cloudwatch.connect_to_region(region)
    metrics = conn.list_metrics(
        metric_name="EstimatedCharges", namespace="AWS/Billing")

    end = datetime.datetime.now()
    start = end - datetime.timedelta(days=1)

    warn, error = [float(r) for r in (warn, error)]
    if metric_name == 'Total':
        metric = None
    else:
        metric = [metric_name]
    [metric] = [m for m in metrics
                if m.dimensions.get('ServiceName') == metric]
    v1, v2 = sorted(metric.query(start, end, 'Maximum', None, period=300),
                    key=lambda x: x['Timestamp'])[-2:]
    rate = int((
        (v2['Maximum'] - v1['Maximum'])
        /
        ((v2['Timestamp'] - v1['Timestamp']).seconds / 3600)
        )+.5)
    if rate > error:
        print metric_name, rate, ">", error
        return 2
    elif rate > warn:
        print metric_name, rate, ">", warn
        return 1
    else:
        print metric_name, rate
        return 0
