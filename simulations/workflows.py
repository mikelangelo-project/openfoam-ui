from django.utils.translation import ugettext_lazy as _

from horizon import workflows, forms, exceptions
from horizon.utils import memoized
from openstack_dashboard.dashboards.ofcloud.simulations import utils
from openstack_dashboard.dashboards.project.instances \
    import utils as instance_utils


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

    class Meta:
        name = _('Details')

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


class SetAddPSimulationDetails(workflows.Step):
    action_class = SetAddSimulationDetailsAction
    contributes = ('simulation_name', 'image', 'flavor', 'solver', 'container_name', 'input_data_object')

    def contribute(self, data, context):
        if data:
            context['simulation_name'] = data.get('simulation_name', '')
            context['image'] = data.get('image', '')
            context['flavor'] = data.get('flavor', '')
            context['solver'] = data.get('solver', '')

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


class AddSimulation(workflows.Workflow):
    slug = 'add'
    name = _('Launch new simulation')
    finalize_button_name = _('Launch')
    success_message = _('Added simulation "%s".')
    failure_message = _('Unable to add provider "%s".')
    success_url = 'horizon:ofcloud:simulations:index'
    failure_url = 'horizon:ofcloud:simulations:index'
    default_steps = (
        SetAddPSimulationDetails,
        InputData,
        Customisation)

    def format_status_message(self, message):
        return message % self.context.get('simulation_name', 'unknown simulation')

    def handle(self, request, context):
        try:
            utils.addSimulation(self, request, context)
            return True
        except Exception:
            print traceback.format_exc()
            exceptions.handle(request, _("Unable to add simulation"))
            return False
