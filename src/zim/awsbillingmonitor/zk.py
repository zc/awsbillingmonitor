import re
import zc.metarecipe
import zc.zk


class Recipe(zc.metarecipe.Recipe):

    def __init__(self, buildout, name, options):

        super(Recipe, self).__init__(buildout, name, options)

        assert name.endswith('.0'), name # There can be only one.
        name = name[:-2]

        zk = self.zk = zc.zk.ZK('zookeeper:2181')

        path = '/' + name.replace(',', '/')
        zkoptions = zk.properties(path, False)

        region = zkoptions.get('region')

        self['deployment'] = dict(
            recipe = 'zc.recipe.deployment',
            name=name,
            user=zkoptions.get('user', 'zope'),
            )

        zim_text = ''
        cimaa_text = ''
        for k, v in sorted(zkoptions.items()):
            if not re.match('[A-Z]', k):
                continue
            assert len(v) == 2, ("bad option", k, v)
            warn, error = v
            data = dict(
                region=region,
                name=(name + '-' + k),
                metric=k,
                warn=warn,
                error=error,
                )
            zim_text += zim_template % data
            cimaa_text += cimaa_template % data

        self[name + '-zim.cfg'] = dict(
            recipe = 'zc.recipe.deployment:configuration',
            deployment = 'deployment',
            text = zim_text,
            directory = "/etc/zim/agent.d",
            )

        self[name + '.cfg'] = dict(
            recipe = 'zc.recipe.deployment:configuration',
            deployment = 'deployment',
            text = cimaa_text,
            directory = "/etc/cimaa/monitors.d",
            )

zim_template = """
[%(name)s]
class = zim.nagiosplugin.Monitor
interval = 3600
/awsbilling/%(metric)s = /opt/awsbillingmonitor/bin/awsbillingmonitor
    %(region)s %(metric)s %(warn)s %(error)s
"""

cimaa_template = """
[%(name)s]
command = /opt/awsbillingmonitor/bin/awsbillingmonitor %(region)s %(metric)s %(warn)s %(error)s
interval = 600
"""
