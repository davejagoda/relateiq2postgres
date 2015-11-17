#!/usr/bin/env python

import argparse, os, sys, requests, json, logging, pprint

def get_static_schema(object, verbose=False):
    if verbose:
        for key in object.keys():
            print('key:{} type(object[key]):{}'.format(key, type(object[key])))
            if list != type(object[key]):
                print('{}-{}'.format(key,object[key]))
    return(object['id'],object['listType'],object['title'])

def get_dynamic_schema(object, verbose=False):
    columns = []
    if verbose:
        pprint.pprint(object['fields'])
    for field in object['fields']:
        assert(7 == len(field.keys()))
        assert(unicode == type(field['dataType']))
        assert(unicode == type(field['id']))
        assert(unicode == type(field['name']))
        assert(bool == type(field['isEditable']))
        assert(bool == type(field['isLinkedField']))
        assert(bool == type(field['isMultiSelect']))
        assert(list == type(field['listOptions']))
        columns.append((field['id'],field['name'], field['dataType']))
    return(columns)

def get_lists(riq_key, riq_secret, verbose=False):
    url = 'https://api.salesforceiq.com/v2/lists'
    r = requests.request('GET', url, auth=(riq_key,riq_secret))
    assert(unicode == type(r.text))
    assert(200 == r.status_code)
    if verbose: print(r.text)
    d = json.loads(r.text)
    assert(dict == type(d))
    assert(2 == len(d))
    assert(d['nextPage'] == None)
    assert(list == type(d['objects']))
    if verbose: print('# of objects:{}'.format(len(d['objects'])))
    for object in d['objects']:
        assert(6 == len(object.keys()))
        assert(0 == object['size']) # omit
        assert(0 == object['modifiedDate']) # omit
        assert(unicode == type(object['id']))
        assert(unicode == type(object['title']))
        assert(unicode == type(object['listType']))
        assert(list == type(object['fields']))
    return(d['objects'])

if '__main__' == __name__:
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--suppressSSLwarning', action='store_true', help='suppress SSL warning')
    parser.add_argument('-v', '--verbose', action='store_true', help='be verbose')
    args = parser.parse_args()
    if args.verbose: print('verbose')
    if args.suppressSSLwarning: logging.captureWarnings(True)
    riq_key = os.getenv('RelateIQAPIKey')
    if None == riq_key:
        print('please set RelateIQAPIKey environment variable')
        sys.exit(1)
    riq_secret = os.getenv('RelateIQAPISecret')
    if None == riq_secret:
        print('please set RelateIQAPISecret environment variable')
        sys.exit(1)
    print('         listId          listype listitle')
    for object in get_lists(riq_key, riq_secret, verbose=args.verbose):
        print(' {}'.format('#'.join(get_static_schema(object, verbose=args.verbose))))
        #print('{}:{}:{}'.format(get_static_schema(object, verbose=args.verbose)))
        dynamic_schema = []
        for (field_id, field_name, field_type) in get_dynamic_schema(object, verbose=args.verbose):
            dynamic_schema.append('{}:{}:{}'.format(field_id, field_name, field_type))
        print('  {}'.format('#'.join(dynamic_schema)))
