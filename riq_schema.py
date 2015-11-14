#!/usr/bin/env python

import argparse, os, sys, requests, json, logging

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
        if verbose:
            for key in object.keys():
                print('key:{} type(object[key]):{}'.format(key, type(object[key])))
                if list != type(object[key]):
                    print('{}-{}'.format(key,object[key]))
    return(['{}:{}:{}'.format(object['id'],object['listType'],object['title']) for object in d['objects']])

if '__main__' == __name__:
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--suppressSSLwarning', action='store_true', help='surpress SSL warning')
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
    for result in get_lists(riq_key, riq_secret, verbose=args.verbose):
        print(result)
