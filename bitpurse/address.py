#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2012 Benoit HERVIER <khertan@khertan.net>
# Licenced under GPLv3

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published
# by the Free Software Foundation; version 3 only.
##
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

from PySide.QtCore import QAbstractListModel, QModelIndex
from utils import prettyPBitcoin
from uuid import uuid4
from datetime import datetime
import time


class Address(object):

    def __init__(self, jsondict={}):
        # QObject.__init__(self,)
        self.addr = ''
        self.label = 'Undefined'
        self.priv = ''
        self.balance = 0
        self.tag = 0
        self.doubleEncrypted = False
        self.sharedKey = unicode(uuid4())
        self.transactions = []
        self.watchOnly = False

        try:
            self.addr = jsondict['addr']
        except KeyError:
            pass
        try:
            self.label = jsondict['label']
        except KeyError:
            pass
        try:
            self.priv = jsondict['priv']
        except KeyError:
            pass
        try:
            self.tag = jsondict['tag']
        except KeyError:
            self.tag = 0
        try:
            self.balance = jsondict['balance']
        except KeyError:
            self.balance = 0
        try:
            self.doubleEncrypted = jsondict['doubleEncrypted']
        except KeyError:
            pass
        try:
            self.sharedKey = jsondict['sharedKey']
        except KeyError:
            pass

        try:
            self.watchOnly = jsondict['watchOnly']
        except KeyError:
            pass
        print self.watchOnly

        try:
            for tx in jsondict['txs']:
                if (tx['timestamp']
                    + (60 * 60 * 24 * 7)
                        > time.time()) or (tx['confirmations'] >= 1):

                    self.transactions.append(TransactionHist(
                        tx['hash'],
                        tx['timestamp'],
                        tx['address'],
                        tx['amount'],
                        tx['confirmations']))
        except KeyError:
            pass

    def __repr__(self, ):
        return {'addr': self.addr,
                'priv': self.priv,
                'tag': self.tag,
                'doubleEncrypted': self.doubleEncrypted,
                'label': self.label,
                'sharedKey': self.sharedKey,
                'balance': self.balance,
                'watchOnly': self.watchOnly,
                'txs': [{'hash': tx.hash,
                         'timestamp': tx.timestamp,
                         'amount': tx.amount,
                         'address': tx.address,
                         'confirmations': tx.confirmations}
                        for tx in self.transactions],
                }


class AddressesModel(QAbstractListModel):
    COLUMNS = ('label', 'address', 'balance', 'index', 'prettyBalance')

    def __init__(self, ):
        self._addresses = []
        QAbstractListModel.__init__(self)
        self.setRoleNames(dict(enumerate(AddressesModel.COLUMNS)))

    def setData(self, data):
        self.beginResetModel()
        self._addresses[:] = data
        self._addresses.sort(key=lambda addr: addr.label)
        self.endResetModel()

    def rowCount(self, parent=QModelIndex()):
        return len(self._addresses)

    def data(self, index, role):
        if index.isValid() and role == AddressesModel.COLUMNS.index('label'):
            return self._addresses[index.row()].label
        elif (index.isValid() and role
              == AddressesModel.COLUMNS.index('address')):
            return self._addresses[index.row()].addr
        elif (index.isValid() and role
              == AddressesModel.COLUMNS.index('prettyBalance')):
            return prettyPBitcoin(self._addresses[index.row()].balance, True)
        elif (index.isValid() and role
              == AddressesModel.COLUMNS.index('balance')):
            return self._addresses[index.row()].balance
        elif (index.isValid() and role
              == AddressesModel.COLUMNS.index('index')):
            return index.row()
        return None


class TransactionsModel(QAbstractListModel):
    COLUMNS = ('date', 'address', 'amount', 'confirmations')

    def __init__(self, ):
        self._transactions = []
        QAbstractListModel.__init__(self)
        self.setRoleNames(dict(enumerate(TransactionsModel.COLUMNS)))

    def setData(self, transactions):
        self.beginResetModel()
        self._transactions[:] = transactions
        self._transactions.sort(key=lambda tx: tx.timestamp, reverse=True)
        self.endResetModel()

    def rowCount(self, parent=QModelIndex()):
        return len(self._transactions)

    def data(self, index, role):
        if index.isValid() and role == TransactionsModel.COLUMNS.index('date'):
            return self._transactions[index.row()].date
        elif (index.isValid() and role
              == TransactionsModel.COLUMNS.index('address')):
            return self._transactions[index.row()].address
        elif (index.isValid() and role
              == TransactionsModel.COLUMNS.index('amount')):
            return prettyPBitcoin(self._transactions[index.row()].amount, True)
        elif (index.isValid() and role
              == TransactionsModel.COLUMNS.index('confirmations')):
            return self._transactions[index.row()].confirmations
        return None


class TransactionHist(object):

    def __init__(self, txhash, timestamp, address, amount, confirmations):
        # QObject.__init__(self)
        self.hash = txhash

        self.timestamp = timestamp
        self.date = unicode(datetime.fromtimestamp(timestamp)
                            .strftime('%c'), 'utf-8')
        self.address = address
        self.amount = amount
        self.confirmations = confirmations
