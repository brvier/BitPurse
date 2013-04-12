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

from PySide.QtCore import Slot, QObject, \
    Signal, Property, QTimer
from PySide.QtGui import QApplication, QClipboard
import urllib2
import json
from PBKDF2 import PBKDF2
from Crypto.Cipher import AES
import threading
import os.path

from address import AddressesModel, Address, TransactionHist, TransactionsModel
from transaction import Transaction, TransactionSubmitted
from settings import Settings
import decimal

from utils import prettyPBitcoin, unpadding, \
    getDataFromChainblock, \
    padding, getAddrFromPrivateKey, \
    EC_KEY, getSecret, \
    SecretToASecret

from wallet import Wallet, DataError, WrongPassword

class WalletController(QObject):
    onError = Signal(unicode)
    onConnected = Signal(bool)
    onTxSent = Signal(bool)
    onBusy = Signal()
    onDoubleEncrypted = Signal()
    onBalance = Signal()
    onFiatBalance = Signal()
    onWalletUnlocked = Signal()
    onCurrentBalance = Signal()
    onCurrentFiatBalance = Signal()
    onCurrentLabel = Signal()
    onCurrentAddress = Signal()
    onCurrentDoubleEncrypted = Signal()
    onCurrentPassKey = Signal()
    onCurrentWatchOnly = Signal()

    def __init__(self,):
        QObject.__init__(self,)
        self.thread = None
        self._balance = '<b>0.00</b>000000'
        self._fiatSymbol = u'€'
        self._fiatRate = 0
        self._fiatBalance = u'0 €'
        self._wallet = Wallet()
        self._walletUnlocked = False
        self.settings = Settings()
        self.addressesModel = AddressesModel()
        self.transactionsModel = TransactionsModel()
        self.timer = QTimer(self)
        self.timer.setInterval(900000)  # 15 min update
        self.timer.timeout.connect(self.update)
        self.timer.start()

        if self.settings.storePassKey:
            self._currentPassKey = self.settings.passKey
            try:
                self.unlockWallet(self._currentPassKey)
            except:
                self.onError.emit('Stored pass phrase is invalid')
        else:
            self._currentPassKey = None
        self._currentAddressIndex = 0

    @Slot(unicode)
    def newAddr(self, doubleKey):
        try:
            self._wallet.createAddr(doubleKey)
            self.storeWallet()
            self.update()
        except (WrongPassword, DataError), err:
            self.onError.emit(unicode(err))

    @Slot(unicode, result=unicode)
    def exportDecryptedAsText(self, doubleKey):
        try:
            return self._wallet.exportDecryptedAsText(doubleKey)

        except (WrongPassword, DataError), err:
            self.onError.emit(unicode(err))
            return ''

    @Slot(result=bool)
    def walletExists(self,):
        if not os.path.exists(os.path.join(
                os.path.expanduser('~'),
                '.bitpurse.wallet')):
            return False
        return True

    @Slot(unicode)
    def createWallet(self, passKey):
        self.settings.doubleEncryption = False
        self._currentPassKey = passKey
        self._walletUnlocked = True
        self._wallet.createAddr(None)
        self._wallet.store(passKey)
        self.update()

    def storeWallet(self):
        self._wallet.store(self._currentPassKey)
        self.addressesModel.setData(self._wallet.getActiveAddresses())

    def getCurrentPassKey(self):
        return self._currentPassKey

    def setCurrentPassKey(self, value):
        self._currentPassKey = value
        self.settings.currentPassKey = value
        self.onCurrentPassKey.emit()

    def getCurrentBalance(self):
        try:
            return prettyPBitcoin(self._wallet.addresses[
                self._currentAddressIndex].balance)
        except IndexError:
            return prettyPBitcoin(0)

    def getCurrentFiatBalance(self):
        try:
            return '%f %s (%f)' \
                % (self._wallet.addresses[self._currentAddressIndex].balance
                   * self._fiatRate / 100000000, self._fiatSymbol,
                   self._fiatRate)
        except IndexError:
            return ''

    def getCurrentLabel(self):
        try:
            return self._wallet.addresses[
                self._currentAddressIndex].label
        except IndexError:
            return ''

    def getCurrentAddress(self):
        try:
            return self._wallet.addresses[
                self._currentAddressIndex].addr
        except IndexError:
            return ''

    def getCurrentWatchOnly(self):
        try:
            return self._wallet.addresses[self._currentAddressIndex] \
                .watchOnly
        except IndexError:
            return False

    def getCurrentDoubleEncrypted(self):
        try:
            return self._wallet.addresses[self._currentAddressIndex] \
                .doubleEncrypted
        except IndexError:
            return False

    @Slot(unicode)
    def requestFromCurrent(self, amount):
        import dbus
        import urllib

        bus = dbus.SessionBus()
        shareService = bus.get_object('com.nokia.ShareUi', '/')
        share = shareService.get_dbus_method(
            'share', 'com.nokia.maemo.meegotouch.ShareUiInterface')
        description = urllib.quote('Request %s BTC' % amount)
        title = urllib.quote('Request %s BTC' % amount)
        if amount:
            link = urllib.quote('bitcoin:%s?amount=%d'
                                % (self.getCurrentAddress(),
                                   int(decimal.Decimal(amount) * 100000000)))
        else:
            link = urllib.quote('bitcoin:%s'
                                % (self.getCurrentAddress()))

        item = 'data:text/x-url;description=%s;title=%s,%s' \
            % (description, title, link)
        share([item, ])

    @Slot()
    def exportWithShareUI(self):
        import dbus
        # import urllib
        import shutil
        shutil.copyfile(os.path.join(os.path.expanduser('~'),
                        '.bitpurse.wallet'),
                        os.path.join(os.path.expanduser('~'),
                        'MyDocs',
                        'bitpurse.wallet'))
        bus = dbus.SessionBus()
        shareService = bus.get_object('com.nokia.ShareUi', '/')
        share = shareService.get_dbus_method(
            'share', 'com.nokia.maemo.meegotouch.ShareUiInterface')
        # description = urllib.quote('BitPurse Wallet')
        # title = urllib.quote('BitPurse Wallet')
        link = os.path.join(os.path.expanduser('~'),
                            'MyDocs',
                            'bitpurse.wallet')
        item = '%s' % link
        share([item, ])

    @Slot(unicode, unicode, unicode, unicode)
    def importFromBlockchainInfoWallet(self, guid, key, skey, dkey):
        if self.thread:
            if self.thread.isAlive():
                self.onError.emit(
                    u'Please wait, a communication is already in progress')
        self.thread = threading.Thread(None,
                                       self._importFromBlockchainInfoWallet,
                                       None, (guid, key, skey, dkey))
        self.thread.start()

    @Slot(unicode, unicode, unicode)
    def importFromPrivateKey(self, privateKey,
                             label='Undefined', doubleKey=''):
        try:
            self._wallet.importFromPrivateKey(self._currentPassKey,
                                              privateKey,
                                              label,
                                              doubleKey)
            self.storeWallet()
            self.onError.emit('Key imported')
            self.update()
        except Exception, err:
            print err
            import traceback
            traceback.print_exc()
            self.onError.emit(unicode(err))

    @Slot(unicode, result=bool)
    def doubleEncrypt(self, doubleKey):
        return self._doubleEncrypt(doubleKey)

    @Slot(unicode, unicode)
    def importWatchOnly(self, addr,
                        label='Undefined'):
        try:
            self._wallet.importWatchOnly(self._currentPassKey,
                                         addr,
                                         label)
            self.storeWallet()
            self.onError.emit('Address imported')
            self.update()
        except Exception, err:
            print err
            import traceback
            traceback.print_exc()
            self.onError.emit(unicode(err))

    def _importFromBlockchainInfoWallet(self, guid, key, skey, doubleKey):
        self.onBusy.emit()
        try:
            self._wallet.importFromBlockchainInfoWallet(
                self._currentPassKey,
                guid, key, skey, doubleKey)
            self.storeWallet()
        except Exception, err:
            print err
            import traceback
            traceback.print_exc()
            self.onError.emit(unicode(err))
        try:
            self._update()
        except:
            pass
        self.onBusy.emit()

    def _doubleEncrypt(self, doubleKey):
        self.onBusy.emit()
        try:
            self._wallet.doubleEncryptPrivKeys(doubleKey)
            self.settings.useDoubleEncryption = True
            self.storeWallet()
            self._update()
        except Exception, err:
            self.onError.emit(unicode(err))
            self.settings.useDoubleEncryption = False
            self.settings.on_useDoubleEncryption.emit()
        self.onBusy.emit()
        return self.settings.useDoubleEncryption

    @Slot(unicode, result=bool)
    def doubleDecrypt(self, doubleKey):
        return self._doubleDecrypt(doubleKey)

    def _doubleDecrypt(self, doubleKey):
        self.onBusy.emit()
        try:
            self._wallet.doubleDecryptPrivKeys(doubleKey)
            self.settings.useDoubleEncryption = False
            self.storeWallet()
            self._update()
        except Exception, err:
            self.settings.useDoubleEncryption = True
            self.settings.on_useDoubleEncryption.emit()
            self.onError.emit(unicode(err))
        self.onBusy.emit()
        return self.settings.useDoubleEncryption

    @Slot(unicode, unicode, unicode, unicode)
    def sendFromCurrent(self, dstAddr, amout, fee, secondPassword=None):
        if self.thread:
            if self.thread.isAlive():
                self.onError.emit(
                    u'Please wait, a communication is already in progress')
        self.thread = threading.Thread(None,
                                       self._sendFromCurrent,
                                       None, (dstAddr, amout,
                                              fee, secondPassword))
        self.thread.start()

    def _sendFromCurrent(self, dstAddr, amout, fee, secondPassword):
        self.onBusy.emit()
        try:
            Transaction(self.getCurrentAddress(),
                        [(dstAddr,
                         int(decimal.Decimal(amout) * 100000000)), ],
                        self._wallet.getPrivKeyForAddress(
                        self.getCurrentAddress(), secondPassword),
                        fee=int(decimal.Decimal(fee) * 100000000),
                        change_addr=None)
        except TransactionSubmitted, err:
            print 'TransactionSubmitted:', err
            self.onTxSent.emit(True)
            self.onError.emit(unicode(err))
            try:
                self._update()
            except:
                pass
        except Exception, err:
            print err
            import traceback
            traceback.print_exc()
            self.onError.emit(unicode(err))
            self.onTxSent.emit(False)
        self.onBusy.emit()

    @Slot(unicode, result=bool)
    def unlockWallet(self, passKey):
        try:
            self.setCurrentPassKey(passKey)
            try:
                self._wallet.load_addresses(self._currentPassKey)
            except ValueError:
                raise WrongPassword('Wrong passphrase')
            try:
                self._updateFiat()
            except (urllib2.URLError, urllib2.HTTPError):
                pass
            self._balance = prettyPBitcoin(self._wallet.balance)
            self._fiatBalance = u'%f %s (%f)' % ((self._wallet.balance
                                                  * self._fiatRate
                                                  / 100000000),
                                                 self._fiatSymbol,
                                                 self._fiatRate)
            self.onBalance.emit()
            self.onFiatBalance.emit()
            self._walletUnlocked = True
            self.addressesModel.setData(self._wallet.getActiveAddresses())

        except WrongPassword:
            self.onError.emit(u'Wrong passphrase')
            import traceback
            traceback.print_exc()
            return False

        except Exception, err:
            self.onError.emit(unicode(err))
            import traceback
            traceback.print_exc()
            return False
        return True

    @Slot()
    def update(self,):
        if self._walletUnlocked:
            if self.thread:
                if self.thread.isAlive():
                    return
            self.thread = threading.Thread(None, self._update, None, ())
            self.thread.start()

    def _updateFiat(self,):
        req = 'https://blockchain.info/ticker'
        data = getDataFromChainblock(req)
        self._fiatRate = data[self.settings.fiatCurrency]['15m']
        self._fiatSymbol = data[self.settings.fiatCurrency]['symbol']
        print self._fiatRate, self._fiatSymbol

    def _update(self,):
        self.onBusy.emit()
        try:
            self._wallet.update(self._currentPassKey)
            self._updateFiat()
            self._balance = prettyPBitcoin(self._wallet.balance)
            self._fiatBalance = u'%f %s (%f)' % ((self._wallet.balance
                                                  * self._fiatRate
                                                  / 100000000),
                                                 self._fiatSymbol,
                                                 self._fiatRate)
            self.onBalance.emit()
            self.onFiatBalance.emit()
            # print self._wallet.getActiveAddresses()
            self.addressesModel.setData(self._wallet.getActiveAddresses())
            try:
                self.transactionsModel.setData(
                    self._wallet.addresses[self._currentAddressIndex]
                    .transactions)
            except IndexError:
                print 'index error loading transactions model : ', \
                      self._currentAddressIndex
                self._currentAddressIndex = 0

            # self.onDoubleEncrypted.emit()
            # self.onConnected.emit(True)
            # self.setDefaultAddress()
        except urllib2.URLError:
            pass
        except Exception, err:
            print err
            self.onError.emit(unicode(err))
        self.onBusy.emit()

    @Slot(unicode)
    def remove(self, addr):
        self._wallet.remove(addr)
        self.storeWallet()
        self.update()

    @Slot(unicode, result=unicode)
    def getLabelForAddr(self, addr):
        return self._wallet.getLabelForAddr(addr)

    @Slot(unicode, unicode)
    def setLabelForAddr(self, addr, label):
        self._wallet.setLabelForAddr(addr, label)
        self.storeWallet()

    @Slot(unicode)
    def setCurrentAddress(self, addr):
        self._currentAddressIndex = self._wallet.getIndex(addr)
        self.onCurrentBalance.emit()
        self.onCurrentLabel.emit()
        self.onCurrentAddress.emit()
        self.onCurrentWatchOnly.emit()
        self.onCurrentFiatBalance.emit()
        try:
            self.transactionsModel.setData(
                self._wallet.addresses[self._currentAddressIndex]
                .transactions)
        except IndexError:
            print 'index error loading transactions model'

    def isBusy(self, ):
        if not self.thread:
            return False
        if self.thread.isAlive():
            return True
        return False

    def getBalance(self):
        return self._balance

    def getFiatBalance(self):
        return self._fiatBalance

    def getWalletUnlocked(self):
        return self._walletUnlocked

    @Slot(unicode)
    def putAddrInClipboard(self, addr):
        QApplication.clipboard().setText(addr, QClipboard.Clipboard)

    currentWatchOnly = Property(bool, getCurrentWatchOnly,
                                notify=onCurrentWatchOnly)
    currentDoubleEncrypted = Property(bool, getCurrentDoubleEncrypted,
                                      notify=onCurrentDoubleEncrypted)
    busy = Property(bool, isBusy,
                    notify=onBusy)
    walletUnlocked = Property(bool, getWalletUnlocked,
                              notify=onWalletUnlocked)
    balance = Property(unicode, getBalance, notify=onBalance)
    fiatBalance = Property(unicode, getFiatBalance, notify=onFiatBalance)
    currentBalance = Property(unicode,
                              getCurrentBalance,
                              notify=onCurrentBalance)
    currentFiatBalance = Property(unicode,
                                  getCurrentFiatBalance,
                                  notify=onCurrentFiatBalance)
    currentLabel = Property(unicode,
                            getCurrentLabel,
                            notify=onCurrentLabel)
    currentAddress = Property(unicode,
                              getCurrentAddress,
                              notify=onCurrentAddress)
    currentPassKey = Property(unicode,
                              getCurrentPassKey,
                              setCurrentPassKey,
                              notify=onCurrentPassKey)
