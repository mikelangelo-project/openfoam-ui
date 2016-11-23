import json

from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import tabs
from horizon.utils import functions as horizon_utils
from openstack_dashboard.dashboards.ofcloud.instances.tables import ConfigTable
from openstack_dashboard.dashboards.ofcloud.instances.utils import get_instance_log


class Config:
    def __init__(self, id, file, parameter, value):
        self.id = id
        self.file = file
        self.parameter = parameter
        self.value = value


class OverviewTab(tabs.Tab):
    name = _("Overview")
    slug = "overview"
    template_name = ("ofcloud/instances/_detail_overview.html")

    def get_context_data(self, request):
        instance = self.tab_group.kwargs['instance']
        instance.instance_url = "horizon:project:instances:detail"

        return {"instance": instance}


class ConfigTab(tabs.TableTab):
    name = _("Configurations")
    slug = "configurations"
    table_classes = (ConfigTable,)
    template_name = "ofcloud/instances/_detail_configurations.html"
    preload = False

    def get_config_data(self, ):
        instance = self.tab_group.kwargs['instance']

        configs = json.loads(instance.config)

        config_rows = []
        for ix, key in enumerate(sorted(configs.keys())):
            print(key)
            fileEndIndex = key.rfind('/')
            file = key[0:fileEndIndex]
            parameter = key[fileEndIndex + 1:]

            config_rows.append(Config(ix, file, parameter, configs[key]))

        return config_rows


class LogTab(tabs.Tab):
    name = _('Log')
    slug = 'log'
    template_name = 'ofcloud/instances/_detail_log.html'
    preload = False

    def get_context_data(self, request):
        instance = self.tab_group.kwargs['instance']
        log_length = horizon_utils.get_log_length(request)

        try:
            data = get_instance_log(request, instance.id, log_length)
        except:
            data = _('Unable to get log for instance "%s"') % instance.instance_id
            exceptions.handle(request, ignore=True)

        return {"instance": instance,
                "console_log": data,
                "log_length": log_length}


class DetailTabs(tabs.TabGroup):
    slug = "instance_details"
    tabs = (OverviewTab, ConfigTab, LogTab,)
    sticky = True
