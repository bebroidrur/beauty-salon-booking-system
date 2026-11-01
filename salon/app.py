"""Flask adapter for the checked-in OpenAPI contract."""
from datetime import datetime, timezone
import re
import uuid
from flask import Flask, jsonify, request, g
from jsonschema.exceptions import ValidationError
from werkzeug.exceptions import HTTPException
from salon.events import record
from salon.auth import authenticate
from salon.contract import API, resolve, validate
from salon.errors import ApiError, reject
from salon.service import Service
from salon.store import Store


def create_app(database, clock=None):
    app = Flask(__name__)
    store = Store(database)
    clock = clock or (lambda: datetime.now(timezone.utc))
    service = Service(store, clock)
    app.extensions.update(store=store, clock=clock, service=service)

    @app.before_request
    def correlation():
        g.request_id = uuid.uuid4().hex
        g.error_code = None

    @app.after_request
    def record_action(response):
        record(request.endpoint or 'unmatched', response.status_code, g.request_id, g.error_code)
        return response

    @app.errorhandler(ApiError)
    def api_error(exc):
        g.error_code = exc.code
        return jsonify(code=exc.code,message=exc.message),exc.status

    @app.errorhandler(HTTPException)
    def http_error(exc):
        return jsonify(code='INVALID_REQUEST',message='Некоректний запит.'),exc.code

    @app.errorhandler(Exception)
    def unexpected_error(exc):
        g.error_code = "INTERNAL_ERROR"
        return jsonify(code='INTERNAL_ERROR',message='Не вдалося обробити запит.'),500

    def handler(operation):
        def route(**params):
            with store.transaction() as db:
                user = None
                if operation['security']:
                    user=authenticate(db,request.headers.get('Authorization',''))
                    if user['role'] not in operation['x-roles']:
                        reject(403,'FORBIDDEN','Операція недоступна для цього користувача.')
                data={}
                if 'requestBody' in operation:
                    if not request.is_json:
                        reject(400,'INVALID_REQUEST','Потрібен JSON.')
                    data=request.get_json()
                try:
                    if 'requestBody' in operation:
                        validate(operation['requestBody']['content']['application/json']['schema'],data)
                    for parameter in operation.get('parameters',[]):
                        name=parameter['name']
                        value=params.get(name) if parameter['in']=='path' else request.args.get(name)
                        if value is None and parameter.get('required'):
                            reject(422 if '422' in operation['responses'] else 400)
                        if value is not None:
                            validate(parameter['schema'],value)
                            params[name]=value
                except ValidationError:
                    reject(422 if '422' in operation['responses'] else 400)
                value=service.execute(db,operation['operationId'],data,params,user)
                status=next(int(s) for s in operation['responses'] if s.startswith('2'))
                if status==204:
                    return '',204
                response=resolve(operation['responses'][str(status)])
                validate(response['content']['application/json']['schema'],value)
                return jsonify(value),status
        return route

    for path, methods in API['paths'].items():
        for method, op in methods.items():
            if op['operationId'] in ('listSlots',):
                continue
            app.add_url_rule(re.sub(r'{(\w+)}',r'<\1>',path),op['operationId'],handler(op),methods=[method.upper()])
    return app
