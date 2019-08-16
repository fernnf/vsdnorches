import json


def return_msg(msg, error=False):
    pkt = [{'error': error, 'result': msg}]
    return json.dumps(pkt, indent=4, ensure_ascii=True)
