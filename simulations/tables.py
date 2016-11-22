from django.utils.translation import ugettext_lazy as _

from horizon import tables
from openstack_dashboard.dashboards.ofcloud.simulations import utils


class AddTableData(tables.LinkAction):
    name = 'add'
    verbose_name = _('Add Simulation')
    url = 'horizon:ofcloud:simulations:add'
    classes = ('btn-launch', 'ajax-modal')


class DeleteTableData(tables.DeleteAction):
    data_type_singular = _("Simulation")
    data_type_plural = _("Simulations")

    def delete(self, request, obj_id):
        utils.delete_simulation(self, obj_id)


class FilterAction(tables.FilterAction):
    name = "simfilter"


def get_flavor(simulation):
    if hasattr(simulation, 'full_flavor'):
        return simulation.full_flavor.name
    else:
        return simulation.flavor


class SimulationTable(tables.DataTable):
    id = tables.Column(
        'id',
        verbose_name=_('Id')
    )
    name = tables.Column(
        'simulation_name',
        link='horizon:ofcloud:simulations:detail',
        verbose_name=_('Name')
    )
    solver = tables.Column(
        'solver',
        verbose_name=_('Solver')
    )
    image = tables.Column(
        'image',
        verbose_name=_('Image')
    )
    flavor = tables.Column(
        get_flavor,
        verbose_name=_('flavor')
    )
    container_name = tables.Column(
        "container_name",
        verbose_name=_('Container')
    )
    input_data_object = tables.Column(
        "input_data_object",
        verbose_name=_('Input data')
    )

    class Meta:
        name = 'simulations'
        verbose_name = _("Simulations")
        table_actions = (AddTableData, FilterAction,)
        row_actions = (DeleteTableData,)
