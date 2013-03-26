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

''' Settings :
    * Store primary password (Yes/No)
    * Primary password : unicode
    * Use double encryption (Yes/No)
    * Sync with BlockChain.info (Yes/No)
    * Blockchain guid
    * Blockchain primary password
    '''
import ConfigParser
from PySide.QtCore import Slot, QObject, Property, Signal

import os


class Settings(QObject):
    '''Config object'''

    def __init__(self,):
        QObject.__init__(self,)
        self.config = ConfigParser.ConfigParser()
        self.check_default_and_load()
        self.currentPassKey = ''

    def check_default_and_load(self):
        if not os.path.exists(os.path.expanduser('~/.bitpurse.cfg')):
            print 'Missing prefs'
            self._write_default()
        self.config.read(os.path.expanduser('~/.bitpurse.cfg'))
        if 'General' not in self.config.sections():
            self.config.add_section('General')
        if 'usedoubleencryption' not in self.config.options('Security'):
            self._write_default()
        elif 'passkey' not in self.config.options('Security'):
            self._write_default()
        elif 'storepasskey' not in self.config.options('Security'):
            self._write_default()

    def _write_default(self):
        ''' Write the default config'''
        try:
            self.config.add_section('Security')
        except ConfigParser.DuplicateSectionError:
            pass

        try:
            self.config.set('Security', 'storePassKey', 'false')
        except ConfigParser.DuplicateOptionError:
            pass

        try:
            self.config.set('Security', 'passKey', '')
        except ConfigParser.DuplicateOptionError:
            pass

        try:
            self.config.set('Security', 'useDoubleEncryption', 'false')
        except ConfigParser.DuplicateOptionError:
            pass

        # Writing our configuration file to 'example.cfg'
        with open(os.path.expanduser('~/.bitpurse.cfg'), 'wb') \
                as configfile:
            self.config.write(configfile)

    def _set(self, option, value):
        # Avoid useless change due to binding
        if self.get(option) == value:
            return

        if option in ('storePassKey', 'passKey',
                      'useDoubleEncryption', ):
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

    def _get_storePassKey(self,):
        return self.get('storePassKey') == 'true'

    def _get_passKey(self,):
        return self.get('passKey')

    def _get_useDoubleEncryption(self,):
        return self.get('useDoubleEncryption') == 'true'

    def _set_storePassKey(self, b):
        self._set('storePassKey', 'true' if b else 'false')
        if b is 'false':
            self._set('passKey', '')
        else:
            self._set('passKey', self.currentPassKey)
        self.on_storePassKey.emit()
        self.on_passKey.emit()

    def _set_passKey(self, passKey):
        self._set('passKey', passKey)
        self.on_passKey.emit()

    def _get_numberOfLaunch(self,):
        try:
            return int(self.get('numberOfLaunch'))
        except:
            return 0

    def _set_numberOfLaunch(self, value):
        self._set('numberOfLaunch', str(value))

    def _set_useDoubleEncryption(self, b):
        self._set('useDoubleEncryption', 'true' if b else 'false')
        self.on_useDoubleEncryption.emit()

    on_storePassKey = Signal()
    on_passKey = Signal()
    on_useDoubleEncryption = Signal()
    on_numberOfLaunch = Signal ()
    numberOfLaunch = Property(int, _get_numberOfLaunch, _set_numberOfLaunch,
                              notify = on_numberOfLaunch)
    storePassKey = Property(bool, _get_storePassKey, _set_storePassKey,
                            notify=on_storePassKey)
    passKey = Property(unicode, _get_passKey,
                       _set_passKey, notify=on_passKey)
    useDoubleEncryption = Property(bool,
                                   _get_useDoubleEncryption,
                                   _set_useDoubleEncryption,
                                   notify=on_useDoubleEncryption)    