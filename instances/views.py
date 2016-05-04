from collections import OrderedDict
import logging

from django import http
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions, tables, views, forms, tabs, workflows

from openstack_dashboard import api
from openstack_dashboard.dashboards.ofcloud.instances import utils

from openstack_dashboard.dashboards.ofcloud.instances \
        import tabs as ofcloud_tabs
from openstack_dashboard.dashboards.ofcloud.instances.tables import InstancesTable
from openstack_dashboard.dashboards.ofcloud.instances.utils import get_instance_log

import requests

LOG = logging.getLogger(__name__)


class IndexView(tables.DataTableView):
    table_class = InstancesTable
    template_name = 'ofcloud/instances/index.html'

    def get_data(self):
        instances = utils.get_instances(self)
        return instances

class DetailView(tabs.TabView):
    tab_group_class = ofcloud_tabs.DetailTabs
    template_name = 'ofcloud/instances/detail.html'
    # redirect_url = 'horizon:ofcloud:instances:index'
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
