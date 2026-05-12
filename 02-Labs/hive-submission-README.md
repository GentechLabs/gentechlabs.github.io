# generate_openapi.py

A CLI tool that scans a Flask application directory and generates an OpenAPI 3.0 YAML specification — using AST parsing only (no runtime Flask execution).

## Features

- **Static Analysis**: Uses Python's `ast` module to parse source files without importing or executing Flask code
- **Route Extraction**: Detects `@app.route`, `@blueprint.route`, and `@bp.get/post/put/delete` decorators
- **Method Detection**: Automatically extracts HTTP methods from `methods=['GET', 'POST']` arguments
- **Docstring Parsing**: Uses function docstrings for operation summaries and descriptions
- **Reqparse Detection**: Identifies Flask-RESTful `parser.add_argument()` calls for request body/query parameter schemas
- **Path Parameters**: Converts Flask route variables (e.g., `<int:id>`) to OpenAPI path parameters
- **Response Inference**: Detects `abort()` calls and tuple returns to infer response status codes
- **Clean YAML Output**: Produces properly formatted YAML with multi-line string support

## Requirements

- Python 3.7+
- PyYAML

## Installation

```bash
pip install pyyaml
```

## Usage

### Basic Usage

```bash
python generate_openapi.py /path/to/your/flask/app
```

This scans all `.py` files in the directory and generates `openapi.yaml` in the current directory.

### Options

```
usage: generate_openapi.py [-h] [--output OUTPUT] [--title TITLE]
                           [--description DESCRIPTION] [--version VERSION]
                           [--verbose]
                           app_dir

positional arguments:
  app_dir               Path to the Flask application directory to scan

options:
  --output, -o OUTPUT   Output file path (default: openapi.yaml)
  --title TITLE         API title for the OpenAPI spec (default: Flask API)
  --description DESCRIPTION
                        API description for the OpenAPI spec
  --version VERSION     API version (default: 1.0.0)
  --verbose, -v         Print detailed information about extracted routes
```

### Examples

```bash
# Basic scan
python generate_openapi.py ./my_flask_app

# Custom output file and metadata
python generate_openapi.py ./my_flask_app \
    --output api-spec.yaml \
    --title "User Management API" \
    --description "REST API for managing users" \
    --version "2.0.0"

# Verbose mode to see what was extracted
python generate_openapi.py ./my_flask_app --verbose
```

## Supported Patterns

### Route Decorators

```python
@app.route('/users')
@app.route('/users', methods=['GET', 'POST'])
@blueprint.route('/items/<int:item_id>')
@bp.get('/search')
@bp.post('/create')
```

### Path Parameters

Flask path converters are mapped to OpenAPI types:

| Flask Converter | OpenAPI Type |
|----------------|-------------|
| `<int:id>`     | `integer`   |
| `<float:val>`  | `number`    |
| `<string:name>`| `string`    |
| `<path:p>`     | `string`    |
| `<uuid:id>`    | `string`    |
| `<id>` (no type)| `string`   |

### Docstrings

```python
@app.route('/users')
def get_users():
    """Get all users.
    
    Returns a paginated list of all users in the system.
    """
```

- First line → operation `summary`
- Remaining text → operation `description`

### Flask-RESTful Reqparse

```python
from flask_restful import reqparse

parser = reqparse.RequestParser()
parser.add_argument('name', type=str, required=True, help='User name')
parser.add_argument('age', type=int, required=False)
parser.add_argument('role', type=str, choices=['admin', 'user'])
args = parser.parse_args()
```

These are automatically detected and converted to:
- **Request body schemas** (for POST/PUT/PATCH)
- **Query parameters** (for GET/DELETE)

## Example Input

```python
# app.py
from flask import Flask, abort, jsonify

app = Flask(__name__)

@app.route('/api/users', methods=['GET', 'POST'])
def users():
    """Manage users.
    
    List all users or create a new user.
    """
    pass

@app.route('/api/users/<int:user_id>')
def get_user(user_id):
    """Get a specific user by ID."""
    pass

@app.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Delete a user."""
    pass
```

## Example Output

```yaml
openapi: '3.0.0'
info:
  title: Flask API
  description: Auto-generated OpenAPI specification
  version: '1.0.0'
paths:
  /api/users:
    get:
      summary: Manage users
      description: List all users or create a new user.
      operationId: users
      tags:
        - App
      responses:
        '200':
          description: Successful response
    post:
      summary: Manage users
      description: List all users or create a new user.
      operationId: users
      tags:
        - App
      responses:
        '200':
          description: Successful response
  /api/users/{user_id}:
    get:
      summary: Get a specific user by ID
      operationId: get_user
      tags:
        - App
      parameters:
        - name: user_id
          in: path
          required: true
          schema:
            type: integer
      responses:
        '200':
          description: Successful response
    delete:
      summary: Delete a user
      operationId: delete_user
      tags:
        - App
      parameters:
        - name: user_id
          in: path
          required: true
          schema:
            type: integer
      responses:
        '200':
          description: Successful response
```

## Limitations

- Only analyzes Python source files (`.py` extension)
- Does not follow imports or resolve cross-module references
- Reqparse detection works with direct `add_argument()` calls in function bodies
- Response inference is based on common patterns; custom error handlers are not detected
- Nested blueprints or factory patterns may not be fully resolved

## License

MIT
