import json

# projects\LSTMu22_6\data\training_log.json

def slice_log(log_path, slice_path, start, end):
    with open(log_path, 'r') as f:
        log_dict = json.load(f)
    for key in log_dict:
        log_dict[key] = log_dict[key][start:end]
    with open(slice_path, 'w') as f:
        json.dump(log_dict, f)

slice_log('projects/LSTMu22_6/data/training_log.json', 'projects/LSTMu22_6/data/training_log_slice.json', 0, 30000)
