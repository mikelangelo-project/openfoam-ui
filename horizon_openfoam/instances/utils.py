# Copyright (C) 2015-2017 XLAB, Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import logging

import requests
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions

ofcloud_url = getattr(settings, 'OFCLOUD_API_URL', None)

LOG = logging.getLogger(__name__)


class Instance:
    def __init__(self, id, name, config, ip, instance_id, grafana_url, download_case_url, status):
        self.id = id
        self.name = name
        self.config = config
        self.ip = ip
        self.instance_id = instance_id
        self.grafana_url = grafana_url
        self.download_case_url = download_case_url
        self.status = status


def get_instances(self):
    try:
        r = requests.get(ofcloud_url + '/instances/')

        instances = []
        for instance in r.json():
            instances.append(Instance(
                id=instance['id'],
                name=instance['name'],
                config=instance['config'],
                ip=instance['ip'],
                instance_id=instance['instance_id'],
                grafana_url=instance['grafana_url'],
                download_case_url=instance['download_case_url'],
                status=instance['status']))

        return instances
    except:
        exceptions.handle(self.request, _('Unable to get instances'))
        return []


def get_instance(self, instance_id):
    try:
        r = requests.get(ofcloud_url + '/instances/%s/' % instance_id)

        instance = r.json()

        return Instance(
            id=instance['id'],
            name=instance['name'],
            config=instance['config'],
            ip=instance['ip'],
            instance_id=instance['instance_id'],
            grafana_url=instance['grafana_url'],
            download_case_url=instance['download_case_url'],
            status=instance['status'])
    except:
        exceptions.handle(self.request, _('Unable to retrieve details for instance %s' % instance_id))
        return []


def get_instance_log(request, instance_id, length):
    try:
        r = requests.get(ofcloud_url + '/instances/%s/log' % instance_id)

        cur_ix = r.text.rfind('\n')
        while cur_ix >= 0 and length > 1:
            cur_ix = r.text.rfind('\n', 0, cur_ix - 1)
            length -= 1

        return r.text[cur_ix:]
    except:
        exceptions.handle(request, _('Unable to retrieve the log for instance %s' % instance_id))
        return ""
