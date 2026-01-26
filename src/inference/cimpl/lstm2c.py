import json
logger = logging.getLogger(__name__)
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

def process_1d_array(weights, array_name, rows):
    """处理一维数组"""
import logging
    c_array = f'const port_float {array_name}[{rows}] = {{\n'
    for i in range(rows):
        c_array += '    {:.8f}'.format(weights[i]) + 'f'
        if i != rows - 1:
            c_array += ','
        else:
            c_array += '\n'
    c_array += '};\n\n'
    return c_array

def process_2d_array(weights, array_name, rows, cols):
    """处理二维数组"""
    c_array = f'const port_float {array_name}[{rows}][{cols}] = {{\n'
    for i in range(rows):
        c_array += '    {'
        for j in range(cols):
            c_array += '{:.8f}'.format(weights[i][j]) + 'f'
            if j != cols - 1:
                c_array += ', '
        c_array += '}'
        if i != rows - 1:
            c_array += ',\n'
        else:
            c_array += '\n'
    c_array += '};\n\n'
    return c_array

def json_to_c_array(json_data):
    c_code = ''
    for item in json_data:
        name = item['name']
        weights = item['value']
        shape = item['shape']
        rows = shape[0]
        cols = shape[1] if len(shape) > 1 else 1
        array_name = name.split(':')[0].replace('/', '_')
        if len(shape) == 1:
            c_array = process_1d_array(weights, array_name, rows)
        else:
            c_array = process_2d_array(weights, array_name, rows, cols)
        c_code += c_array
    '\n    add include and ifndef\n    '
    c_code = '#ifndef LSTM_TEST_H\n#define LSTM_TEST_H\n\n#include "port.h"\n\n' + c_code + '#endif\n'
    return c_code
if __name__ == '__main__':
    with open('projects/LSTMu24/data/best_val.weights.json', 'r') as f:
        json_data = json.load(f)
    c_array = json_to_c_array(json_data)
    with open('cimpl/lstm_test.h', 'w') as f:
        f.write(c_array)