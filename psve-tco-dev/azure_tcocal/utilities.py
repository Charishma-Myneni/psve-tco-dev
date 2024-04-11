
import json

def load_json_data(path):
    f = open(path)
    data = json.load(f)
    f.close()
    return data