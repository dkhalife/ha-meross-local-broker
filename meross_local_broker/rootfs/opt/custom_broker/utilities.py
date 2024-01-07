from logger import get_logger
from hashlib import sha256, md5

_LOGGER = get_logger(__name__)

def _hash_password(salt: str, password: str, pre_apply_md5=False) -> str:
    pwd = md5(password.encode("utf8")).hexdigest() if pre_apply_md5 else password
    # Get the salt, compute the hashed password and compare it with the one stored in the db
    clearsaltedpwd = f"{salt}{pwd}"
    hashed_pass = sha256()
    hashed_pass.update(clearsaltedpwd.encode('utf8'))
    computed_hashed_password = hashed_pass.hexdigest()

    return computed_hashed_password
