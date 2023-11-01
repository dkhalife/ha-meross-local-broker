from meross_iot.model.http.exception import HttpApiError

from logger import get_logger
from typing import Dict

from flask import Blueprint, request

from authentication import _user_login
from decorator import meross_http_api
from messaging import make_api_response


auth_blueprint = Blueprint('auth', __name__)
_LOGGER = get_logger(__name__)


@auth_blueprint.route('/signIn', methods=['POST'])
@meross_http_api(login_required=False)
def sign_in(api_payload: Dict, *args, **kwargs):
    email = api_payload.get("email")
    password = api_payload.get("password")
    encryption = api_payload.get("encryption", 0)

    if encryption == 1:
        providing_pre_hashed_password = True
    elif encryption == 0:
        providing_pre_hashed_password = False
    else:
        raise HttpApiError("Invalid or unsupported encryption flag. Only accepted value is 1.")
    
    if email is None:
        raise HttpApiError("Missing email parameter")
    if password is None:
        raise HttpApiError("Missing password parameter")

    user, token = _user_login(email, password, providing_pre_hashed_password)
    _LOGGER.info("User: %s successfully logged in" % email)
    data = {
        "token": str(token.token),
        "key": str(user.mqtt_key),
        "userid": str(user.user_id),
        "email": str(user.email),
        "domain": str(request.scheme + "://" + request.host),
        "mqttDomain": "",
        "mfaLockExpire": 0
    }
    return make_api_response(data=data)


@auth_blueprint.route('/Login', methods=['POST'])
@meross_http_api(login_required=False)
def login(api_payload: Dict, *args, **kwargs):
    """DEPRECATED METHOD. Left for backward compatibility"""
    email = api_payload.get("email")
    password = api_payload.get("password")
    
    if email is None:
        raise HttpApiError("Missing email parameter")
    if password is None:
        raise HttpApiError("Missing password parameter")

    user, token = _user_login(email, password, False)
    _LOGGER.info("User: %s successfully logged in" % email)
    data = {
        "token": str(token.token),
        "key": str(user.mqtt_key),
        "userid": str(user.user_id),
        "email": str(user.email)
    }
    return make_api_response(data=data)
