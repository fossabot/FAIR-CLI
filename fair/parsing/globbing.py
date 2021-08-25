#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""

Glob User Config
=================

Substitute globular expressions in `config.yaml` for entries
within the local registry


Contents
========

Functions
-------

    glob_read_write - glob expressions in 'read' and 'write' blocks

"""

__date__ = "2021-08-16"

import typing
import copy

import fair.registry.requests as fdp_reg_req
import fair.configuration as fdp_conf
import fair.exceptions as fdp_exc
import fair.utilities as fdp_util

def glob_read_write(
    local_repo: str,
    config_dict_sub: typing.List,
    search_key: str = 'name',
    local_glob: bool = False,
    remove_wildcard: bool = False) -> typing.List:
    """Substitute glob expressions in the 'read' or 'write' part of a user config

    Parameters
    ----------
    local_repo : str
        local FAIR repository directory
    config_dict_sub : List[Dict]
        entries to read/write from registry
    search_key : str, optional
        key to search under, default is 'name'
    local_glob : bool, optional
        whether to search the local or remote registry,
        default is False.
    remove_wildcard: bool, optional
        whether to delete wildcard from yaml file, default is False
    """
    _parsed: typing.List[typing.Dict] = []

    # Check whether to glob the local or remote registry
    # retrieve the URI from the repository CLI config
    if local_glob:
        _uri = fdp_conf.get_local_uri()
    else:
        _uri = fdp_conf.get_remote_uri(local_repo)

    # Iterate through all entries in the section looking for any
    # key-value pairs that contain glob statements.
    for entry in config_dict_sub:
        # We still want to keep the wildcard version in case the
        # user wants to write to this namespace
        if not remove_wildcard:
            _parsed.append(entry)

        _glob_vals = [(k, v) for k, v in entry.items() if '*' in v]
        if len(_glob_vals) > 1:
            # For now only allow one value within the dictionary to have them
            raise fdp_exc.NotImplementedError(
                "Only one key-value pair in a 'read' list entry may contain a"
                " globbable value"
            )
        elif len(_glob_vals) == 0:
            # If no globbables keep existing statement
            _parsed.append(entry)
            continue

        _key_glob, _globbable = _glob_vals[0]

        # Send a request to the relevant registry using the search string
        # and the selected search key
        _results = fdp_reg_req.get(
            _uri,
            _key_glob,
            params = {search_key: _globbable}
        )

        # Iterate through all results, make a copy of the entry and swap
        # the globbable statement for the result statement appending this
        # to the output list
        for result in _results:
            _entry_dict = copy.deepcopy(entry)
            _entry_dict[_key_glob] = result[search_key]
            _parsed.append(_entry_dict)

    # Before returning the list of dictionaries remove any duplicates
    return fdp_util.remove_dictlist_dupes(_parsed)
