#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2011 Benoit HERVIER <khertan@khertan.net>
# Licenced under GPLv3

## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published
## by the Free Software Foundation; version 3 only.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.

import ConfigParser
from PySide.QtCore import Slot, QObject, Property, Signal

import os


class Settings(QObject):
    '''Config object'''

    def __init__(self,):
        QObject.__init__(self,)
        self.config = ConfigParser.ConfigParser()
        if not os.path.exists(os.path.expanduser('~/.bitpurse.cfg')):
            self._write_default()
        else:
            self.config.read(os.path.expanduser('~/.bitpurse.cfg'))

    def _write_default(self):
        ''' Write the default config'''
        self.config.add_section('Security')
        self.config.set('Security', 'saveLogin', 'true')
        self.config.set('Security', 'savePassword', 'false')
        self.config.set('Security', 'login', '')
        self.config.set('Security', 'password', '')

        # Writing our configuration file to 'example.cfg'
        with open(os.path.expanduser('~/.bitpurse.cfg'), 'wb') \
                as configfile:
            self.config.write(configfile)

    def _set(self, option, value):
        #Avoid useless change due to binding
        if self.get(option) == value:
            return

        if option in ('saveLogin', 'savePassword', 'login',
                      'password',):
            self.config.set('Security', option, value)
        else:
            self.config.set('General', option, value)

        self._write()

    def _write(self,):
        with open(os.path.expanduser('~/.bitpurse.cfg'), 'wb') \
                as configfile:
            self.config.write(configfile)

    @Slot(unicode, result=unicode)
    def get(self, option):
        try:
            return self.config.get('Security', option)
        except:
            try:
                return self.config.get('General', option)
            except:
                return ''

    def _get_saveLogin(self,):
        return self.get('saveLogin') == 'true'

    def _get_login(self,):
        return self.get('login')

    def _get_savePassword(self,):
        return self.get('savePassword') == 'true'

    def _get_password(self,):
        return self.get('password')

    def _set_saveLogin(self, b):
        self._set('saveLogin', 'true' if b else 'false')

    def _set_login(self, login):
        self._set('login', login)

    def _set_savePassword(self, b):
        self._set('savePassword', 'true' if b else 'false')

    def _set_password(self, password):
        self._set('password', password)

    on_saveLogin = Signal()
    on_login = Signal()
    on_savePassword = Signal()
    on_password = Signal()

    saveLogin = Property(bool, _get_saveLogin,
                         _set_saveLogin, notify=on_saveLogin)
    login = Property(unicode, _get_login, _set_login,
                     notify=on_login)
    savePassword = Property(bool, _get_savePassword,
                            _set_savePassword, notify=on_savePassword)
    password = Property(unicode, _get_password,
                        _set_password, notify=on_password)

