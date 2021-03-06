#!/usr/bin/env python
import urllib2
import urllib
import json
import requests
import sys

ckan_base = 'http://127.0.0.1:5000'
ckan_api_key = '5d9d0f6c-cab6-4704-9c03-3713044d5770'
package_id = 'dataset-of-datasets'

#function to get all the site package lists and its resources
def get_packages_data():
    response=[]
    package_list = requests.get(ckan_base + '/api/3/action/package_list',headers={'X-CKAN-API-Key':ckan_api_key,'Content-type':'application/x-www-form-urlencoded'})
    package_list = package_list.json()['result']

    for package in package_list:
        if package == package_id:
            continue
        try:
            post_dict = {'id':package}
            post_dict  = urllib.quote(json.dumps(post_dict))
            r = requests.post(ckan_base + '/api/3/action/package_show',data=post_dict,headers={'X-CKAN-API-Key':ckan_api_key,'Content-type':'application/x-www-form-urlencoded'})
            response.append(r.json()['result'])
        except:
            print "Error fetching package data for "+package

    return response

#function to get the schema dataset fields
def get_dataset_fields():
    schema_dataset_fields = []
    try:
        r = requests.get(ckan_base + '/api/3/action/scheming_dataset_schema_show?type=dataset',headers={'X-CKAN-API-Key':ckan_api_key,'Content-type':'application/x-www-form-urlencoded'})
        schema_dataset_fields = r.json()['result']['dataset_fields']
    except:
        print "Error fetching dataset schema fields"

    dataset_fields = {}
    for schema_dataset_field in schema_dataset_fields:
        dataset_fields[schema_dataset_field['field_name']] = schema_dataset_field['label']
    return dataset_fields

#function to get the package tags as comma seperated string
def get_package_tags(tags_dict):
    """
    Build out the tag names comma separated string
    """
    tags = [tag.get('display_name') for tag in tags_dict]
    return ",".join(tags)

#get the dataset to which resource is to be created/updated
try:
    post_dict = {'id':package_id}
    post_dict  = urllib.quote(json.dumps(post_dict))
    r = requests.post(ckan_base + '/api/3/action/package_show',data=post_dict,headers={'X-CKAN-API-Key':ckan_api_key,'Content-type':'application/x-www-form-urlencoded'})
    package_data = r.json()['result']
    resources = package_data['resources']
except:
    print "Error fetching package data for "+package_id
    sys.exit()


dataset_fields = get_dataset_fields()
#if dataset has no exisiting resource then create a resource and add records
if len(resources) == 0:
    #create a resource and add data to the created resource
    site_packages = get_packages_data()
    records = []
    for site_package in site_packages:
        record_data = {}
        for key in dataset_fields:
            if key in site_package or key == 'tag_string':
                if key == 'tag_string':
                    record_data[dataset_fields[key]] = get_package_tags(site_package.get('tags'))
                elif key == 'owner_org':
                    if site_package['owner_org'] is not None:
                        record_data[dataset_fields[key]] = site_package['organization']['title']
                    else:
                        record_data[dataset_fields[key]] = ''
                else:
                    record_data[dataset_fields[key]] = site_package[key]
            else:
                record_data[dataset_fields[key]] = ''
        records.append(record_data)
    post_dict = {'resource':{'package_id':'dataset-of-datasets','name':'Datasets List','resource_type':'csv'},'records':records,'primary_key':['URL']}
    post_dict  = urllib.quote(json.dumps(post_dict))
    r = requests.post(ckan_base + '/api/3/action/datastore_create',data=post_dict,headers={'X-CKAN-API-Key':ckan_api_key,'Content-type':'application/x-www-form-urlencoded'})
    result = r.json()
else:
    res_id = resources[0]['id']
    #update data to the existing resource
    site_packages = get_packages_data()
    records = []
    for site_package in site_packages:
        record_data = {}

        for key in dataset_fields:
            if key in site_package or key == 'tag_string':
                if key == 'tag_string':
                    record_data[dataset_fields[key]] = get_package_tags(site_package.get('tags'))
                elif key == 'owner_org':
                    if site_package['owner_org'] is not None:
                        record_data[dataset_fields[key]] = site_package['organization']['title']
                    else:
                        record_data[dataset_fields[key]] = ''
                else:
                    record_data[dataset_fields[key]] = site_package[key]
            else:
                record_data[dataset_fields[key]] = ''
        records.append(record_data)

    post_dict = {'resource_id':res_id,'records':records}
    post_dict  = urllib.quote(json.dumps(post_dict))
    r = requests.post(ckan_base + '/api/3/action/datastore_upsert',data=post_dict,headers={'X-CKAN-API-Key':ckan_api_key,'Content-type':'application/x-www-form-urlencoded'})
    result = r.json()
