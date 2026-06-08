#!/usr/bin/env python3
"""
generate_openapi.py - Scan a Flask application directory and generate an OpenAPI 3.0 YAML specification.

Uses AST parsing (no runtime Flask execution) to extract:
- @app.route / @blueprint.route decorators with HTTP methods
- Docstrings for operation summaries and descriptions
- Flask-RESTful reqparse arguments for request body schemas
- Path parameters from route paths (e.g., /users/<int:id>)

Usage:
    python generate_openapi.py /path/to/flask/app [--output openapi.yaml]
"""

import ast
import argparse
import os
import re
import sys
from collections import defaultdict

try:
    import yaml
except ImportError:
    print("Error: PyYAML is required. Install with: pip install pyyaml", file=sys.stderr)
    sys.exit(1)


# Flask type converters and their OpenAPI type mappings
FLASK_TYPE_MAP = {
    "int": "integer",
    "float": "number",
    "string": "string",
    "path": "string",
    "uuid": "string",
    "any": "string",
}


def parse_flask_route_pattern(route_pattern):
    """
    Parse a Flask route pattern and extract path parameters.
    
    e.g., '/users/<int:id>/posts/<string:slug>' 
    returns ('/users/{id}/posts/{slug}', [{'name': 'id', 'type': 'integer'}, {'name': 'slug', 'type': 'string'}])
    """
    params = []
    
    def replace_param(match):
        type_and_name = match.group(1)
        if ":" in type_and_name:
            type_name, param_name = type_and_name.split(":", 1)
        else:
            type_name = "string"
            param_name = type_and_name
        openapi_type = FLASK_TYPE_MAP.get(type_name, "string")
        params.append({"name": param_name, "type": openapi_type})
        return "{" + param_name + "}"
    
    converted = re.sub(r"<([^>]+)>", replace_param, route_pattern)
    return converted, params


def extract_reqparse_args(node):
    """
    Extract Flask-RESTful reqparse arguments from AST nodes.
    
    Looks for patterns like:
        parser.add_argument('name', type=str, required=True, help='description')
        parser.add_argument('name', type=int)
    """
    arguments = []
    
    if not isinstance(node, ast.Assign):
        return arguments
    
    # Look for assignment patterns like: args = parser.parse_args() or parser = reqparse.RequestParser()
    # We need to find reqparse usage inside function bodies
    
    return arguments


def extract_add_argument_info(call_node):
    """
    Extract argument info from a parser.add_argument() call node.
    Returns a dict or None.
    """
    if not (isinstance(call_node, ast.Call) and
            isinstance(call_node.func, ast.Attribute) and
            call_node.func.attr == "add_argument" and
            call_node.args):
        return None
    
    arg_name = None
    if isinstance(call_node.args[0], ast.Constant):
        arg_name = call_node.args[0].value
    elif isinstance(call_node.args[0], ast.Str):
        arg_name = call_node.args[0].s
    
    if arg_name is None:
        return None
    
    arg_info = {"name": arg_name, "type": "string"}
    
    type_map = {
        "str": "string", "int": "integer", "float": "number",
        "bool": "boolean", "list": "array", "dict": "object",
    }
    
    for keyword in call_node.keywords:
        if keyword.arg == "type":
            type_val = None
            if isinstance(keyword.value, ast.Attribute):
                type_val = keyword.value.attr
            elif isinstance(keyword.value, ast.Name):
                type_val = keyword.value.id
            if type_val:
                arg_info["type"] = type_map.get(type_val, "string")
        elif keyword.arg == "required":
            if isinstance(keyword.value, ast.Constant):
                arg_info["required"] = keyword.value.value
            elif isinstance(keyword.value, ast.NameConstant):
                arg_info["required"] = keyword.value.value
        elif keyword.arg == "help":
            if isinstance(keyword.value, ast.Constant):
                arg_info["description"] = keyword.value.value
            elif isinstance(keyword.value, ast.Str):
                arg_info["description"] = keyword.value.s
        elif keyword.arg == "choices":
            if isinstance(keyword.value, (ast.List, ast.Tuple)):
                choices = []
                for elt in keyword.value.elts:
                    if isinstance(elt, ast.Constant):
                        choices.append(str(elt.value))
                    elif isinstance(elt, ast.Str):
                        choices.append(elt.s)
                if choices:
                    arg_info["enum"] = choices
    
    return arg_info


def collect_module_reqparse_args(tree):
    """
    Scan module-level code for reqparse add_argument calls.
    Returns a list of argument info dicts.
    """
    arguments = []
    for node in ast.iter_child_nodes(tree):
        # Pattern: parser.add_argument('name', type=str, ...)
        # This is an expression statement, not an assignment
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
            info = extract_add_argument_info(node.value)
            if info:
                arguments.append(info)
        elif isinstance(node, ast.Assign) and isinstance(node.value, ast.Call):
            info = extract_add_argument_info(node.value)
            if info:
                arguments.append(info)
    return arguments


def scan_for_reqparse_in_function(func_node, module_args=None):
    """
    Scan a function's body for reqparse argument additions.
    
    Checks both inline add_argument calls and module-level parsers
    if the function calls parse_args().
    
    Returns a list of dicts with argument info.
    """
    arguments = []
    has_parse_args = False
    
    for node in ast.walk(func_node):
        # Pattern: parser.add_argument('name', type=str, ...)
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Attribute):
                if func.attr == "add_argument":
                    info = extract_add_argument_info(node)
                    if info:
                        arguments.append(info)
                elif func.attr == "parse_args":
                    has_parse_args = True
    
    # If the function calls parse_args() but has no inline add_argument,
    # fall back to module-level reqparse args
    if has_parse_args and not arguments and module_args:
        arguments = list(module_args)
    
    return arguments


def parse_docstring(docstring):
    """
    Parse a docstring to extract summary and description.
    
    Convention:
    - First non-empty line is the summary
    - Everything after is the description
    """
    if not docstring:
        return None, None
    
    lines = docstring.strip().split("\n")
    summary = lines[0].strip() if lines else None
    
    description = None
    if len(lines) > 1:
        desc_lines = [l.strip() for l in lines[1:] if l.strip()]
        description = "\n".join(desc_lines) if desc_lines else None
    
    return summary, description


def is_blueprint_variable(name):
    """Check if a variable name looks like a Flask blueprint."""
    blueprint_patterns = [
        "blueprint", "bp", "api", "ns", "namespace",
        "restful", "rest_api", "api_bp", "api_blueprint",
    ]
    name_lower = name.lower()
    return any(p in name_lower for p in blueprint_patterns)


def extract_routes_from_file(filepath):
    """
    Parse a Python file and extract Flask route information.
    
    Returns a list of route dicts.
    """
    routes = []
    
    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            source = f.read()
    except (IOError, OSError) as e:
        print(f"Warning: Could not read {filepath}: {e}", file=sys.stderr)
        return routes
    
    try:
        tree = ast.parse(source, filename=filepath)
    except SyntaxError as e:
        print(f"Warning: Could not parse {filepath}: {e}", file=sys.stderr)
        return routes
    
    # Collect module-level reqparse arguments
    module_reqparse_args = collect_module_reqparse_args(tree)
    
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        
        func = node
        if not func.decorator_list:
            continue
        
        for decorator in func.decorator_list:
            route_info = extract_route_from_decorator(decorator)
            if route_info is None:
                continue
            
            # Extract docstring
            docstring = ast.get_docstring(func)
            summary, description = parse_docstring(docstring)
            
            # Extract reqparse arguments (inline + module-level fallback)
            reqparse_args = scan_for_reqparse_in_function(func, module_reqparse_args)
            
            # Parse the route pattern
            openapi_path, path_params = parse_flask_route_pattern(route_info["path"])
            
            # Build the route entry
            entry = {
                "path": openapi_path,
                "methods": route_info["methods"],
                "summary": summary or f"{func.name.replace('_', ' ').title()}",
                "description": description,
                "path_params": path_params,
                "reqparse_args": reqparse_args,
                "function_name": func.name,
                "source_file": os.path.basename(filepath),
            }
            
            # Infer HTTP status codes from common patterns
            entry["responses"] = infer_responses(func)
            
            routes.append(entry)
    
    return routes


def extract_route_from_decorator(decorator):
    """
    Extract route info from a decorator node.
    
    Handles:
    - @app.route('/path', methods=['GET', 'POST'])
    - @app.route('/path')
    - @blueprint.route('/path')
    - @bp.get('/path')
    - @api.route('/path')
    """
    if isinstance(decorator, ast.Call):
        func = decorator.func
        
        # Check if it's a .route() call
        if isinstance(func, ast.Attribute) and func.attr in ("route",):
            route_path = None
            methods = ["GET"]
            
            # First positional arg is the path
            if decorator.args:
                if isinstance(decorator.args[0], ast.Constant):
                    route_path = decorator.args[0].value
                elif isinstance(decorator.args[0], ast.Str):
                    route_path = decorator.args[0].s
            
            if route_path is None:
                return None
            
            # Look for methods= keyword argument
            for keyword in decorator.keywords:
                if keyword.arg == "methods":
                    if isinstance(keyword.value, (ast.List, ast.Tuple)):
                        methods = []
                        for elt in keyword.value.elts:
                            if isinstance(elt, ast.Constant):
                                methods.append(elt.value.upper())
                            elif isinstance(elt, ast.Str):
                                methods.append(elt.s.upper())
            
            return {"path": route_path, "methods": methods}
        
        # Check for @bp.get('/path'), @bp.post('/path'), etc.
        if isinstance(func, ast.Attribute) and func.attr.lower() in (
            "get", "post", "put", "patch", "delete", "head", "options"
        ):
            method = func.attr.upper()
            route_path = None
            
            if decorator.args:
                if isinstance(decorator.args[0], ast.Constant):
                    route_path = decorator.args[0].value
                elif isinstance(decorator.args[0], ast.Str):
                    route_path = decorator.args[0].s
            
            if route_path is None:
                return None
            
            return {"path": route_path, "methods": [method]}
    
    return None


def infer_responses(func_node):
    """
    Infer HTTP response codes by scanning the function body for
    common patterns like abort(), jsonify(), return '', status_code.
    """
    responses = {
        "200": {"description": "Successful response"},
    }
    
    for node in ast.walk(func_node):
        # Look for abort() calls
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name) and func.id == "abort":
                if node.args and isinstance(node.args[0], (ast.Constant, ast.Num)):
                    code = node.args[0].value if isinstance(node.args[0], ast.Constant) else node.args[0].n
                    code_str = str(code)
                    if code_str not in responses:
                        descriptions = {
                            "400": "Bad request",
                            "401": "Unauthorized",
                            "403": "Forbidden",
                            "404": "Not found",
                            "500": "Internal server error",
                        }
                        responses[code_str] = {"description": descriptions.get(code_str, f"Error {code}")}
        
        # Look for return with status code pattern: return ..., status_code
        if isinstance(node, ast.Return) and node.value:
            if isinstance(node.value, ast.Tuple) and len(node.value.elts) >= 2:
                last_elt = node.value.elts[-1]
                if isinstance(last_elt, (ast.Constant, ast.Num)):
                    code = last_elt.value if isinstance(last_elt, ast.Constant) else last_elt.n
                    if isinstance(code, int) and code >= 200 and code < 600:
                        code_str = str(code)
                        if code_str not in responses:
                            responses[code_str] = {"description": f"HTTP {code} response"}
    
    return responses


def build_openapi_spec(routes, title="Flask API", description="Auto-generated OpenAPI specification"):
    """
    Build a complete OpenAPI 3.0 spec dict from extracted routes.
    """
    spec = {
        "openapi": "3.0.0",
        "info": {
            "title": title,
            "description": description,
            "version": "1.0.0",
        },
        "paths": {},
    }
    
    # Group routes by path
    path_map = defaultdict(dict)
    
    for route in routes:
        path = route["path"]
        if not path.startswith("/"):
            path = "/" + path
        
        for method in route["methods"]:
            method_lower = method.lower()
            operation = {}
            
            # Summary
            operation["summary"] = route["summary"]
            
            # Description
            if route.get("description"):
                operation["description"] = route["description"]
            
            # Operation ID
            operation["operationId"] = route["function_name"]
            
            # Tags (from source file)
            source_file = route.get("source_file", "unknown")
            tag = source_file.replace(".py", "").replace("_", " ").title()
            operation["tags"] = [tag]
            
            # Path parameters
            if route.get("path_params"):
                parameters = []
                for param in route["path_params"]:
                    parameters.append({
                        "name": param["name"],
                        "in": "path",
                        "required": True,
                        "schema": {"type": param["type"]},
                    })
                operation["parameters"] = parameters
            
            # Request body from reqparse args
            if route.get("reqparse_args") and method_lower in ("post", "put", "patch"):
                properties = {}
                required_fields = []
                for arg in route["reqparse_args"]:
                    prop = {"type": arg["type"]}
                    if "description" in arg:
                        prop["description"] = arg["description"]
                    if "enum" in arg:
                        prop["enum"] = arg["enum"]
                    properties[arg["name"]] = prop
                    if arg.get("required", False):
                        required_fields.append(arg["name"])
                
                if properties:
                    schema = {
                        "type": "object",
                        "properties": properties,
                    }
                    if required_fields:
                        schema["required"] = required_fields
                    
                    operation["requestBody"] = {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": schema,
                            }
                        }
                    }
            
            # Also add reqparse args as query parameters for GET
            if route.get("reqparse_args") and method_lower in ("get", "delete"):
                if "parameters" not in operation:
                    operation["parameters"] = []
                for arg in route["reqparse_args"]:
                    param = {
                        "name": arg["name"],
                        "in": "query",
                        "required": arg.get("required", False),
                        "schema": {"type": arg["type"]},
                    }
                    if "description" in arg:
                        param["description"] = arg["description"]
                    if "enum" in arg:
                        param["schema"]["enum"] = arg["enum"]
                    operation["parameters"].append(param)
            
            # Responses
            operation["responses"] = route.get("responses", {"200": {"description": "Successful response"}})
            
            path_map[path][method_lower] = operation
    
    # Convert to sorted paths
    for path in sorted(path_map.keys()):
        spec["paths"][path] = dict(sorted(path_map[path].items()))
    
    return spec


class OpenAPIYAMLDumper(yaml.SafeDumper):
    """Custom YAML dumper for cleaner output without anchors."""
    def ignore_aliases(self, data):
        return True


def str_representer(dumper, data):
    """Use block style for multi-line strings."""
    if "\n" in data:
        return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")
    return dumper.represent_scalar("tag:yaml.org,2002:str", data)


OpenAPIYAMLDumper.add_representer(str, str_representer)


def scan_directory(app_dir):
    """Scan a directory for Python files and extract routes from all of them."""
    all_routes = []
    
    for root, dirs, files in os.walk(app_dir):
        # Skip common non-source directories
        dirs[:] = [d for d in dirs if d not in ("venv", "env", ".env", "__pycache__", ".git", "node_modules", ".tox", ".eggs")]
        
        for filename in sorted(files):
            if not filename.endswith(".py"):
                continue
            
            filepath = os.path.join(root, filename)
            routes = extract_routes_from_file(filepath)
            all_routes.extend(routes)
    
    return all_routes


def main():
    parser = argparse.ArgumentParser(
        description="Generate OpenAPI 3.0 YAML specification from a Flask application directory.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python generate_openapi.py ./my_flask_app
  python generate_openapi.py ./my_flask_app --output api-spec.yaml
  python generate_openapi.py ./my_flask_app --title "My API" --description "My awesome API"
        """,
    )
    parser.add_argument(
        "app_dir",
        help="Path to the Flask application directory to scan",
    )
    parser.add_argument(
        "--output", "-o",
        default="openapi.yaml",
        help="Output file path (default: openapi.yaml)",
    )
    parser.add_argument(
        "--title",
        default="Flask API",
        help="API title for the OpenAPI spec (default: Flask API)",
    )
    parser.add_argument(
        "--description",
        default="Auto-generated OpenAPI specification",
        help="API description for the OpenAPI spec",
    )
    parser.add_argument(
        "--version",
        default="1.0.0",
        help="API version (default: 1.0.0)",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Print detailed information about extracted routes",
    )
    
    args = parser.parse_args()
    
    # Validate input directory
    if not os.path.isdir(args.app_dir):
        print(f"Error: '{args.app_dir}' is not a valid directory.", file=sys.stderr)
        sys.exit(1)
    
    # Scan for routes
    if args.verbose:
        print(f"Scanning {args.app_dir} for Flask routes...", file=sys.stderr)
    
    routes = scan_directory(args.app_dir)
    
    if not routes:
        print("Warning: No Flask routes found in the specified directory.", file=sys.stderr)
        print("Make sure the directory contains Python files with @app.route or @blueprint.route decorators.", file=sys.stderr)
    
    if args.verbose:
        print(f"Found {len(routes)} route(s):", file=sys.stderr)
        for route in routes:
            methods = ", ".join(route["methods"])
            print(f"  {methods:20s} {route['path']:<40s} (from {route['source_file']})", file=sys.stderr)
    
    # Build OpenAPI spec
    spec = build_openapi_spec(
        routes,
        title=args.title,
        description=args.description,
    )
    spec["info"]["version"] = args.version
    
    # Write YAML output
    try:
        with open(args.output, "w", encoding="utf-8") as f:
            yaml.dump(
                spec,
                f,
                Dumper=OpenAPIYAMLDumper,
                default_flow_style=False,
                sort_keys=False,
                allow_unicode=True,
                width=120,
            )
        print(f"OpenAPI spec written to {args.output}", file=sys.stderr)
        if args.verbose:
            print(f"Contains {len(spec['paths'])} path(s) with {sum(len(v) for v in spec['paths'].values())} operation(s)", file=sys.stderr)
    except (IOError, OSError) as e:
        print(f"Error writing output file: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
