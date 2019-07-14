from configparser import NoOptionError

from redis import Redis

# Config Sections and Keys
RCONFIG_SECTION = 'Redis'
RCONFIG_PERSISTENT_SECTION = 'Persistent_Redis'
RCONFIG_KEY_HOST = 'host'
RCONFIG_KEY_PORT = 'port'
RCONFIG_KEY_DB = 'db'
RCONFIG_KEY_EXPIRE = 'expire'

RCONFIG_VALUE_EXPIRE = None
RCONFIG_VALUE_EXPIRE_COMMANDS = 5


def log(s):
    # dummy method
    pass


def _get_redis(config, section):
    """
    :param ConfigParser config:
    :param str section:
    :return Redis:
    """
    return Redis(host=config.get(section, RCONFIG_KEY_HOST),
                 port=config.getint(section, RCONFIG_KEY_PORT),
                 db=config.get(section, RCONFIG_KEY_DB),
                 socket_connect_timeout=5)


def get_redis(config):
    """
    Returns the default Redis connection
    :param ConfigParser config:
    :return Redis:
    """
    global RCONFIG_VALUE_EXPIRE
    try:
        RCONFIG_VALUE_EXPIRE = config.getint(RCONFIG_SECTION, RCONFIG_KEY_EXPIRE)
        log("The Redis values will expire after {} seconds.".format(RCONFIG_VALUE_EXPIRE))
    except NoOptionError:
        log("The Redis values will not expire.")
        RCONFIG_VALUE_EXPIRE = None
    except ValueError:
        log("The provided default Expire value is invalid! No expiration will be set.")
        RCONFIG_VALUE_EXPIRE = None

    return _get_redis(config, RCONFIG_SECTION)


def get_persistent_redis(config):
    """
    Returns the Persistent Redis Connection
    :param ConfigParser config:
    :return Redis:
    """
    return _get_redis(config, RCONFIG_PERSISTENT_SECTION)


def get_piped(r, keys):
    """
    Creates a Pipeline and requests all listed items at once.
    Returns a dictionary with the key-value pairs being equivalent
    to the stored values in Redis.
    :param Redis r:
    :param list of str keys:
    :return dict of (str, str):
    """
    data_dict = {}
    pipe = r.pipeline()
    for key in keys:
        pipe.get(key)
        data_dict[key] = None

    data = pipe.execute()
    for i, item in enumerate(data):
        data_dict[keys[i]] = item

    return data_dict


def set_piped(r, data_dict):
    """
    Creates a Pipeline and sends all listed items at once.
    Returns a dictionary with the key-value pairs containing the
    result of each operation.
    :param Redis r:
    :param dict of (str, object) data_dict:
    :return dict of (str, str):
    """
    keys = []
    result_dict = {}
    pipe = r.pipeline()
    for key, value in data_dict.iteritems():
        if value is None:
            pipe.delete(key)
        else:
            pipe.set(key, value, ex=RCONFIG_VALUE_EXPIRE)

        result_dict[key] = None
        keys.append(key)

    data = pipe.execute()
    for i, item in enumerate(data):
        result_dict[keys[i]] = item

    return result_dict


def incr_piped(r, data_dict):
    """
    Same as set_piped, but uses INCRBY instead of SET.
    Increases <key> by <value>.
    Note that INCRBY does not support expiration so this will
    not be taken into account
    :param Redis r:
    :param dict of (str, object) data_dict:
    :return dict of (str, str):
    """
    keys = []
    result_dict = {}
    pipe = r.pipeline()
    for key, value in data_dict.iteritems():
        if value is None:
            pipe.delete(key)
        else:
            pipe.incrbyfloat(key, value)

        result_dict[key] = None
        keys.append(key)

    data = pipe.execute()
    for i, item in enumerate(data):
        result_dict[keys[i]] = item

    return result_dict


def get_command_param_key(command, param_name):
    return command + '.Param:' + param_name


def send_command_request(r, command, params=None):
    """
    Creates a new Command Request and sends it to Redis for
    a request processor to process
    :param Redis r: Redis instance
    :param str command: Command Name
    :param dict of str, object params: Optional Command params
    :return:
    """
    pipe = r.pipeline()
    pipe.set(command, True, ex=RCONFIG_VALUE_EXPIRE_COMMANDS)
    if params:
        for key, value in params.iteritems():
            if value is not None:
                param_key = get_command_param_key(command, key)
                pipe.set(param_key, value, ex=RCONFIG_VALUE_EXPIRE_COMMANDS)

    pipe.execute()


def set_command_as_handled(r, command):
    """
    Removes a Command Request from Redis and thus marks it as handled
    :param Redis r: Redis instance
    :param str command: Command Name
    """
    pipe = r.pipeline()
    pipe.delete(command)
    pipe.execute()


def get_command_params(r, command, params, delete_after_request=True):
    """
    Returns one or more parameters of a given command
    :param Redis r: Redis instance
    :param str command: Command Name
    :param str|list of str params: Paramter Name or list of Parameter Names to request
    :param bool delete_after_request: If True, all requested parameters will be deleted after execution
    :return str|dict of str, str:
    """
    if isinstance(params, list):
        output = {}
        keys = []
        key_map = {}

        for key in params:
            output[key] = None
            param_key = get_command_param_key(command, key)
            keys.append(param_key)
            key_map[param_key] = key

        out = get_piped(r, keys)

        for key, value in out.iteritems():
            output[key_map[key]] = value

        if delete_after_request:
            pipe = r.pipeline()
            for key in keys:
                r.delete(key)
            pipe.execute()

        return output
    else:
        return r.get(get_command_param_key(command, params))


def load_synced_value(r, pr, key):
    """
    :param Redis r: Redis instance
    :param Redis pr: Persistent Redis instance
    :param str key:
    :return str:
    """
    o = get_piped(pr, [key])
    if key in o and o[key]:
        set_piped(r, {key: o[key]})
        return o[key]
    else:
        r.delete(key)
        return None


def save_synced_value(r, pr, key, value):
    """
    :param Redis r: Redis instance
    :param Redis pr: Persistent Redis instance
    :param str key:
    :param str|None value:
    :return str:
    """
    if value:
        s = {key: value}
        set_piped(r, s)
        set_piped(pr, s)
    else:
        r.delete(key)
        pr.delete(key)


def check_command_requests(r, commands):
    """
    Checks a list of commands for a pending request
    :param Redis r: Redis instance
    :param list of str commands: List of Commands
    :return:
    """
    return get_piped(r, commands)
