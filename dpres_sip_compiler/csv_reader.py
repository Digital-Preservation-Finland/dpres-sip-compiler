"""CSV Reader for SIP Compiler
"""
import os
import csv

def read_csv(workspace, config):
    """Read CSV file
    """
    # TODO: Detailed info from CSV
    objects = set()
    events = set()
    event_rels = {}
    object_dicts = []
    event_dicts = []
    csvfile = None
    for filepath in os.listdir(workspace):
        if filepath.endswith("%s.csv" % config["script"]["meta_ending"]):
            csvfile = os.path.join(workspace, filepath)
            break
    with open(csvfile) as csvfile:
        csvreader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
        for row in csvreader:
            if row[config["object"]["sumtype"]].lower() == \
                    config["script"]["used_checksum"].lower():
                objects.add(tuple([row[config["object"][key]]
                                   for key in config["object"]]))
            events.add(tuple([row[config["event"][key]]
                              for key in config["event"]]))
            if not row[config["event"]["id"]] in event_rels:
                event_rels[row[config["event"]["id"]]] = {
                    "agents": [], "objects": [], "paths": []}
            event_rels[row[config["event"]["id"]]]["agents"].append(
                {key: row[config["agent"][key]] for key in config["agent"]})
            event_rels[row[config["event"]["id"]]]["objects"].append(
                row[config["object"]["id"]])
    for obj in objects:
        object_dicts.append(dict(zip([
            key for key in config["object"]], obj)))
    for event in events:
        event_dicts.append(dict(zip([
            key for key in config["event"]], event)))

    return (object_dicts, event_dicts, event_rels)
