import os
import re
import sys
import traceback

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Intentionally use unresolvable hostnames to trigger the DNS pre-check
TEST_URI = "mongodb://user:pass@mongodb1:27017,mongodb2:27017,arbiter:27017/histo?replicaSet=rs"

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
    print('Unexpected: connection succeeded')
    print('Servers in topology:', client.nodes)
except Exception as e:
    print('Expected failure:')
    print(str(e))
    print('\nMasked traceback tail for brevity:')
    tb = traceback.format_exc().splitlines()
    for line in tb[-10:]:
        print(line)
