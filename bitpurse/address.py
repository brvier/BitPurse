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

from PySide.QtCore import QAbstractListModel, QModelIndex
from utils import prettyPBitcoin


class Address(object):

    def __init__(self, jsondict={}):
        #QObject.__init__(self,)
        self.addr = ''
        self.label = 'Undefined'
        self.priv = ''
        self.balance = 0
        self.tag = 0
        self.transactions = []

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


class AddressesModel(QAbstractListModel):
    COLUMNS = ('label', 'address', 'balance', 'index', 'prettyBalance')

    def __init__(self, ):
        self._addresses = {}
        QAbstractListModel.__init__(self)
        self.setRoleNames(dict(enumerate(AddressesModel.COLUMNS)))

    def clearData(self, ):
        self._addresses = {}

    def setData(self, data):
        self.beginResetModel()
        self._addresses = data
        self.endResetModel

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
            return index
        return None


class TransactionsModel(QAbstractListModel):
    COLUMNS = ('date', 'address', 'amount')

    def __init__(self, ):
        self._transactions = []
        QAbstractListModel.__init__(self)
        self.setRoleNames(dict(enumerate(TransactionsModel.COLUMNS)))

    def resetData(self, ):
        self._transactions = []

    def setTransactions(self, transactions):
        self.beginResetModel()
        self._transactions = transactions
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
        return None


class TransactionHist(object):
    def __init__(self, txhash, date, address, amount):
        #QObject.__init__(self)
        self.date = date
        self.address = address
        self.amount = amount
