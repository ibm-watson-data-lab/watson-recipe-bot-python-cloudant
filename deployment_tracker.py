import time
import json
from re import search
from requests import post
from os import environ as env


def track(tracker_url=None):

    # version and repository URL
    version = '0.0.1'
    repo_url = 'https://github.com/ibm-cds-labs/watson-recipe-bot-python-cloudant'

    # get vcap application details
    if env.get('VCAP_APPLICATION') is not None:
        vcap_app = json.loads(env['VCAP_APPLICATION'])
        event = dict()
        event['date_sent'] = time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime())
        if version is not None:
            event['code_version'] = version
        if repo_url is not None:
            event['repository_url'] = repo_url
        event['runtime'] = 'python'
        event['application_name'] = str(vcap_app['name'])
        event['space_id'] = str(vcap_app['space_id'])
        event['application_version'] = str(vcap_app['application_version'])
        event['application_uris'] = [str(uri) for uri in vcap_app['application_uris']]

        # Check for VCAP_SERVICES env var with at least one service
        # Refer to http://docs.cloudfoundry.org/devguide/deploy-apps/environment-variable.html#VCAP-SERVICES
        if env.get('VCAP_SERVICES') is not None and json.loads(env['VCAP_SERVICES']):
            vcap_services = json.loads(env['VCAP_SERVICES'])
            event['bound_vcap_services'] = dict()

            # For each bound service, count the number of instances and identify used plans
            for service in vcap_services:
                event['bound_vcap_services'][service] = {
                    'count': len(vcap_services[service]),
                    'plans': []
                }

                # Append plans for each instance
                for instance in vcap_services[service]:
                    if 'plan' in instance.keys():
                        event['bound_vcap_services'][service]['plans'].append(str(instance['plan']))

                if len(event['bound_vcap_services'][service]['plans']) == 0:
                    del event['bound_vcap_services'][service]['plans']

        # Create and format request to Deployment Tracker
        url = 'https://deployment-tracker.mybluemix.net/api/v1/track' if tracker_url is None else tracker_url
        headers = {'content-type': "application/json"}
        try:
            print ('Uploading stats to Deployment Tracker: {}'.format(json.dumps(event)))
            response = post(url, data=json.dumps(event), headers=headers)
            print ('Uploaded stats: %s' % response.text)
        except Exception as e:
            print ('Deployment Tracker upload error: %s' % str(e))