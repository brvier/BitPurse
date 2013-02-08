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
    QModelIndex, Signal, Property
import urllib2
import json
from PBKDF2 import PBKDF2
from Crypto.Cipher import AES
import threading
from datetime import datetime
from address import AddressesModel, Address, TransactionHist, TransactionsModel
from transaction import Transaction

import decimal

from utils import prettyPBitcoin, unpadding, \
    getDataFromChainblock, b58decode


class WrongPassword(Exception):
    pass


class DataError(Exception):
    pass


class Wallet(object):
    def __init__(self,):
        self.addresses = []
        self.balance = 0
        self.guid = ''
        from uuid import uuid4
        self.sharedKey = unicode(uuid4())
        self.isDoubleEncrypted = False

    def decrypt(self, key, cipherdata):
        key = PBKDF2(key, cipherdata[:16], iterations=10).read(32)
        cipher = AES.new(key, AES.MODE_CBC, cipherdata[:16])
        return unpadding(cipher.decrypt(cipherdata[16:]))

    def decryptPK(self, data, password, sharedKey):
        data = data.decode('base64', 'strict')
        key = PBKDF2(sharedKey + password, data[:16], iterations=10).read(32)
        cipher = AES.new(key, AES.MODE_CBC, data[:16])
        return unpadding(cipher.decrypt(data[16:]))

    def getRemoteWallet(self, guid, key):
        self.guid = guid
        self.key = key
        req = urllib2.Request('https://blockchain.info/wallet/'
                              + '%s?format=json&resend_code=false' %
                              self.guid,
                              None, {'user-agent': 'KhtBitcoin'})
        opener = urllib2.build_opener()
        fh = opener.open(req)
        encryptedWallet = json.loads(fh.read())['payload']

        #cipherdata = encryptedWallet.decode('base64', 'strict')
        #key = PBKDF2(self.key, cipherdata[:16], iterations=10).read(32)
        #cipher = AES.new(key, AES.MODE_CBC, cipherdata[:16])

        try:
            data = self.decrypt(self.key,
                                encryptedWallet.decode('base64', 'strict'))
            #data = unpadding(cipher.decrypt(cipherdata[16:]))
        except:
            raise WrongPassword('Unknow login')

        try:
            data = json.loads(data)
        except:
            raise WrongPassword('Incorrect password')

        self.addresses = [Address(jsondict=address)
                          for address in data['keys']]

        if 'double_encryption' in data:
            self.isDoubleEncrypted = bool(data['double_encryption'])

        if 'sharedKey' in data:
            self.sharedKey = data['sharedKey']

    def addTransactionHistForAddress(self, addr, transaction):
        for address in self.addresses:
            if addr == address.addr:
                address.transactions.append(transaction)
                return

    def getPrivKeyForAddress(self, addr, secondPassword=None):
        for address in self.addresses:
            if addr == address.addr:
                if self.isDoubleEncrypted:
                    if not secondPassword:
                        raise WrongPassword('You must provide a'
                                            ' second password for double'
                                            ' encrypted wallet')
                    try:
                        uncryptedKey = self.decryptPK(
                            address.priv,
                            secondPassword,
                            self.sharedKey)
                        if len(b58decode(uncryptedKey, None)) != 32:
                            raise WrongPassword('Wrong second password')
                        return b58decode(uncryptedKey, None)
                    except:
                        import traceback
                        traceback.print_exc()
                        raise

                else:
                    return b58decode(address.priv, None)

    def getActiveAddrAddresses(self,):
        return [address.addr for address in self.addresses if address.tag == 0]

    def getArchivedAddrAddresses(self,):
        return [address.addr for address in self.addresses if address.tag == 0]

    def getAddrAddresses(self,):
        return [address.addr for address in self.addresses]

    def getActiveAddresses(self, ):
        return [address for address in self.addresses if address.tag == 0]

    def getTransactionForAddr(self, addr):
        for address in self.addresses:
            if addr == address.addr:
                return address.transactions

    def isMine(self, address):
        if address in self.getAddrAddresses():
            return True
        return False

    def getRemoteAddresses(self,):
        req = ('https://blockchain.info/multiaddr'
               + '?format=json&filter=0&offset=0'
               + '&active=%s&archived=%s'
               % ('|'.join(self.getActiveAddrAddresses()),
               '|'.join(self.getArchivedAddrAddresses())))

        data = getDataFromChainblock(req)

        self.balance = data['wallet']['final_balance']

        for address in data['addresses']:
            try:
                for addr in self.addresses:
                    if address['address'] == addr.addr:
                        addr.balance = address['final_balance']
            except KeyError, err:
                print err

        for tx in data['txs']:
            try:
                txAddresses = {}
                txDst = []
                for txout in tx['out']:
                    if self.isMine(txout['addr']):
                        if not txout['addr'] in txAddresses:
                            txAddresses[txout['addr']] = 0
                        txAddresses[txout['addr']] += txout['value']
                    if not txout['addr'] in txDst:
                        txDst.append(txout['addr'])
                for txin in tx['inputs']:
                    if self.isMine(txin['prev_out']['addr']):
                        if not txin['prev_out']['addr'] in txAddresses:
                            txAddresses[txin['prev_out']['addr']] = 0
                        txAddresses[txin['prev_out']['addr']] -= \
                            txin['prev_out']['value']
                    if not txin['prev_out']['addr'] in txDst:
                        txDst.append(txin['prev_out']['addr'])

                for txAddress in txAddresses:
                    self.addTransactionHistForAddress(
                        txAddress,
                        TransactionHist(
                            tx['hash'],
                            unicode(datetime.fromtimestamp(tx['time'])
                                    .strftime('%c'), 'utf-8'),
                            '\n'.join(list(set(txDst)
                            .difference([txAddress, ]))),
                            txAddresses[txAddress]))

            except KeyError, err:
                print err

    def update(self, login, privkey):
        try:
            self.getRemoteWallet(login, privkey)
            self.getRemoteAddresses()
        except:
            import traceback
            traceback.print_exc()
            raise


class WalletController(QObject):
    onError = Signal(unicode)
    onConnected = Signal(bool)
    onTxSent = Signal(bool)
    onBusy = Signal()
    onDoubleEncrypted = Signal()
    onBalance = Signal()
    onCurrentAddressBalance = Signal()
    onCurrentAddressLabel = Signal()
    onCurrentAddressAddress = Signal()

    def __init__(self,):
        QObject.__init__(self,)
        self.thread = None
        self._wallet = Wallet()
        self.addressesModel = AddressesModel()
        self.transactionsModel = TransactionsModel()

        self._balance = '<b>0.00</b>0000'

        self._currentAddressBalance = '<b>0.00</b>0000'
        self._currentAddressLabel = 'Undefined'
        self._currentAddressAddress = 'Undefined'
        self._currentAddressPrivKey = 'Undefined'

    def getCurrentAddressBalance(self):
        return self._currentAddressBalance

    def setCurrentAddressBalance(self, value):
        self._currentAddressBalance = value
        self.onCurrentAddressBalance.emit()

    def getCurrentAddressLabel(self):
        return self._currentAddressLabel

    def setCurrentAddressLabel(self, value):
        self._currentAddressLabel = value
        self.onCurrentAddressLabel.emit()

    def getCurrentAddressAddress(self):
        return self._currentAddressAddress

    def setCurrentAddressAddress(self, value):
        self._currentAddressAddress = value
        self.onCurrentAddressAddress.emit()

    @Slot(unicode, unicode, unicode, unicode)
    def sendFromCurrent(self, dstAddr, amout, fee, secondPassword=None):
        if self.thread:
            if self.thread.isAlive():
                self.onError.emit(
                    u'Please wait, transactions are already in progress')
        self.thread = threading.Thread(None,
                                       self._sendFromCurrent,
                                       None, (dstAddr, amout,
                                              fee, secondPassword))
        self.thread.start()
        self.onBusy.emit()

    def _sendFromCurrent(self, dstAddr, amout, fee, secondPassword):
        self.onBusy.emit()
        try:
            Transaction(self.currentAddressAddress,
                        [(dstAddr,
                         int(decimal.Decimal(amout) * 100000000)), ],
                        self._wallet.getPrivKeyForAddress(
                        self.currentAddressAddress, secondPassword),
                        fee=int(decimal.Decimal(fee) * 100000000),
                        change_addr=None)
            self.onTxSent.emit(True)

        except Exception, err:
            print err
            self.onError.emit(unicode(err))
            self.onTxSent.emit(False)

    @Slot(unicode, unicode)
    def getData(self, guid, key):
        if self.thread:
            if self.thread.isAlive():
                return
        self.thread = threading.Thread(None, self._getData, None, (guid, key))
        self.thread.start()
        self.onBusy.emit()

    def _getData(self, guid, key):
        try:
            self._wallet.update(guid, key)
            self.onBusy.emit()
            self._balance = prettyPBitcoin(self._wallet.balance)
            self.onBalance.emit()
            self.addressesModel.setData(self._wallet.getActiveAddresses())
            self.onDoubleEncrypted.emit()
            self.onConnected.emit(True)
            self.setDefaultAddress()

        except Exception, err:
            print err
            self.onConnected.emit(False)
            self.onError.emit(unicode(err))

    def setDefaultAddress(self,):
        if len(self._wallet.addresses) > 0:
            self.setCurrentAddressLabel(self._wallet.addresses[0].label)
            self.setCurrentAddressBalance(self._wallet.addresses[0].balance)
            self.setCurrentAddressAddress(self._wallet.addresses[0].addr)

    @Slot(QModelIndex)
    def setCurrentAddress(self, index):
        self.setCurrentAddressLabel(
            self.addressesModel.data(index,
                                     AddressesModel.COLUMNS.index('label')))
        self.setCurrentAddressBalance(prettyPBitcoin(
            self.addressesModel.data(index,
                                     AddressesModel.COLUMNS.index('balance'))))
        self.setCurrentAddressAddress(
            self.addressesModel.data(index,
                                     AddressesModel.COLUMNS.index('address')))
        self.transactionsModel.setTransactions(
            self._wallet.getTransactionForAddr(self.currentAddressAddress))

    def isBusy(self, ):
        if not self.thread:
            return False
        if self.thread.isAlive():
            return True
        return False

    def getBalance(self):
        return self._balance

    def isDoubleEncrypted(self,):
        return self._wallet.isDoubleEncrypted

    doubleEncrypted = Property(bool, isDoubleEncrypted,
                               notify=onDoubleEncrypted)
    busy = Property(bool, isBusy,
                    onBusy)
    balance = Property(unicode, getBalance, notify=onBalance)
    currentAddressBalance = Property(unicode,
                                     getCurrentAddressBalance,
                                     notify=onCurrentAddressBalance)
    currentAddressLabel = Property(unicode,
                                   getCurrentAddressLabel,
                                   notify=onCurrentAddressLabel)
    currentAddressAddress = Property(unicode,
                                     getCurrentAddressAddress,
                                     notify=onCurrentAddressAddress)
