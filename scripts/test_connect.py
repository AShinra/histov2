import os
import re
import sys
import traceback

# Ensure the repository root is on sys.path so we can import local modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Use a test URI — replace with your actual one if you want to test your environment
# NOTE: This file intentionally masks printed URIs to avoid leaking credentials in logs.
TEST_URI = "mongodb://admin:q8vm5dz-h29piX%3FMo%26%3ClO4e0zn@mongodb4:27017,arbiter:27017/zeno_db?authSource=admin&replicaSet=rs1"

os.environ['MONGO_URI'] = TEST_URI

from common import connect_to_mongodb


def _mask_uri(uri):
    try:
        return re.sub(r'://([^:@]+):([^@]+)@', '://<user>:<redacted>@', uri)
    except Exception:
        return '<redacted>'

print('Attempting to connect to MongoDB using env MONGO_URI (masked):', _mask_uri(os.environ.get('MONGO_URI')))

try:
    client = connect_to_mongodb()
    # If we get here, ping succeeded in connect_to_mongodb()
    print('Connection successful: ping OK')
    # Show server info summary
    print('Servers in topology:', client.nodes)
except Exception as e:
    print('Connection failed:')
    print(e)
    print('\nTraceback (masked):')
    tb = traceback.format_exc()
    print(tb.split('\n')[-1])
