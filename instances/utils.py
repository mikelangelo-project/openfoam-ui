import traceback, logging, json

from django.utils.translation import ugettext_lazy as _

from horizon import exceptions

import requests

ofcloud_url = 'http://10.211.55.101:8000'

LOG = logging.getLogger(__name__)


class Instance:
    def __init__(self, id, name, config, ip, instance_id, grafana_url, download_case_url):
        self.id = id
        self.name = name
        self.config = config
        self.ip = ip
        self.instance_id = instance_id
        self.grafana_url = grafana_url
        self.download_case_url = download_case_url


def get_instances(self):
    try:
        r = requests.get(ofcloud_url + '/instances/')

        instances = []
        for instance in r.json():
            instances.append(Instance(
                instance['id'],
                instance['name'],
                instance['config'],
                instance['ip'],
                instance['instance_id'],
                instance['grafana_url'],
                instance['download_case_url']))

        return instances
    except:
        exceptions.handle(self.request, _('Unable to get instances'))
        return []


def get_instance(self, instance_id):
    try:
        r = requests.get(ofcloud_url + '/instances/%s/' % instance_id)

        instance = r.json()

        return Instance(
                        instance['id'],
                        instance['name'],
                        instance['config'],
                        instance['ip'],
                        instance['instance_id'],
                        instance['grafana_url'],
                        instance['download_case_url'])
    except:
        exceptions.handle(self.request, _('Unable to retrieve details for instance %s' % instance_id))
        return []

def get_instance_log(request, instance_id, length):
    try:
        r = requests.get(ofcloud_url + '/instances/%s/log' % instance_id)

        cur_ix = r.text.rfind('\n')
        while cur_ix >= 0 and length > 1:
            print "BLAH %d" % cur_ix
            cur_ix = r.text.rfind('\n', 0, cur_ix - 1)
            length -= 1

        return r.text[cur_ix:]
    except:
        exceptions.handle(request, _('Unable to retrieve the log for instance %s' % instance_id))
        return ""

