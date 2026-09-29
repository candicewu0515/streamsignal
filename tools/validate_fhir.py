"""Validate an exported bundle against a locally downloaded official R4 JSON schema.
Usage: python validate_fhir.py bundle.json fhir.schema.json
Install optional validator: pip install jsonschema==4.26.0
Schema: https://hl7.org/fhir/R4/downloads.html (JSON Schema).
This checks structure, not all FHIR invariants, terminology or local profiles.
"""
import json,sys
from jsonschema import Draft6Validator
bundle=json.load(open(sys.argv[1],encoding='utf-8'))
schema=json.load(open(sys.argv[2],encoding='utf-8'))
errors=list(Draft6Validator(schema).iter_errors(bundle))
for error in errors:print(error.message)
print(f'FHIR R4 JSON schema errors: {len(errors)}')
raise SystemExit(bool(errors))
