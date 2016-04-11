from django.core import urlresolvers
from django.utils.translation import ugettext_lazy as _

from horizon import tables

from openstack_dashboard.dashboards.ofcloud.simulations import utils


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
    id = tables.Column('id',
            verbose_name=_('Id'))
    name = tables.Column('name',
                         link='horizon:ofcloud:instances:detail',
                         verbose_name=_('Instance Name'))
    # name = tables.Column('name',
                         # link=get_instance_link,
                         # verbose_name=_('Instance Name'))
    config = tables.Column('config',
                           verbose_name=_('Simulation Configuration'))
    ip = tables.Column('ip',
                       verbose_name=_("IP Address"),
                       attrs={'data-type': "ip"})

    class Meta:
        name = 'instances'
        verbose_name = _("Instances")
        row_actions = (OpenGrafana, OpenOSvDashboard,DownloadInstanceCaseData,)


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
