# -*- coding: utf-8 -*-

import hashlib
import time
import os
import json
import xbmcaddon, xbmcvfs

from sqlite3 import dbapi2 as db, OperationalError
from log_utils import log_exc
addonInfo = xbmcaddon.Addon().getAddonInfo
dataPath = xbmcvfs.translatePath(addonInfo('profile'))
cacheFile = os.path.join(dataPath, 'cache.db')


def get(function, duration, *args, **kwargs):
    """
    This module is used to get/set cache for every action done in the system
    :param function: Function to be executed
    :param duration: Duration of validity of cache in hours
    :param args: Optional arguments for the provided function
    """

    key = _hash_function(function, args, kwargs)
    cache_result = cache_get(key)
    if cache_result:
        if _is_cache_valid(cache_result["date"], duration):
            try:
                if cache_result["value"] == "True":
                    return []
                return json.loads(cache_result["value"])
            except Exception as e:
                print(f'Błąd przetwarzania wyniku pamięci podręcznej: {e}')

    fresh_result = function(*args, **kwargs)

    if _is_valid_result(fresh_result):
        try:
            cache_insert(key, json.dumps(fresh_result))
            return fresh_result
        except Exception as e:
            print(f'Nie dodano poprawnego rezultatu do cache: {e}')
            print(f'Cache fresh result: {str(fresh_result)}')

    if cache_result:
        return json.loads(cache_result["value"])

    if fresh_result == "404:NOT FOUND":
        cache_insert(key, None)

    return None


def _hash_function(function, args, kwargs):
    combined = f"{function.__name__}_{args}_{kwargs}"
    return hashlib.md5(combined.encode()).hexdigest()


def _is_cache_valid(stored_time, duration):
    current_time = int(time.time())
    #print(f"current_time: {current_time}")
    #print(f"stored_time: {stored_time}")
    return (current_time - int(stored_time)) < duration


def _is_valid_result(result):
    return result not in [None, "", [], {}, "404:NOT FOUND"]


def create_cache_table():
    cursor = _get_connection_cursor()
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS cache (key TEXT, value TEXT, date INTEGER, UNIQUE(key))"
    )

#old functions
def timeout(function_, *args, **kwargs):
    try:
        key = _hash_function(function_, args, kwargs)
        result = cache_get(key)
        return int(result['date']) if result else 0
    except Exception:
        return 0

def remove(function, *args, **kwargs):
    try:
        key = _hash_function(function, args, kwargs)
        key_exists = cache_get(key)
        if key_exists:
            dbcon = _get_connection()
            #dbcur = _get_connection_cursor(dbcon)
            dbcur = _get_connection_cursor()
            dbcur.execute('DELETE FROM cache WHERE key=?', (key,))
            dbcur.connection.commit()
    except:
        print('Cache remove error:')
    try:
        dbcon.close()
    except:
        pass
'''
def cache_existing(function, *args):
    try:
        cache_result = cache_get(_hash_function(function, args))
        if cache_result:
            return literal_eval(cache_result['value'])
        else:
            return None
    except:

        print('Cache existing error:')
        return None
'''
def cache_get(key):
    # type: (str, str) -> dict or None
    try:
        create_cache_table()
        cursor = _get_connection_cursor()
        cursor.execute('SELECT * FROM cache WHERE key=?', (key,))
        return cursor.fetchone()
    except OperationalError:
        return None


def cache_insert(key, value):
    # type: (str, str) -> None
    try:
        create_cache_table()
        cursor = _get_connection_cursor()
        now = int(time.time())
        cursor.execute(
            'CREATE TABLE IF NOT EXISTS cache (key TEXT, value TEXT, date INTEGER, UNIQUE(key))')

        update_result = cursor.execute(
            'UPDATE cache SET value=?,date=? WHERE key=?', (value, now, key)
        )

        if update_result.rowcount == 0:
            cursor.execute(
                'INSERT INTO cache Values (?, ?, ?)', (key, value, now)
            )

        cursor.connection.commit()

    except OperationalError:
        print(f'Błąd cache insert {key}')
        log_exc()
        pass

def remove_partial_key(partial_key):
    try:
        create_cache_table()
        cursor = _get_connection_cursor()
        cursor.execute(f"DELETE FROM cache WHERE key LIKE '%{partial_key}%'")
        cursor.connection.commit()
    except OperationalError:
        pass

def cache_clear(flush_only=False):
    cleared = False
    try:
        dbcon = _get_connection()
        dbcur = _get_connection_cursor()
        #dbcur = _get_connection_cursor(dbcon)
        if flush_only:
            dbcur.execute('DELETE FROM cache')
            dbcur.connection.commit()  # added this for what looks like a 19 bug not found in 18, normal commit is at end
            dbcur.execute('VACUUM')
            cleared = True
        else:
            dbcur.execute('DROP TABLE IF EXISTS cache')

            dbcur.execute('VACUUM')
            dbcur.connection.commit()
            cleared = True
    except Exception as e:
        print(repr(e))
        print('Cache  cache_clear error: ')
        cleared = False
    finally:
        dbcon.close()
    return cleared


def cache_clear_all():
    cache_clear()
#    cache_clear_search()
#   cache_clear_meta()
#   cache_clear_providers()


def _get_connection_cursor():
    return _get_connection().cursor()


def _get_connection():
    if not xbmcvfs.exists(dataPath):
        xbmcvfs.mkdir(dataPath)
    dbcon = db.connect(cacheFile, timeout=60) # added timeout 3/23/21 for concurrency with threads
    dbcon.execute('PRAGMA page_size = 32768')
    dbcon.execute('PRAGMA journal_mode = OFF')
    dbcon.execute('PRAGMA synchronous = OFF')
    dbcon.execute('PRAGMA temp_store = memory')
    dbcon.execute('PRAGMA mmap_size = 30000000000')
    dbcon.row_factory = _dict_factory
    return dbcon


def _dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d
# meta cache
'''
def _get_connection_cursor_meta():
    conn = _get_connection_meta().cursor()
    return conn

def _get_connection_meta():
    xbmcvfs.mkdir(dataPath)
    conn = db.connect(os.path.join(dataPath, metacacheFile))
    conn.row_factory = _dict_factory
    return conn

def cache_clear_meta():

    try:
        cursor = _get_connection_cursor_meta()

        for t in ['meta']:
            try:
                cursor.execute(f'DROP TABLE IF EXISTS {t}')
                cursor.execute('VACUUM')
                cursor.commit()
            except:
                pass
    except:
        pass

def cache_clear_search():
    try:
        cursor = _get_connection_search().cursor()

        for t in ['tvshow', 'movies']:
            try:
                cursor.execute(f'DROP TABLE IF EXISTS {t}')
                cursor.execute('VACUUM')
                cursor.commit()
            except:
                pass
    except:
        pass


def _get_connection_search():
    xbmcvfs.mkdir(dataPath)
    conn = db.connect(os.path.join(dataPath, searchFile))
    conn.row_factory = _dict_factory
    return conn
'''


'''
def _hash_function(function_instance, *args):
    return _get_function_name(function_instance) + _generate_md5(args)


def _get_function_name(function_instance):
    return re.sub(
        ".+\smethod\s|.+function\s|\sat\s.+|\sof\s.+", "", repr(function_instance)
    )


def _generate_md5(*args):
    md5_hash = hashlib.md5()
    try:
        [md5_hash.update(str(arg)) for arg in args]
    except:
        [md5_hash.update(str(arg).encode('utf-8')) for arg in args]
    return str(md5_hash.hexdigest())


def _is_cache_valid(cached_time, cache_timeout):
    now = int(time.time())
    diff = now - cached_time
    return (cache_timeout * 3600) > diff
'''
