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
from collections import OrderedDict

from horizon import exceptions, tables, workflows
from openstack_dashboard import api
from horizon_openfoam.instances.tables import InstancesTable
from horizon_openfoam.simulations import utils
from horizon_openfoam.simulations.tables import SimulationTable
from horizon_openfoam.simulations.workflows import AddSimulation

LOG = logging.getLogger(__name__)


class SimulationsIndexView(tables.DataTableView):
    table_class = SimulationTable
    template_name = 'horizon_openfoam/simulations/index.html'

    def get_data(self):
        simulations = utils.getSimulations(self)

        # Gather our flavors and images and correlate our instances to them
        try:
            flavors = api.nova.flavor_list(self.request)
        except Exception:
            flavors = []
            exceptions.handle(self.request, ignore=True)

        full_flavors = OrderedDict([(str(flavor.id), flavor) for flavor in flavors])
        for simulation in simulations:
            try:
                flavor_id = simulation.flavor
                if flavor_id in full_flavors:
                    simulation.full_flavor = full_flavors[flavor_id]
                else:
                    # If the flavor_id is not in full_flavors list,
                    # get it via nova api.
                    simulation.full_flavor = api.nova.flavor_get(
                        self.request, flavor_id)
            except Exception:
                msg = ('Unable to retrieve flavor "%s" for experiment "%s".'
                       % (flavor_id, simulation.id))
                LOG.info(msg)

        return simulations


class DetailView(tables.DataTableView):
    table_class = InstancesTable
    template_name = 'horizon_openfoam/simulations/instances.html'

    def get_data(self):
        simulation_id = self.kwargs['simulation_id']

        return utils.get_simulation_instances(self, simulation_id)


class AddSimulationView(workflows.WorkflowView):
    workflow_class = AddSimulation

    def get_initial(self):
        initial = super(AddSimulationView, self).get_initial()
        return initial
