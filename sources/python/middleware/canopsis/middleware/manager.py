# -*- coding: utf-8 -*-
#--------------------------------
# Copyright (c) 2014 "Capensis" [http://www.capensis.com]
#
# This file is part of Canopsis.
#
# Canopsis is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Canopsis is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Canopsis.  If not, see <http://www.gnu.org/licenses/>.
# ---------------------------------

from canopsis.configuration import \
    Parameter, Configuration, Manager as ConfigurableManager
from . import Middleware, parse_scheme, DEFAULT_DATA_SCOPE


class Manager(ConfigurableManager):
    """
    Manages middlewares like a Manager manages sub-configurables.

    Attributes are related to middlewares where the data_scope corresponds to
    attribute names.

    Middleware instances can be shared through a sharing_scope in the same
    processus. By default, this sharing_scope is the same for all Managers.
    """

    CONF_RESOURCE = 'middleware/manager.conf'  #: conf path

    SHARED = 'shared'  #: conf shared name
    SHARING_SCOPE = 'sharing_scope'  #: conf sharing scope name
    AUTO_CONNECT = 'auto_connect'  #: conf auto connect name
    DATA_SCOPE = 'data_scope'  #: configuration data scope name

    CATEGORY = 'MANAGER'  #: middleware manager

    MIDDLEWARE_SUFFIX = '_uri'  #: middleware attribute suffix

    __MIDDLEWARES__ = {}
    """
    Global dict of {sharing_scope: {protocol: {data_type: {data_scope:
        middleware}}}}
    """

    class Error(Exception):
        """
        Handle Manager errors.
        """
        pass

    def __init__(
        self, shared=True, sharing_scope=None, auto_connect=True,
        data_scope=None,
        *args, **kwargs
    ):
        """
        :param shared: sub-middleware shared usage (default:True)
        :type shared: bool

        :param sharing_scope: sub-middleware sharing scope usage (default:None)
        :type sharing_scope: object

        :param auto_connect: sub-middleware auto connect (default:True)
        :type auto_connect: bool

        :param data_scope: sub-middleware data_scope property (default:None)
        :type data_scope: str
        """

        super(Manager, self).__init__(*args, **kwargs)

        self.auto_connect = auto_connect
        self.shared = shared
        self.sharing_scope = sharing_scope
        self.data_scope = data_scope

    @property
    def shared(self):
        return self._shared

    @shared.setter
    def shared(self, value):
        self._shared = value

    @property
    def sharing_scope(self):
        return self._sharing_scope

    @sharing_scope.setter
    def sharing_scope(self, value):
        self._sharing_scope = value

    @property
    def auto_connect(self):
        return self._auto_connect

    @auto_connect.setter
    def auto_connect(self, value):
        self._auto_connect = value

    @property
    def data_scope(self):
        return self._data_scope

    @data_scope.setter
    def data_scope(self, value):
        self._data_scope = value

    def get_middleware(
        self,
        protocol, data_type=None, data_scope=None,
        auto_connect=None,
        shared=None, sharing_scope=None,
        *args, **kwargs
    ):
        """
        Load a middleware related to input uri.

        If shared, the result instance is shared among sharing_scope, protocol,
        data_type and data_scope.

        :param protocol: protocol to use
        :type protocol: str

        :param data_type: data type to use
        :type data_type: str

        :param data_scope: data scope to use
        :type data_scope: str

        :param auto_connect: middleware auto_connect parameter
        :type auto_connect: bool

        :param shared: if True, the result is a shared middleware instance
            among managers of the same class. If None, use self.shared.
        :type shared: bool

        :param sharing_scope: scope sharing
        :type sharing_scope: bool

        :return: middleware instance corresponding to input uri and data_scope.
        :rtype: Middleware
        """

        if data_scope is None:
            data_scope = self._data_scope

        if auto_connect is None:
            auto_connect = self._auto_connect

        if shared is None:
            shared = self._shared

        if sharing_scope is None:
            sharing_scope = self._sharing_scope

        if shared:

            protocols = Manager.__MIDDLEWARES__.setdefault(
                sharing_scope, {})

            data_types = protocols.setdefault(protocol, {})

            data_scopes = data_types.setdefault(data_type, {})

            try:
                result = data_scopes.setdefault(data_scope,
                    Middleware.get_middleware(
                        protocol=protocol, data_type=data_type,
                        data_scope=data_scope, auto_connect=auto_connect,
                        *args, **kwargs))

            except Exception as e:
                # clean memory in case of error
                if not data_scopes:
                    del data_types[data_type]
                if not data_types:
                    del protocols[protocol]
                if not protocols:
                    del Manager.__MIDDLEWARES__[sharing_scope]
                # and raise back e
                raise e

        else:
            # get a new middleware instance
            result = Middleware.get_middleware(
                protocol=protocol, data_type=data_type, data_scope=data_scope,
                auto_connect=auto_connect,
                *args, **kwargs)

        return result

    def get_middleware_by_uri(
        self,
        uri,
        auto_connect=None, shared=None, sharing_scope=None, *args, **kwargs
    ):

        """
        Load a middleware related to input uri.

        If shared, the result instance is shared among same middleware type
        and self class type.

        :param uri: middleware uri
        :type uri: str

        :param auto_connect: middleware auto_connect parameter
        :type auto_connect: bool

        :param shared: if True, the result is a shared middleware instance
            among managers of the same class. If None, use self.shared.
        :type shared: bool

        :param sharing_scope: scope sharing
        :type sharing_scope: bool

        :return: middleware instance corresponding to the input uri.
        :rtype: Middleware
        """

        protocol, data_type, data_scope = parse_scheme(uri)

        result = self.get_middleware(
            protocol=protocol, data_type=data_type, data_scope=data_scope,
            auto_connect=auto_connect, shared=shared,
            sharing_scope=sharing_scope, uri=uri, *args, **kwargs)

        return result

    def _get_conf_files(self, *args, **kwargs):

        result = super(Manager, self)._get_conf_files(
            *args, **kwargs)

        result.append(Manager.CONF_RESOURCE)

        return result

    def _conf(self, *args, **kwargs):

        result = super(Manager, self)._conf(*args, **kwargs)

        result.add_unified_category(
            name=Manager.CATEGORY,
            new_content=(
                Parameter(Manager.SHARED, self.shared, parser=Parameter.bool),
                Parameter(Manager.SHARING_SCOPE, self.sharing_scope),
                Parameter(Manager.AUTO_CONNECT, self.auto_connect),
                Parameter(Manager.DATA_SCOPE, self.data_scope)))

        return result

    def _configure(self, unified_conf, *args, **kwargs):

        super(Manager, self)._configure(
            unified_conf=unified_conf, *args, **kwargs)

        # set shared
        self._update_property(
            unified_conf=unified_conf, param_name=Manager.SHARED)
        self._update_property(
            unified_conf=unified_conf, param_name=Manager.SHARING_SCOPE)
        self._update_property(
            unified_conf=unified_conf, param_name=Manager.AUTO_CONNECT)
        self._update_property(
            unified_conf=unified_conf, param_name=Manager.DATA_SCOPE)

        values = unified_conf[Configuration.VALUES]

        # set all middlewares which ends with Manager.MIDDLEWARE_SUFFIX
        for parameter in values:
            if parameter.name.endswith(Manager.MIDDLEWARE_SUFFIX):
                name = parameter.name[:-len(Manager.MIDDLEWARE_SUFFIX)]
                # set a middleware in list of configurables
                self[name] = Middleware.get_middleware_by_uri(
                    uri=parameter.value)
