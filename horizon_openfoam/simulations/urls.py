# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from django.conf.urls import patterns
from django.conf.urls import url

from horizon_openfoam.simulations import views

VIEW_MOD = 'horizon_openfoam.simulations.views'

urlpatterns = patterns(
    VIEW_MOD,
    url(r'^$', views.SimulationsIndexView.as_view(), name='index'),
    url(r'^add$', views.AddSimulationView.as_view(), name='add'),
    url(r'^(?P<simulation_id>[^/]+)/$',
        views.DetailView.as_view(), name='detail'),
)
