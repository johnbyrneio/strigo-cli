# strigo-cli
A command line interface for the Strigo (strigo.io) API 

This project is still very much in alpha. I've only tested it on Python 3.7.

## Getting Started

strigo-cli expects the following environment variables to be set:

- STRIGO_ORG_ID
- STRIGO_API_KEY

The values can be retrieved from https://app.strigo.io/settings#account.

## Usage

strigo-cli supports most of the functions currently exposed by the Strigo API, including:

- create-event
- delete-event
- list-events
- get-event
- list-classes
- get-class

### create-event
```
$ strigo-cli create-event --name "My Training Event" \
  --owner "john@johnbyrne.io" \
  --classid "xxxxxxxxxx" \
  --start 2019-01-28T09:00+01:00 \ 
  --end 2019-01-28T17:00+01:00  \
  --chat \
  --video \
  --ta "john.doe@example.com" \
  --ta "jane.doe@example.com" \
  -f student_list.txt
```

| option        | short | description                                                                      |
|---------------|-------|----------------------------------------------------------------------------------|
| --name        | -n    | Name of the event                                                                |
| --owner       | -o    | Email address of event owner                                                     |
| --classid     | -c    | Class ID (Use list-classes to get a list of IDs)                                 |
| --start       | -s    | Start time using datetime format (ex: 2019-01-28T09:00-05:00)                    |
| --end         | -e    | End time using datetime format (ex: 2019-01-28T17:00-05:00)                      |
| --chat        |       | Enable chat                                                                      |
| --video       |       | Enable video                                                                     |
| --ta          | -t    | Email address of teaching assistant. Can be used multiple times.                 |
| --studentfile | -f    | Path to file containing a list of student email addresses. One address per line. |

### delete-event
```
$ strigo-cli delete-event <event_id>
```

### list-events
```
$ strigo-cli list-events [-a]
```

| option | short | description                          |
|--------|-------|--------------------------------------|
| --all  | -a    | List all events, including completed |

### get-event
```
$ strigo-cli get-event <event_id>
```

### list-classes
```
$ strigo-cli list-classes
```

### get-class
```
$ strigo-cli get-class <class_id>

```