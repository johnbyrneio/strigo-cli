#!/usr/bin/env python3

import argparse
import json
import os
import pprint
import requests
import sys

API_BASE_URL = "https://app.strigo.io/api/v1/"

def load_token():
    loadSuccessful = True

    if os.environ.get('STRIGO_ORG_ID'):
        org_id = os.environ.get('STRIGO_ORG_ID')
    else:
        print("ERROR: Environment Variable 'STRIGO_ORG_ID' not set.")
        loadSuccessful = False
    
    if os.environ.get('STRIGO_API_KEY'):
        api_key = os.environ.get('STRIGO_API_KEY')
    else:
        print("ERROR: Environment Variable 'STRIGO_API_KEY' not set.")
        loadSuccessful = False

    if loadSuccessful:
        bearer_token = org_id + ":" + api_key
        return bearer_token
    else:
        sys.exit(1)

def create_event(args, auth_header):
    api_endpoint = API_BASE_URL + 'events'

    event_config = {
        "name": args.name,
        "owner": args.owner,
        "class_id": args.classid,
        "description": args.description,
        "date_start": args.start,
        "date_end": args.end,
        "include_chat": args.chat,
        "include_video": args.video,
        "use_new_console": args.newconsole,
        "tas": args.ta,
    }

    if args.studentfile:
        with open(args.studentfile) as f:
            event_config['trainees'] = f.read().splitlines()

    r = requests.post(api_endpoint, headers=auth_header, json=event_config)
    check_request_error(r)
    response = r.json()

    print("%s: %s" % (response['data']['name'], response['data']['event_link']))

    if response['data']['availability'] == 'public':
        print("Token: %s" % response['data']['token'])

def modify_event(args, auth_header):
    api_endpoint = API_BASE_URL + 'events' + '/' + args.event_id

    event_config = {}

    if args.studentfile:
        with open(args.studentfile) as f:
            event_config['trainees'] = f.read().splitlines()

    r = requests.patch(api_endpoint, headers=auth_header, json=event_config)
    check_request_error(r)

def list_events(args, auth_header):
    api_endpoint = API_BASE_URL + 'events'
    r = requests.get(api_endpoint, headers=auth_header)
    check_request_error(r)
    event_list = r.json()['data']

    print('')
    print('{:<80s}{:<30s}{:<30s}'.format("Event Name", "Event ID", "Status"))
    print('-' * 100)

    if args.all:
        for event in event_list:
            print('{:<80s}{:<30s}{:<30s}'.format(event['name'], event['id'], event['status']))
    else:
        for event in event_list:

            if event['status'] == 'ready' or event['status'] == 'live':
                print('{:<80s}{:<30s}{:<30s}'.format(event['name'], event['id'], event['status']))

def get_event(args, auth_header):
    api_endpoint = API_BASE_URL + 'events' + '/' + args.event_id
    r = requests.get(api_endpoint, headers=auth_header)
    check_request_error(r)
    event = r.json()['data']
    class_api_endpoint = API_BASE_URL + 'classes' '/' + event['class_id']
    class_lookup = requests.get(class_api_endpoint, headers=auth_header)
    class_name = class_lookup.json()['data']['name']

    token = ""
    if event['availability'] == 'public':
        token = event['token']
    else:
        token = "n/a"

    ta_emails = lookup_member_emails(event['tas'], auth_header)

    print("Name:      %s" % event['name'])
    print("ID:        %s" % event['id'])
    print("Link:      %s" % event['event_link'])
    print("Owner:     %s" % event['owner']['email'])
    print("Pub/Pri:   %s" % event['availability'])
    print("Token:     %s" % token)
    print("Class:     %s (%s)" % (class_name, event['class_id']))
    print("Start:     %s" % event['date_start'])
    print("End:       %s" % event['date_end'])
    print("Status:    %s" % event['status'])
    print("TAs:       %s" % ', '.join(ta_emails))

    print("")
    print("Students:")
    print("---------")
    for trainee in event['trainees']:
        print(trainee)

def lookup_member_emails(member_ids, auth_header):
    api_endpoint = API_BASE_URL + 'members'
    r = requests.get(api_endpoint, headers=auth_header)
    check_request_error(r)
    members = r.json()['data']
    member_emails = []

    for member in members:
        if member['id'] in member_ids:
            member_emails.append(member['email'])
    
    return member_emails

def delete_event(args, auth_header):
    api_endpoint = API_BASE_URL + 'events' + '/' + args.event_id
    r = requests.delete(api_endpoint, headers=auth_header)
    check_request_error(r)

def enroll(args, auth_header):
    api_endpoint = API_BASE_URL + 'ondemand' + '/' + args.classid + '/' +'enrollments'

    if not (args.email or args.studentfile):
        print("Error: must provicde --email and/or --studentfile")
        sys.exit(1)

    enroll_list = []

    if args.email:
        enroll_list.extend(args.email)

    if args.studentfile:
        with open(args.studentfile) as f:
            enroll_list += f.read().splitlines()

    for email in enroll_list:

        email_json = {"email": email}

        r = requests.post(api_endpoint, headers=auth_header, json=email_json)
        check_request_error(r)
        response = r.json()

        print("%s: %s" % (response['data']['email'], response['data']['status']))

def list_classes(args, auth_header):
    api_endpoint = API_BASE_URL + 'classes'
    r = requests.get(api_endpoint, headers=auth_header)
    check_request_error(r)
    class_list = r.json()['data']

    print('')
    print('{:<40s}{:<0s}'.format("Class Name", "Class ID"))
    print('-' * 60)

    for classroom in class_list:
        print('{:<40s}{:<4s}'.format(classroom['name'], classroom['id']))

def get_class(args, auth_header):
    api_endpoint = API_BASE_URL + 'classes' + '/' + args.class_id

    r = requests.get(api_endpoint, headers=auth_header)

    check_request_error(r)

    classroom = r.json()['data']

    print("Name:      %s" % classroom['name'])
    print("ID:        %s" % classroom['id'])
    print("Owner:     %s" % classroom['owner']['email'])
    print("Lab Instance:")
    
    for resource in classroom['resources']:
        print("    Name: %s" % resource['name'])
        print("    Type: %s" % resource['instance_type'])
        print("    AMI: %s" % resource['image_id'])
        print("    User: %s" % resource['image_user'])

def check_request_error(response):
    if response.json()['result'] == 'failure':
        print(response.text)
        sys.exit(1)

def main():
    bearer_token = load_token()
    auth_header  = {"Authorization":"Bearer %s" %(bearer_token)}
    
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    parser_create_event = subparsers.add_parser('create-event')
    parser_create_event.add_argument('-n', '--name', required=True, help="event name")
    parser_create_event.add_argument('-o', '--owner', required=True, help="event owner's email address")
    parser_create_event.add_argument('-c', '--classid', required=True, help="ID of class to use")
    parser_create_event.add_argument('-d', '--description', required=False, help="optional event description")
    parser_create_event.add_argument('-s', '--start', required=True, help="start date/time (ex: 2019-01-28T09:00-05:00")
    parser_create_event.add_argument('-e', '--end', required=True, help="end date/time (ex: 2019-01-28T17:00-05:00)")
    parser_create_event.add_argument('--chat', action="store_true", help="enable chat")
    parser_create_event.add_argument('--video', action="store_true", help="enable video")
    parser_create_event.add_argument('--newconsole', action="store_true", help="use new console (beta)")
    parser_create_event.add_argument('-t', '--ta', action="append", help="Teaching assistant email. Can use multiple times")
    parser_create_event.add_argument('-f', '--studentfile', help="file containing student emails (one per line)")
    parser_create_event.set_defaults(func=create_event)

    parser_modify_event = subparsers.add_parser('modify-event')
    parser_modify_event.add_argument('event_id', help="event ID")
    parser_modify_event.add_argument('-f', '--studentfile', help="file containing student emails (one per line)")
    parser_modify_event.set_defaults(func=modify_event)

    parser_list_events = subparsers.add_parser('list-events')
    parser_list_events.add_argument('-a', '--all', action="store_true", help="show all events, including completed")
    parser_list_events.set_defaults(func=list_events)

    parser_get_event = subparsers.add_parser('get-event')
    parser_get_event.add_argument('event_id', help="event ID")
    parser_get_event.set_defaults(func=get_event)

    parser_delete_event = subparsers.add_parser('delete-event')
    parser_delete_event.add_argument('event_id', help="event ID")
    parser_delete_event.set_defaults(func=delete_event)

    parser_enroll = subparsers.add_parser('enroll')
    parser_enroll.add_argument('-c', '--classid', required=True, help="ID of class to use")
    parser_enroll.add_argument('-e', '--email', action="append", help="Student email address. Can use multiple times")
    parser_enroll.add_argument('-f', '--studentfile', help="file containing student emails (one per line)")
    parser_enroll.set_defaults(func=enroll)

    parser_list_classes = subparsers.add_parser('list-classes')
    parser_list_classes.set_defaults(func=list_classes)

    parser_get_class = subparsers.add_parser('get-class')
    parser_get_class.add_argument('class_id', help="class ID")
    parser_get_class.set_defaults(func=get_class)

    args = parser.parse_args()
    args.func(args, auth_header)

if __name__ == "__main__":
   main()