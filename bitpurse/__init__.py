#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2012 Benoit HERVIER <khertan@khertan.net>
# Licenced under GPLv3

## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published
## by the Free Software Foundation; version 3 only.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.

from PySide.QtGui import QApplication
from PySide.QtCore import QUrl, QObject
from PySide import QtDeclarative
from PySide.QtOpenGL import QGLWidget, QGLFormat
from wallet import WalletController
from settings import Settings
import sys
import os
import os.path

__author__ = 'Benoit HERVIER (Khertan)'
__email__ = 'khertan@khertan.net'
__version__ = '1.7.0'
__build__ = '1'
__upgrade__ = '''0.9.0: First beta release
0.9.1: Second beta release, add missing python-crypto dependancy
0.9.2: Second beta release, add missing python-crypto dependancy for deb
0.9.3: Fix error due to API changes of BlockChain.info
1.5.0: Rewrite to be independant of BlockChain.info my wallet service, but
       still use BlockChain.info API to get blockchain informations
1.6.0: add an unEncrypted view of wallet address and private key
       Fix new address creation with double encrypted key 
       Fix for clearing second password after successfully emitting a transaction 
1.7.0: Fix a bug in blockchain.info mywallet import
'''


class BitPurse(QApplication):
    ''' Application class '''
    def __init__(self):
        QApplication.__init__(self, sys.argv)
        self.setOrganizationName("Khertan Software")
        self.setOrganizationDomain("khertan.net")
        self.setApplicationName("BitPurse")

        self.view = QtDeclarative.QDeclarativeView()
        # Are we on mer ? So don't use opengl
        # As it didn't works on all devices
        if os.path.exists('/etc/mer-release'):
            fullscreen = True
        elif os.path.exists('/etc/aegis'):
            fullscreen = True
            self.glformat = QGLFormat().defaultFormat()
            self.glformat.setSampleBuffers(False)
            self.glw = QGLWidget(self.glformat)
            self.glw.setAutoFillBackground(False)
            self.view.setViewport(self.glw)
        else:
            fullscreen = False

        self.walletController = WalletController()
        self.rootContext = self.view.rootContext()
        self.rootContext.setContextProperty("argv", sys.argv)
        self.rootContext.setContextProperty("__version__", __version__)
        self.rootContext.setContextProperty("__upgrade__", __upgrade__
                                            .replace('\n', '<br />'))
        self.rootContext.setContextProperty('WalletController',
                                            self.walletController)
        self.rootContext.setContextProperty('AddressesModel',
                                            self.walletController
                                            .addressesModel)
        self.rootContext.setContextProperty('TransactionsModel',
                                            self.walletController
                                            .transactionsModel)
        self.rootContext.setContextProperty('Settings',
                                            self.walletController
                                            .settings)

        self.view.setSource(QUrl.fromLocalFile(
            os.path.join(os.path.dirname(__file__),
                         'qml', 'main.qml')))

        self.rootObject = self.view.rootObject()
        if fullscreen:
            self.view.showFullScreen()
        else:
            self.view.show()
        # self.loginPage = self.rootObject.findChild(QObject, "loginPage")
        self.sendPage = self.rootObject.findChild(QObject, "sendPage")
        self.aboutPage = self.rootObject.findChild(QObject, "aboutPage")
        self.walletController.onError.connect(self.rootObject.onError)
        # self.walletController.onConnected.connect(self.loginPage.onConnected)
        self.walletController.onTxSent.connect(self.sendPage.onTxSent)
        # self.walletController.onTxSent.connect(self.aboutPage.onTxSent)


if __name__ == '__main__':
    sys.exit(BitPurse().exec_()) 