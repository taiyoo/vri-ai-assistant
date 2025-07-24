import boto3
import json
from decimal import Decimal

def convert_floats(obj):
    if isinstance(obj, float):
        return Decimal(str(obj))
    if isinstance(obj, dict):
        return {k: convert_floats(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [convert_floats(i) for i in obj]
    return obj

dynamodb = boto3.resource('dynamodb', region_name='ap-southeast-2')
table = dynamodb.Table('alzheimer_dataset')

with open('alzheimer_dataset_with_names.json') as f:
    for i, line in enumerate(f):
        if i >= 1000:
            break
        item = json.loads(line)
        filtered = {k: v for k, v in item.items() if not isinstance(v, float)}
        filtered = convert_floats(filtered)
        table.put_item(Item=filtered)