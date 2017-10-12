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


from django.utils.translation import ugettext_lazy as _

from horizon import tables
from horizon_openfoam.simulations import utils


class AddTableData(tables.LinkAction):
    name = 'add'
    verbose_name = _('Add Experiment')
    url = 'horizon:horizon_openfoam:simulations:add'
    classes = ('btn-launch', 'ajax-modal')


class DeleteTableData(tables.DeleteAction):
    data_type_singular = _("Experiment")
    data_type_plural = _("Experiments")

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
        link='horizon:horizon_openfoam:simulations:detail',
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
        verbose_name = _("Experiments")
        table_actions = (AddTableData, FilterAction,)
        row_actions = (DeleteTableData,)
