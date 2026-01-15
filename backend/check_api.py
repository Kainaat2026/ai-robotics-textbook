"""Check what routes are actually served by the running server."""
import requests
import json

response = requests.get('http://localhost:8000/openapi.json')
data = response.json()

paths = data.get('paths', {})
print(f"Total endpoints: {len(paths)}\n")

for path in sorted(paths.keys()):
    for method in paths[path].keys():
        print(f"  {method.upper():8} {path}")
