#!/usr/bin/env python

import argparse, os, sys, requests, json, logging, pprint, re

def normalize_name(name):
# this RE is subtle - don't need to escape the - since it's last
# however do need to escape the '
    name = re.sub('[():?/_"\'-]', ' ', name)
    name = '_'.join(name.split())
    return(name.lower())

def get_static_schema(object, verbose=0):
    if verbose > 1:
        for key in object.keys():
            print('key:{} type(object[key]):{}'.format(key, type(object[key])))
            if list != type(object[key]):
                print('{}-{}'.format(key,object[key]))
    return(object['id'],object['listType'],object['title'])

def get_dynamic_schema(object, verbose=0):
    columns = []
    if verbose > 1:
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
        columns.append((field['id'], field['name'], field['dataType']))
    return(columns)

def make_riq_schema_to_postgres_schema():
    return({
        'Numeric': 'bigint',
        'DateTime': 'timestamp',
        'Date': 'date',
        'Text': 'text',
        'Url': 'text',
        'Contact': 'text', # these are links to other tables
        'User': 'text', #these are relateIQ users? owners?
        'File': 'text', #are these ever used?
        'ItemLink': 'text', #what are these?
        'List': 'text' # is this the list id itself?
        })

def get_lists(riq_key, riq_secret, verbose=0):
    url = 'https://api.salesforceiq.com/v2/lists'
    r = requests.request('GET', url, auth=(riq_key,riq_secret))
    assert(unicode == type(r.text))
    assert(200 == r.status_code)
    if verbose > 2: print(r.text)
    d = json.loads(r.text)
    assert(dict == type(d))
    assert(2 == len(d))
    assert(d['nextPage'] == None)
    assert(list == type(d['objects']))
    if verbose > 0: print('# of objects:{}'.format(len(d['objects'])))
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
    parser.add_argument('-v', '--verbose', action='count', help='be verbose')
    parser.add_argument('-d', '--ddl', help='write data definition language to this file')
    args = parser.parse_args()
    if args.verbose > 0: print('verbosity level:{}'.format(args.verbose))
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
        if args.ddl:
            ddl_data = []
            riq2pg = make_riq_schema_to_postgres_schema()
        print('{}'.format('#'.join(get_static_schema(object, verbose=args.verbose))))
        dynamic_schema = []
        for (field_id, field_name, field_type) in get_dynamic_schema(object, verbose=args.verbose):
            if args.ddl: ddl_data.append((normalize_name(field_name), field_type))
            dynamic_schema.append('{}:{}:{}'.format(field_id, field_name, field_type))
        if args.verbose > 0: print(' {}'.format('#'.join(dynamic_schema)))
        if args.ddl:
            with open(args.ddl, 'a') as f:
                f.write('CREATE TABLE {} (\n'.format(normalize_name(object['title'])))
                midamble = []
                for (column_name, column_type) in ddl_data:
                    midamble.append('    {} {}'.format(column_name, riq2pg[column_type]))
                    if args.verbose > 0: print('RIQCOLTYPE:{} SQLCOLTYPE:{}'.format(column_type, riq2pg[column_type]))
                f.write(',\n'.join(midamble))
                f.write('\n);\n\n')
    if args.ddl:
        with open(args.ddl, 'a') as f:
            f.write('CREATE TABLE table_of_tables (\n')
            f.write('    id text,\n')
            f.write('    title text,\n')
            f.write('    listType text\n')
            f.write(');\n')
