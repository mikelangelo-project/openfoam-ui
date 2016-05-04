# OpenFOAM Cloud Dashboard

This repository provides a dashboard for the OpenStack Horizon application. To
use it, you must also install the [backend
application](https://github.com/mikelangelo-project/openfoam-cloud.git).

## Installing

In order to use the OpenFOAM Horizon dashboard, one must first clone the
OpenStack's Horizon project and checkout the Liberty version:

    git clone https://github.com/openstack/horizon.git
    git checkout stable/liberty

Install the required packages (we suggest to use virtualenv for this):

    cd horizon
    pip install -r requirements.txt

Then add the `ofcloud` dashboard submodule

    cd horizon/openstack_dashboard/dashboards/
    git submodule add --name ofcloud https://github.com/mikelangelo-project/openfoam-ui.git ofcloud

In order to enable the dashboard, go to `horizon/openstack_dashboard/enabled`.
This directory contains several files configuring the dashboards and panels.
File ordering is important in that it sets the structure of the Horizon
dashboard.

Create a file in this directory, for example `_50_ofcloud.py` and copy the 
following content:

    # The name of the dashboard to be added to HORIZON['dashboards']. Required.
    DASHBOARD = 'ofcloud'
    
    # If set to True, this dashboard will not be added to the settings.
    DISABLED = False
    
    # A list of applications to be added to INSTALLED_APPS.
    ADD_INSTALLED_APPS = [ 
        'openstack_dashboard.dashboards.ofcloud',
        ] 

Finally, edit the local settings file (`horizon/openstack_dashboard/local/local_settings.py`)
and put the following settings (replace with values appropriate to your
system setup):

    OFCLOUD_API_URL         = 'ofcloud-backend-url'
    S3_ACCESS_KEY_ID        = 'your-s3-key'
    S3_SECRET_ACCESS_KEY    = 'your-s3-secrect-key'
    S3_HOST                 = 's3-host'
    S3_PORT                 = s3-port

The `OFCLOUD_API_URL` is the root URL of the [OpenFOAM Backend](https://github.com/mikelangelo-project/openfoam-cloud.git).

## Running

Start the OpenStack Horizon application, login and look for the OpenFOAM Cloud
dashboard.

    cd horizon
    python manage.py runserver 0.0.0.0:8000

## Acknowledgements

This project  has been conducted within the RIA [MIKELANGELO
project](https://www.mikelangelo-project.eu) (no.  645402), started in January
2015, and co-funded by the European Commission under the H2020-ICT- 07-2014:
Advanced Cloud Infrastructures and Services programme.
