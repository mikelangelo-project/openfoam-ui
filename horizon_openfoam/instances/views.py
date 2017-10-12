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
from django import http
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions, tables, tabs
from horizon_openfoam.instances import tabs as ofcloud_tabs
from horizon_openfoam.instances import utils
from horizon_openfoam.instances.tables import InstancesTable
from horizon_openfoam.instances.utils import get_instance_log

LOG = logging.getLogger(__name__)


class IndexView(tables.DataTableView):
    table_class = InstancesTable
    template_name = 'horizon_openfoam/instances/index.html'

    def get_data(self):
        instances = utils.get_instances(self)
        return instances


class DetailView(tabs.TabView):
    tab_group_class = ofcloud_tabs.DetailTabs
    template_name = 'horizon_openfoam/instances/detail.html'
    page_title = _("Instance Details: {{ instance.name }}")

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        instance = self.get_data()

        context["instance"] = instance
        context["actions"] = self._get_actions(instance)
        return context

    def _get_actions(self, instance):
        table = InstancesTable(self.request)
        return table.render_row_actions(instance)

    def get_data(self):
        instance_id = self.kwargs['instance_id']

        instance = utils.get_instance(self, instance_id)

        return instance

    def get_tabs(self, request, *args, **kwargs):
        instance = self.get_data()
        return self.tab_group_class(request, instance=instance, **kwargs)


def console(request, instance_id):
    data = _('Unable to get log for instance "%s".') % instance_id
    tail = request.GET.get('length')
    if tail and not tail.isdigit():
        msg = _('Log length must be a nonnegative integer.')
        messages.warning(request, msg)
    else:
        try:
            data = get_instance_log(request, instance_id, int(tail))
        except Exception:
            exceptions.handle(request, ignore=True)
    return http.HttpResponse(data.encode('utf-8'), content_type='text/plain')


def download(request, instance_id):
    try:
        r = requests.get(getattr(settings, 'OFCLOUD_API_URL', None) + '/instances/%s/download' % instance_id)

        response = http.HttpResponse(r.content, content_type='application/x-gzip')
        response['Content-Disposition'] = r.headers['Content-Disposition']

        return response
    except:
        exceptions.handle(request, ignore=True)
