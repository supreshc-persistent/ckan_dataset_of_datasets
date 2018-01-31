#!/usr/bin/env python
import urllib2
import urllib
import json
import requests

#from ckanext.scheming import helpers

#function to get all the site package lists and its resources
def get_packages_data():
    response=[]
    #r = requests.get('http://127.0.0.1:5000/api/3/action/current_package_list_with_resources',headers={'X-CKAN-API-Key':ckan_api_key,'Content-type':'application/x-www-form-urlencoded'})
    package_list = requests.get('http://127.0.0.1:5000/api/3/action/package_list',headers={'X-CKAN-API-Key':ckan_api_key,'Content-type':'application/x-www-form-urlencoded'})
    package_list = package_list.json()['result']

    for package in package_list:
        post_dict = {'id':package}
        post_dict  = urllib.quote(json.dumps(post_dict))
        r = requests.post('http://127.0.0.1:5000/api/3/action/package_show',data=post_dict,headers={'X-CKAN-API-Key':ckan_api_key,'Content-type':'application/x-www-form-urlencoded'})
        response.append(r.json()['result'])

    return response

ckan_api_key = '5d9d0f6c-cab6-4704-9c03-3713044d5770'

#todo get these fields from the schema files
dataset_fields = {'title':'Title','name':'URL','notes':'Description','owner_org':'Department','contact_email':'Contact Email'}

#get the dataset to which resource is to be created/updated
post_dict = {'id':'dataset-of-datasets'}
post_dict  = urllib.quote(json.dumps(post_dict))
r = requests.post('http://127.0.0.1:5000/api/3/action/package_show',data=post_dict,headers={'X-CKAN-API-Key':ckan_api_key,'Content-type':'application/x-www-form-urlencoded'})

package_data = r.json()['result']
resources = package_data['resources']

#if dataset has no exisiting resource then create a resource and add records
if len(resources) == 0:
    #create a resource and add data to the created resource
    site_packages = get_packages_data()
    records = []
    for site_package in site_packages:
        record_data = {}
        for key in dataset_fields:
            if key in site_package:
                record_data[dataset_fields[key]] = site_package[key]
        records.append(record_data)
    post_dict = {'resource':{'package_id':'dataset-of-datasets','name':'Datasets List','resource_type':'csv'},'records':records,'primary_key':['URL']}
    post_dict  = urllib.quote(json.dumps(post_dict))
    r = requests.post('http://127.0.0.1:5000/api/3/action/datastore_create',data=post_dict,headers={'X-CKAN-API-Key':ckan_api_key,'Content-type':'application/x-www-form-urlencoded'})
    result = r.json()
    print result
else:
    res_id = resources[0]['id']
    #update data to the existing resource
    site_packages = get_packages_data()
    records = []
    for site_package in site_packages:
        record_data = {}
        for key in dataset_fields:
            if key in site_package:
                record_data[dataset_fields[key]] = site_package[key]
        records.append(record_data)
    post_dict = {'resource_id':res_id,'records':records}
    post_dict  = urllib.quote(json.dumps(post_dict))
    r = requests.post('http://127.0.0.1:5000/api/3/action/datastore_upsert',data=post_dict,headers={'X-CKAN-API-Key':ckan_api_key,'Content-type':'application/x-www-form-urlencoded'})
    result = r.json()
    print result
