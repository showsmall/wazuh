#!/usr/bin/env python
# Copyright (C) 2023, Wazuh Inc.
#
# This program is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public
# License (version 2) as published by the FSF - Free Software
# Foundation.

import json
import os
import sys
import time

try:
    import requests
    from requests.auth import HTTPBasicAuth
except Exception as e:
    print("No module 'requests' found. Install: pip install requests")
    sys.exit(1)

# ossec.conf configuration structure
#  <integration>
#      <name>slack</name>
#      <hook_url>https://hooks.slack.com/services/XXXXXXXXXXXXXX</hook_url>
#      <alert_format>json</alert_format>
#      <options>JSON_OBJ</options>
#  </integration>

# Global vars
debug_enabled   = False
debug_console   = True
pwd             = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
json_alert      = {}
json_options    = {}
now             = time.strftime("%a %b %d %H:%M:%S %Z %Y")

# Log path
LOG_FILE        = f'{pwd}/logs/integrations.log'

# Constants
ALERT_INDEX     = 1
WEBHOOK_INDEX   = 3


def main(args: list[str]):
    global debug_enabled
    try:
        # Read arguments
        bad_arguments: bool = False
        if len(args) >= 4:
            msg = '{0} {1} {2} {3} {4} {5}'.format(
                now,
                args[1],
                args[2],
                args[3],
                args[4] if len(args) > 4 else '',
                args[5] if len(args) > 5 else ''
            )
            debug_enabled = (len(args) > 4 and args[4] == 'debug')
        else:
            msg = '{0} Wrong arguments'.format(now)
            bad_arguments = True

        # Logging the call
        with open(LOG_FILE, "a") as f:
            f.write(msg + '\n')

        if bad_arguments:
            debug("# Exiting: Bad arguments. Inputted: %s" % args)
            sys.exit(2)
        
        # Core function
        process_args(args)

    except Exception as e:
        debug(str(e))
        raise 
    
def process_args(args: list[str]) -> None:
    """ 
        This is the core function, creates a message with all valid fields 
        and overwrite or add with the optional fields
        
        Parameters
        ----------
        args : list[str]
            The argument list from main call
    """
    debug("# Starting")
    
    # Read args
    alert_file_location:str     = args[ALERT_INDEX]
    webhook:str                 = args[WEBHOOK_INDEX]
    options_file_location:str   = ''
    
    # Look for options file location
    for idx in range(4,len(args)):
        if(args[idx][-7:] == "options"):
            options_file_location = args[idx]
            break

    debug("# Options file location")
    debug(options_file_location)
    
    # Load options. Parse JSON object.
    json_options = get_json_options(options_file_location)
        
    debug("# Processing options")
    debug(json_options)
    
    debug("# Alert file location")
    debug(alert_file_location)  

    # Load alert. Parse JSON object.            
    json_alert = get_json_alert(alert_file_location)

    debug("# Processing alert")
    debug(json_alert)

    debug("# Generating message")
    msg: any = generate_msg(json_alert, json_options)
    
    if not len(msg):
        debug("# ERR - Empty message")
        raise Exception
    debug(msg)

    debug("# Sending message")
    send_msg(msg, webhook)

def debug(msg: str) -> None:
    """ 
        Log the message in the log file with the timestamp, if debug flag
        is enabled
        
        Parameters
        ----------
        msg : str
            The message to be logged.
    """
    if debug_enabled:
        msg = "{0}: {1}\n".format(now, msg)
        print(msg)
        with open(LOG_FILE, "a") as f:
            f.write(msg)
    if debug_console:
        msg = "{0}: {1}\n".format(now, msg)
        print(msg)


def generate_msg(alert: any, options: any) -> any:
    """ 
        Generate the JSON object with the message to be send

        Parameters
        ----------
        alert : any
            JSON alert object.
        options: any
            JSON options object.

        Returns
        -------
        msg: str
            The JSON message to send
    """
    level           = alert['rule']['level']

    if (level <= 4):
        color = "good"
    elif (level >= 5 and level <= 7):
        color = "warning"
    else:
        color = "danger"
        
    msg             = {}
    msg['color']    = color
    msg['pretext']  = "WAZUH Alert"
    msg['title']    = alert['rule']['description'] if 'description' in alert['rule'] else "N/A"
    msg['text']     = alert.get('full_log')

    msg['fields']   = []
    if 'agent' in alert:
        msg['fields'].append({
            "title": "Agent",
            "value": "({0}) - {1}".format(
                alert['agent']['id'],
                alert['agent']['name']
            ),
        })
    if 'agentless' in alert:
        msg['fields'].append({
            "title": "Agentless Host",
            "value": alert['agentless']['host'],
        })
    msg['fields'].append({"title": "Location", "value": alert['location']})
    msg['fields'].append({
        "title": "Rule ID",
        "value": "{0} _(Level {1})_".format(alert['rule']['id'], level),
    })

    msg['ts']       = alert['id']

    if(options):
        msg.update(options)

    attach = {'attachments': [msg]}

    return json.dumps(attach)

def send_msg(msg: str, url: str) -> None:
    """ 
        Send the message to the API

        Parameters
        ----------
        msg : str
            JSON message.
        url: str
            URL of the API.
    """
    debug("# In send msg")
    headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}
    res = requests.post(url, data=msg, headers=headers)
    debug("# After send msg: %s" % res)
    
def get_json_alert(alert_file_location: str) -> any:
    """ 
        Read the JSON object from alert file

        Parameters
        ----------
        alert_file_location : str
            Path to file alert location.
            
        Returns
        -------
        {}: any
            The JSON object read it.
        
        Raises
        ------
        FileNotFoundError
            If no alert file is not present.
        JSONDecodeError
            If no valid JSON file are used
    """
    try:
        with open(alert_file_location) as alert_file:
            return json.load(alert_file)
    except FileNotFoundError:
        debug("# Alert file %s doesn't exist" % alert_file_location)
        sys.exit(3)
    except json.decoder.JSONDecodeError as e:
        debug("Failed getting json_alert %s" % e)
        sys.exit(4)
        
def get_json_options(options_file_location: str) -> any:
    """ 
        Read the JSON object from options file

        Parameters
        ----------
        options_file_location : str
            Path to file options location.
            
        Returns
        -------
        {}: any
            The JSON object read it.
        
        Raises
        ------
        FileNotFoundError
            If no optional file is not present.
        JSONDecodeError
            If no valid JSON file are used
    """
    try:
        with open(options_file_location) as options_file:
            return json.load(options_file)
    except FileNotFoundError:
        debug("# Option file %s doesn't exist" % options_file_location)
        sys.exit(3)
    except json.decoder.JSONDecodeError as e:
        debug("Failed getting json_alert %s" % e)
        sys.exit(4)

if __name__ == "__main__":
    main(sys.argv)