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


from django.core import urlresolvers
from django.utils.translation import ugettext_lazy as _

from horizon import tables


def get_instance_link(instance):
    return urlresolvers.reverse('horizon:project:instances:detail',
                                kwargs={'instance_id': instance.instance_id})


def get_grafana_title(instance):
    return _('Monitor')


def get_grafana_link(instance):
    return instance.grafana_url


class OpenGrafana(tables.LinkAction):
    name = 'open-grafana'
    verbose_name = _('Open Grafana')
    # url = 'horizon:ofcloud:simulations:instances:open-grafana'
    classes = ('btn-launch')

    def get_link_url(self, datum):
        return datum.grafana_url


class OpenOSvDashboard(tables.LinkAction):
    name = 'open-dashboard'
    verbose_name = _('Open OSv Dashboard')
    classes = ('btn-dashboard')

    def get_link_url(self, datum):
        return 'http://%s:8000' % datum.ip


class DownloadInstanceCaseData(tables.LinkAction):
    name = 'download-instance-case-data'
    verbose_name = _('Download Instance Data')
    classes = ('btn-download-instance-case-data')

    def get_link_url(self, datum):
        return datum.download_case_url


class InstancesTable(tables.DataTable):
    id = tables.Column(
        'id',
        verbose_name=_('Id')
    )
    name = tables.Column(
        'name',
        link='horizon:horizon_openfoam:instances:detail',
        verbose_name=_('Instance Name')
    )
    config = tables.Column(
        'config',
        verbose_name=_('Simulation Configuration')
    )
    ip = tables.Column(
        'ip',
        verbose_name=_("IP Address"),
        attrs={'data-type': "ip"}
    )
    status = tables.Column(
        'status',
        verbose_name=_("Status"),
    )

    class Meta:
        name = 'instances'
        verbose_name = _("Instances")
        row_actions = (OpenGrafana, OpenOSvDashboard, DownloadInstanceCaseData,)


class ConfigTable(tables.DataTable):
    file = tables.Column('file',
                         verbose_name=_('Filename'))
    parameter = tables.Column('parameter',
                              verbose_name=_('Parameter'))
    value = tables.Column('value',
                          verbose_name=_('Value'))

    class Meta:
        name = 'config'
        verbose_name = _('Instance Configurations')
