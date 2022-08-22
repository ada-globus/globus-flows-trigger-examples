#!/usr/bin/env python

import os
import argparse

# This could go into a different file and be invoked without the file watcher
from globus_automate_client import create_flows_client

def run_flow(event_file):
    
    fc = create_flows_client()

    # TODO: Specify the flow to run when tiggered
    flow_id = 'REPLACE_WITH_FLOW_ID'
    flow_scope = fc.get_flow(flow_id).data['globus_auth_scope']

    # TODO: Modify source collection ID
    # Source collection must be on the endpoint where this trigger code is running
    source_id = 'REPLACE_WITH_SOURCE_COLLECTION_ID'
   
    # TODO: Modify destination collection ID
    # Default is to use a GCP collection on the funcX endpoint
    destination_id = 'REPLACE_WITH_DESTINATION_COLLECTION_ID'
    
    # TODO: Modify destination collection path
    destination_base_path = '/home/devN/scratch/'

    # Get the directory where the triggering file is stored and 
    # add trailing '/' to satisfy Transfer requirements for moving a directory
    event_folder = os.path.dirname(event_file)
    source_path = os.path.join(event_folder, "") 

    # TODO: Modify funcX registered function ID
    funcx_function_id = 'REPLACE_WITH_REGISTERED_FUNCTION_ID'

    # TODO: Modify funcX endpoint ID
    funcx_endpoint_id = 'REPLACE_WITH_FUNCX_ENDPOINT_ID'
   
    # TODO: Set a label for the flow run
    # Default includes the file name that triggered the run
    flow_label = f"Transfer and Compute trigger: {os.path.basename(event_file)}"

    # Get name of monitored folder to use as destination path
    # and for setting permissions
    event_folder_name = os.path.basename(event_folder)

    # Add a trailing '/' to meet Transfer requirements for directory transfer
    destination_path = os.path.join(destination_base_path, event_folder_name, "")

    # Inputs to the flow
    flow_input = {
        "input" : {
            "source": {
              "id": source_id,
              "path": source_path,
            },
            "destination": {
                "id": destination_id,
                "path": destination_path,
             },
            "recursive_tx": True,
            "funcx_function_id": funcx_function_id,
            "funcx_endpoint_id": funcx_endpoint_id,
            "funcx_function_payload": {
                "input_path": destination_path,
                "result_path": f"{destination_path}results"
            }
        }
    }
    print(flow_input)

    flow_run_request = fc.run_flow(
        flow_id=flow_id,
        flow_scope=flow_scope,
        flow_input=flow_input,
        label=flow_label,
        tags=['Trigger_Tutorial']
    )
    print(f"Transferring and Computing: {source_path}")
    print(f"https://app.globus.org/runs/{flow_run_request['run_id']}")


# Parse input arguments
def parse_args():
    parser = argparse.ArgumentParser(description='''
        Ru  a compute job/task using funcX''')
    parser.add_argument('--watchdir',
        type=str,
        default=os.path.abspath('.'),
        help=f'Directory path to watch. [default: current directory]')
    parser.add_argument('--patterns',
        type=str,
        default='',
        nargs='*', 
        help='Filename suffix pattern(s) that will trigger the flow. [default: ""]')
    parser.set_defaults(verbose=True)
    
    return parser.parse_args()


if __name__ == '__main__':

    args = parse_args()
    
    # Creates and starts the watcher
    from watch import FileTrigger
    trigger = FileTrigger(
        watch_dir=os.path.expanduser(args.watchdir),
        patterns=args.patterns,
        FlowRunner=run_flow
    )
    trigger.run()
