import json
import hashlib
import modules.constants as constants

from os.path import exists


def auth_list_to_dict(auth_list):
    auth_dict = {}
    for auth_data in auth_list:
        if 'user' in auth_data:
            if 'hash' in auth_data:
                auth_dict |= {auth_data['user']: auth_data['hash']}
            elif 'pass' in auth_data:
                auth_dict |= {auth_data['user']: hashlib.sha256(bytes(auth_data['pass'], encoding='utf-8')).hexdigest()}
    return auth_dict


def load_auth_data(filename=None):
    auth_dict = None
    if filename != None and exists(filename):
        with open(filename, encoding='utf-8') as auth_file:
            try:
                auth_obj = json.load(auth_file)
                if isinstance(auth_obj, list) and len(auth_obj) > 0:
                    auth_dict = auth_list_to_dict(auth_obj)
            except Exception as e:
                print('load_auth_data, e: ' + str(e))
    return auth_dict


auth_dict = load_auth_data(constants.AUTH_FILENAME)

auth_enabled = auth_dict != None


def check_auth(user, password):
    print(f"Connection attempt for {user}")
    if user not in auth_dict:
        return False
    else:
        password_correct = hashlib.sha256(bytes(password, encoding='utf-8')).hexdigest() == auth_dict[user]

        if password_correct:
            print(f"{user} logged successfully")
            import_log(user) # Try to import previous Fooocus log upon login

        return password_correct


def import_log(username: str):
    """Launches a script to move user's log-atlas.html to a specified location"""
    from ldm_patched.modules.args_parser import args as global_args
    import subprocess, os
    from pathlib import Path
    if global_args.importScript is None:
        return
    script_path = Path(global_args.importScript).as_posix()
    if script_path and os.path.exists(script_path) and os.path.isfile(script_path):
        try:
            print("Ran subprocess upon login")
            subprocess.Popen([script_path, username])
        except Exception as e:
            print(e)
