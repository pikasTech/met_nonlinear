import json
import datetime


def dumps(obj):
    def serialize(obj, key=None):
        if isinstance(obj, dict):
            items = []
            for k, v in obj.items():
                items.append('"%s": %s' % (k, serialize(v, key=k)))
            return '{%s}' % ', '.join(items)
        elif isinstance(obj, list):
            items = [serialize(item, key=key) for item in obj]
            return '[%s]' % ', '.join(items)
        elif isinstance(obj, float):
            if key in ('timestamp', 'timestamps'):
                # Format timestamp as number in 'YYYYMMDDHHMMSS.F' format
                formatted_timestamp = format_timestamp_number(obj)
                return formatted_timestamp  # Number as string, without quotes
            else:
                # Check if the value is NaN
                if str(obj).lower() == 'nan':
                    return 'nan'  # Return 'nan' string directly
                # Format float in scientific notation with four decimal places
                formatted_float = format_float(obj)
                return formatted_float  # Number as string, without quotes
        elif isinstance(obj, int):
            return str(obj)
        elif obj is True:
            return 'true'
        elif obj is False:
            return 'false'
        elif obj is None:
            return 'null'
        else:
            # Strings need to be properly escaped
            return json.dumps(obj)
    return serialize(obj)


def format_float(value):
    # Format float in scientific notation with four decimal places
    formatted_float = "{0:.4e}".format(value)
    # Remove any leading '+' in the exponent
    formatted_float = formatted_float.replace('+', '')
    return formatted_float


def format_timestamp_number(value):
    # Convert timestamp float to datetime
    dt = datetime.datetime.fromtimestamp(value)
    # Format as 'YYYYMMDDHHMMSS.F' with one decimal place
    formatted_timestamp = dt.strftime('%Y%m%d%H%M%S.%f')[
        :-5]  # Keep one decimal place
    return formatted_timestamp  # Return as number string, without quotes


def loads(s):
    # 预处理 JSON 字符串，处理 nan 和时间戳格式
    def preprocess_json_string(s):
        import re
        # 替换独立的 nan 为 "nan" 字符串
        s = re.sub(r':\s*nan\s*([,}])', r': "nan"\1', s)
        # 替换数值形式的时间戳为字符串
        s = re.sub(r'("timestamp"\s*:\s*)(\d{14}\.\d+)', r'\1"\2"', s)
        return s

    # 预处理 JSON 字符串
    s = preprocess_json_string(s)
    # Load JSON data, keeping numbers as strings to control parsing
    data = json.loads(s, parse_float=str, parse_int=str)

    def parse(obj, key=None):
        if isinstance(obj, dict):
            parsed = {}
            for k, v in obj.items():
                parsed[k] = parse(v, key=k)
            return parsed
        elif isinstance(obj, list):
            return [parse(item, key=key) for item in obj]
        elif isinstance(obj, str):
            if key in ('timestamp', 'timestamps'):
                # Parse timestamp number string back into float timestamp
                timestamp_float = parse_timestamp_number(obj)
                return timestamp_float
            elif key in ('epoch', 'epochs'):
                # Try to parse as integer
                try:
                    value = int(float(obj))
                    return value
                except ValueError:
                    return obj
            else:
                # Check if the value is 'nan' string
                if obj.lower() == 'nan':
                    return float('nan')
                # Try to parse as float
                try:
                    value = float(obj)
                    return value
                except ValueError:
                    return obj  # Return as is if not a float
        else:
            return obj
    return parse(data)


def parse_timestamp_number(s):
    # s is a string like '20241203113130.2'
    try:
        # Pad the fractional part to six digits
        if '.' in s:
            integer_part, fractional_part = s.split('.')
            fractional_part = (fractional_part + '000000')[:6]
        else:
            integer_part = s
            fractional_part = '000000'
        timestamp_str = integer_part + fractional_part
        dt = datetime.datetime.strptime(timestamp_str, '%Y%m%d%H%M%S%f')
        timestamp = dt.timestamp()
        return timestamp
    except ValueError:
        # Fallback: Try to parse as a float
        return float(s)


def load(fp):
    return loads(fp.read())


def dump(obj, fp):
    fp.write(dumps(obj))


if __name__ == "__main__":
    # Test data with 'timestamps' as a list
    test_data = {
        'timestamps': [1733256810.2, 1733256810.1],  # List of timestamps
        'value': 0.005723,
        'measurements': [13.2513, 1.2345, 0.1342],
        'note': 'Test data'
    }

    # Expected formatted timestamps
    expected_formatted_timestamps = []
    for ts in test_data['timestamps']:
        dt = datetime.datetime.fromtimestamp(ts)
        formatted_ts = dt.strftime('%Y%m%d%H%M%S.%f')[
            :-5]  # Keep one decimal place
        expected_formatted_timestamps.append(formatted_ts)

    # Expected output string (after serialization)
    expected_json = (
        '{'
        '"timestamps": ['
        f'{expected_formatted_timestamps[0]}, {expected_formatted_timestamps[1]}'
        '], '
        f'"value": {format_float(test_data["value"])}, '
        '"measurements": ['
        f'{format_float(test_data["measurements"][0])}, '
        f'{format_float(test_data["measurements"][1])}, '
        f'{format_float(test_data["measurements"][2])}'
        '], '
        f'"note": {json.dumps(test_data["note"])}'
        '}'
    )

    # Serialize using myjson
    json_str = dumps(test_data)
    print(json_str)
