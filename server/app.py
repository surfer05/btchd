from flask import Flask, request, jsonify
from flasgger import Swagger, swag_from
import os

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB limit, matching Express

# Configure Swagger
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'apispec',
            "route": '/apispec.json',
            "rule_filter": lambda rule: True,  # all in
            "model_filter": lambda tag: True,  # all in
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/docs"
}

swagger = Swagger(app, config=swagger_config)

@app.route('/assert', methods=['POST'])
@swag_from({
    'tags': ['Verification'],
    'summary': 'Assert verification proof',
    'description': 'Submit and verify an App Attest assertion with proof',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'keyId': {
                        'type': 'string',
                        'description': 'The key identifier'
                    },
                    'assertion': {
                        'type': 'string',
                        'description': 'The assertion data'
                    },
                    'proof': {
                        'type': 'string',
                        'description': 'The verification proof'
                    },
                    'publicInputs': {
                        'type': 'array',
                        'items': {
                            'type': 'string'
                        },
                        'description': 'Array of public inputs'
                    }
                }
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Verification successful',
            'schema': {
                'type': 'object',
                'properties': {
                    'ok': {
                        'type': 'boolean',
                        'example': True
                    }
                }
            }
        }
    }
})
def assert_route():
    # For demo: accept and log. Add real App Attest verification later.
    data = request.get_json(force=True)
    key_id = data.get('keyId')
    assertion = data.get('assertion')
    proof = data.get('proof')
    public_inputs = data.get('publicInputs')
    
    print(f"assert key: {key_id} proof bytes: {len(proof) if proof else 0} pubs: {len(public_inputs) if public_inputs else 0}")
    return jsonify({"ok": True})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=port, debug=True)
