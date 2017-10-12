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
import logging
import traceback

import boto
import boto.s3.connection
import requests
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon_openfoam.instances.utils import Instance

ofcloud_url = getattr(settings, 'OFCLOUD_API_URL', None)

LOG = logging.getLogger(__name__)


class Simulation:
    def __init__(self, id, simulation_name, image, flavor, solver, instance_count, container_name, input_data_object):
        self.id = id
        self.simulation_name = simulation_name
        self.image = image
        self.flavor = flavor
        self.solver = solver
        self.instance_count = instance_count
        self.container_name = container_name
        self.input_data_object = input_data_object


def getSimulations(self):
    try:
        r = requests.get(ofcloud_url + '/simulations/')

        simulations = []
        for sim in r.json():
            simulations.append(Simulation(
                id=sim['id'],
                simulation_name=sim['simulation_name'],
                image=sim['image'],
                flavor=sim['flavor'],
                solver=sim.get('solver', ''),
                instance_count=sim['instance_count'],
                container_name=sim['container_name'],
                input_data_object=sim['input_data_object']))

        return simulations
    except:
        exceptions.handle(self.request, _('Unable to get experiments'))
        return []


# request - horizon environment settings
# context - user inputs from form
def addSimulation(self, request, context):
    try:
        simulation_name = context.get('simulation_name')
        image = context.get('image')
        flavor = context.get('flavor')
        solver = context.get('solver')
        instance_count = context.get('count')
        container_name = context.get('container_name')
        input_data_object = context.get('input_data_object')
        cases = context.get('cases')
        decomposition = context.get('decomposition')

        payload = {
            'simulation_name': simulation_name,
            'image': image,
            'flavor': flavor,
            'solver': solver,
            'instance_count': instance_count,
            'container_name': container_name,
            'input_data_object': input_data_object,
            'cases': json.dumps(cases) if cases else "",
            'decomposition': json.dumps(decomposition) if decomposition else ""
        }

        requests.post(ofcloud_url + "/simulations/", json=payload)

    except:
        print "Exception inside utils.addSimulation"
        print traceback.format_exc()
        exceptions.handle(self.request, _('Unable to add experiment'))

        return []


def delete_simulation(self, id):
    try:
        requests.delete(ofcloud_url + "/simulations/" + id)

    except:
        print traceback.format_exc()
        exceptions.handle(self.request,
                          _('Unable to delete experiment.'))

        return False


class ObjectKey:
    def __init__(self, id, name):
        self.id = id
        self.name = name


def object_list(request, container_name):
    """Utility method to retrieve a list of objects from the given container."""
    try:
        conn = boto.connect_s3(
            aws_access_key_id=settings.S3_ACCESS_KEY_ID,
            aws_secret_access_key=settings.S3_SECRET_ACCESS_KEY,
            host=settings.S3_HOST,
            port=settings.S3_PORT,
            calling_format=boto.s3.connection.OrdinaryCallingFormat(),
        )

        bucket = conn.get_bucket(container_name)

        objects = []
        # Asume inputs/ prefix is used
        for key in bucket.list():
            if not key.name.endswith('/'):
                objects.append(ObjectKey(key.name, key.name))

        return objects

    # return swift.swift_get_objects(request, container_name)
    except:
        exceptions.handle(request,
                          _('Unable to retrieve objects in %s container' % container_name))
        return []


def sort_object_list(request, objects):
    def get_key(obj, sort_key):
        try:
            return getattr(obj, sort_key)
        except AttributeError:
            LOG.warning('Could not find sort key "%s". Using default '
                        '"name" instead.', sort_key)
            return getattr(obj, 'name')

    # try:
    sort_key = 'name'
    key = lambda obj: get_key(obj, sort_key)

    object_list = [(obj.id, '%s' % obj.name) for obj in sorted(objects, key=key)]

    return object_list


def objects_field_data(request, container_name):
    objects = object_list(request, container_name)
    if objects:
        objects_list = sort_object_list(request, objects)
        return [("", _("Select Object")), ] + objects_list

    return [("", _("No objects available")), ]


def get_simulation_instances(self, simulation_id):
    try:
        r = requests.get(ofcloud_url + '/simulations/%s/' % simulation_id)

        instances = []
        for instance in r.json()['instances']:
            instances.append(Instance(
                instance['id'],
                instance['name'],
                instance['config'],
                instance['ip'],
                instance['instance_id'],
                instance['grafana_url'],
                instance['download_case_url'],
                instance['status']))

        return instances
    except:
        exceptions.handle(self.request, _('Unable to get instances for experiment %s' % simulation_id))
        return []
