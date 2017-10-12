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
import traceback

from django.core.validators import RegexValidator
from django.utils.translation import ugettext_lazy as _
from horizon import workflows, forms, exceptions
from horizon.utils import memoized
from openstack_dashboard import api
from openstack_dashboard.dashboards.project.instances import utils as instance_utils

from horizon_openfoam.simulations import utils


class SetAddSimulationDetailsAction(workflows.Action):
    simulation_name = forms.CharField(
        label=_('Name'),
        required=True,
        max_length=200,
        help_text=_('Name'))

    solver = forms.ChoiceField(
        label=_('Solver'),
        required=True,
        help_text=_('OpenFOAM solver'))

    image = forms.CharField(
        label=_('Image'),
        required=True,
        max_length=100,
        help_text=_('Image'))

    flavor = forms.ChoiceField(
        label=_('Flavor'),
        help_text=_('Flavor'))

    # this field has to be named count, because then it is bound to flavors_and_quotas directive
    count = forms.IntegerField(
        label=_('Instances'),
        required=True,
        initial=1,
        min_value=1,
        help_text=_('Number of instances')
    )

    class Meta:
        name = _('Details')
        help_text_template = ("project/instances/"
                              "_launch_details_help.html")

    def __init__(self, request, context, *args, **kwargs):
        self.request = request
        self.context = context

        super(SetAddSimulationDetailsAction, self).__init__(
            request, context, *args, **kwargs)

    @memoized.memoized_method
    def _get_flavor(self, flavor_id):
        try:
            # We want to retrieve details for a given flavor,
            # however flavor_list uses a memoized decorator
            # so it is used instead of flavor_get to reduce the number
            # of API calls.
            flavors = instance_utils.flavor_list(self.request)
            flavor = [x for x in flavors if x.id == flavor_id][0]
        except IndexError:
            flavor = None
        return flavor

    def populate_flavor_choices(self, request, context):
        return instance_utils.flavor_field_data(request, False)

    @memoized.memoized_method
    def _get_solver(self, solver_id):
        solver = None
        return solver

    def populate_solver_choices(self, request, context):
        return [('', _("select"))] + \
               [("openfoam.pimplefoam", _("pimpleFoam")),
                ("openfoam.pisofoam", _("pisoFoam")),
                ("openfoam.poroussimplefoam", _("poroussimpleFoam")),
                ("openfoam.potentialfoam", _("potentialFoam")),
                ("openfoam.rhoporoussimplefoam", _("rhoporoussimpleFoam")),
                ("openfoam.rhosimplefoam", _("rhosimpleFoam")),
                ("openfoam.simplefoam", _("simpleFoam"))]

    def get_help_text(self, extra_context=None):
        extra = {} if extra_context is None else dict(extra_context)
        try:
            extra['usages'] = api.nova.tenant_absolute_limits(self.request)
            extra['usages_json'] = json.dumps(extra['usages'])
            flavors = json.dumps([f._info for f in
                                  instance_utils.flavor_list(self.request)])
            extra['flavors'] = flavors

        except Exception:
            exceptions.handle(self.request,
                              _("Unable to retrieve quota information."))
        return super(SetAddSimulationDetailsAction, self).get_help_text(extra)


class SetAddPSimulationDetails(workflows.Step):
    action_class = SetAddSimulationDetailsAction
    contributes = ('simulation_name', 'image', 'flavor', 'solver', 'container_name', 'input_data_object', 'count')

    def contribute(self, data, context):
        if data:
            context['simulation_name'] = data.get('simulation_name', '')
            context['image'] = data.get('image', '')
            context['flavor'] = data.get('flavor', '')
            context['solver'] = data.get('solver', '')
            context['count'] = data.get('count', 1)

        return context


class InputDataAction(workflows.Action):
    container_name = forms.CharField(
        label=_('Object container name'),
        required=True,
        max_length=50,
        initial='mikelangelo-cases',
        help_text=_('Object container name'))

    input_data_object = forms.ChoiceField(
        label=_('Input data'),
        help_text=_('Input data'))

    class Meta:
        name = _('Input Data')

    def __init__(self, request, context, *args, **kwargs):
        self.request = request
        self.context = context

        super(InputDataAction, self).__init__(
            request, context, *args, **kwargs)

    def populate_input_data_object_choices(self, request, context):
        return utils.objects_field_data(request, "mikelangelo-cases")


class InputData(workflows.Step):
    action_class = InputDataAction
    contributes = ('container_name', 'input_data_object')

    def contribute(self, data, context):
        if data:
            context['container_name'] = data.get('container_name', '')
            context['input_data_object'] = data.get('input_data_object', '')

        return context


class CustomisationAction(workflows.Action):
    cases = forms.CharField(
        label=_('Cases'),
        help_text=_('Case Customisations'),
        widget=forms.widgets.Textarea(attrs={
            'class': 'switched',
            'data-switch-on': 'cases',
            'data-scriptsource-raw': _('Case Customisations')}),
        required=False)

    class Meta:
        name = _('Case Customisations')

    def __init__(self, request, context, *args, **kwargs):
        self.request = request
        self.context = context

        super(CustomisationAction, self).__init__(
            request, context, *args, **kwargs)


class Customisation(workflows.Step):
    action_class = CustomisationAction
    contributes = ('cases')

    def contribute(self, data, context):
        if data:
            context['cases'] = data.get('cases', 'empty')

        return context


class DecompositionAction(workflows.Action):
    xyz_validator = RegexValidator(regex='^([0-9]+) ([0-9]+) ([0-9]+)$',
                                   message='Number of subdomains in "x y z" format. Example "2 1 2"')

    subdomains = forms.IntegerField(
        label=_('Total number of subdomains'),
        required=False,
        min_value=1,
    )

    decomposition_method = forms.ChoiceField(
        label=_('Decomposition method'),
        required=False,
        help_text=_('OpenFOAM decomposition method')
    )

    n = forms.CharField(
        label=_('Number of subdomains in x, y, z'),
        required=False,
        help_text=_('Number of subdomains in x, y, z'),
        validators=[xyz_validator]
    )

    delta = forms.FloatField(
        label=_('Delta'),
        required=False,
        help_text=_('Cell skew factor'),
        min_value=0
    )

    order = forms.ChoiceField(
        label=_('Order'),
        required=False,
        help_text=_('Order of decomposition')
    )

    strategy = forms.CharField(
        label=_('Strategy'),
        required=False,
        help_text=_('Decomposition strategy: optional and complex')
    )

    processor_weights = forms.CharField(
        label=_('Processor weights'),
        required=False,
        help_text=_(
            'List of weighting factors for allocation of cells to processors; <wt1> is the weighting factor for '
            'processor 1, etc. ; weights are normalised so can take any range of values.')
    )

    datafile = forms.CharField(
        label=_('Data file'),
        required=False,
        help_text=_('Name of file containing data of allocation of cells to processors ')
    )

    class Meta:
        name = _('Decomposition method customization')

    def __init__(self, request, context, *args, **kwargs):
        self.request = request
        self.context = context

        super(DecompositionAction, self).__init__(
            request, context, *args, **kwargs)

    def populate_decomposition_method_choices(self, request, context):
        return [('', _("select"))] + \
               [('simple', _("Simple")),
                ('hierarchical', _("Hierarchical")),
                ('scotch', _("Scotch")),
                ('manual', _("Manual"))]

    def populate_order_choices(self, request, context):
        return [('xyz', _('xyz')),
                ('xzy', _('xzy')),
                ('yxz', _('yxz')),
                ('yzx', _('yzx')),
                ('zxy', _('zxy')),
                ('zyx', _('zyx'))]


class Decomposition(workflows.Step):
    action_class = DecompositionAction
    contributes = 'decomposition'

    def contribute(self, data, context):
        if data:
            context['decomposition'] = {
                'subdomains': data.get('subdomains'),
                'decomposition_method': data.get('decomposition_method'),
                'n': data.get('n'),
                'delta': data.get('delta'),
                'order': data.get('order'),
                'strategy': data.get('strategy'),
                'processor_weights': data.get('processor_weights'),
                'datafile': data.get('datafile')
            }
        return context


class AddSimulation(workflows.Workflow):
    slug = 'add'
    name = _('Launch new experiment')
    finalize_button_name = _('Launch')
    success_message = _('Added experiment "%s".')
    failure_message = _('Unable to add provider "%s".')
    success_url = 'horizon:horizon_openfoam:simulations:index'
    failure_url = 'horizon:horizon_openfoam:simulations:index'
    default_steps = (
        SetAddPSimulationDetails,
        InputData,
        Customisation,
        Decomposition)

    def format_status_message(self, message):
        return message % self.context.get('simulation_name', 'unknown experiment')

    def handle(self, request, context):
        try:
            utils.addSimulation(self, request, context)
            return True
        except Exception:
            print traceback.format_exc()
            exceptions.handle(request, _("Unable to add experiment"))
            return False
