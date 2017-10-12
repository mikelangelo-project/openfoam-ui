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


import json

from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import tabs
from horizon.utils import functions as horizon_utils
from horizon_openfoam.instances.tables import ConfigTable
from horizon_openfoam.instances.utils import get_instance_log


class Config:
    def __init__(self, id, file, parameter, value):
        self.id = id
        self.file = file
        self.parameter = parameter
        self.value = value


class OverviewTab(tabs.Tab):
    name = _("Overview")
    slug = "overview"
    template_name = ("horizon_openfoam/instances/_detail_overview.html")

    def get_context_data(self, request):
        instance = self.tab_group.kwargs['instance']
        instance.instance_url = "horizon:project:instances:detail"

        return {"instance": instance}


class ConfigTab(tabs.TableTab):
    name = _("Configurations")
    slug = "configurations"
    table_classes = (ConfigTable,)
    template_name = "horizon_openfoam/instances/_detail_configurations.html"
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
    template_name = 'horizon_openfoam/instances/_detail_log.html'
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
