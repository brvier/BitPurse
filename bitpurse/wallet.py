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
    Signal, Property
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
    getDataFromChainblock, b58decode, \
    padding, getAddrFromPrivateKey


class WrongPassword(Exception):
    pass


class DataError(Exception):
    pass


class Wallet(object):
    def __init__(self,):
        self.addresses = []
        self.balance = 0
        self.settings = Settings()

    def load_addresses(self, passKey):
        '''Load wallet from a json file
         {
            'keys':[{'addr':unicode,
                     'priv':unicode,
                     'label':unicode,
                     'doubleEncrypted': bool,
                     'sharedKey'},]
            'wallet': {'balance': int}
         }'''

        with open(
            os.path.join(os.path.expanduser('~'),
                         '.bitpurse.wallet'), 'rb') as fh:
            payload = fh.read()

            payload = json.loads(self.decrypt(passKey,
                                 payload.decode('base64', 'strict')))
            self.settings.passKey = passKey
            self.addresses = [Address(jsondict=address)
                              for address in payload['keys']]

            self.balance = payload['balance']

    def store(self, passKey):
        '''Store wallet in a json file'''
        jsondict = json.dumps({'keys': [address.__repr__()
                                        for address in self.addresses],
                               'balance': self.balance})

        payload = self.encrypt(passKey,
                               jsondict).encode('base64', 'strict')

        with open(
            os.path.join(os.path.expanduser('~'),
                         '.bitpurse.wallet'), 'wb') as fh:
            fh.write(payload)

    def getIndex(self, addr):
        for idx, address in enumerate(self.addresses):
            if address.addr == addr:
                return idx
        return -1

    def encrypt(self, key, cipherdata):
        iv = os.urandom(16)
        cipherdata = padding(cipherdata)
        key = PBKDF2(key, iv, iterations=10).read(32)

        cipher = AES.new(key, AES.MODE_CBC, iv)
        return iv + cipher.encrypt(cipherdata)

    def decrypt(self, key, cipherdata):
        ''' Decrypt an wallet encrypted with a PBKDF2 Key with AES'''
        key = PBKDF2(key, cipherdata[:16], iterations=10).read(32)
        cipher = AES.new(key, AES.MODE_CBC, cipherdata[:16])
        return unpadding(cipher.decrypt(cipherdata[16:]))

    def decryptPK(self, data, password, sharedKey):
        ''' Decrypt an double encrypted private key'''
        data = data.decode('base64', 'strict')
        key = PBKDF2(sharedKey + password, data[:16], iterations=10).read(32)
        cipher = AES.new(key, AES.MODE_CBC, data[:16])
        return unpadding(cipher.decrypt(data[16:]))

    def exportToBlockchainInfoWallet(self, guid, key):
        '''Export wallet to BlockChain.info MyWallet services'''
        #TODO
        pass

    def importFromPrivateKey(self, passKey, privateKey):

        privateKey = privateKey.strip('\n')

        bc = getAddrFromPrivateKey(privateKey)

        addr = Address()
        addr.addr = bc
        addr.priv = privateKey
        self.addresses.append(addr)
        self.store(passKey)

    def importFromBlockchainInfoWallet(self, passKey, guid, key, skey):
        '''Import wallet from BlockChain.info MyWallet services'''
        req = urllib2.Request('https://blockchain.info/wallet/'
                              + '%s?format=json&resend_code=false' %
                              (guid),
                              None, {'user-agent': 'BitPurse'})
        opener = urllib2.build_opener()
        fh = opener.open(req)
        encryptedWallet = json.loads(fh.read())['payload']
        #print encryptedWallet

        try:
            data = self.decrypt(key,
                                encryptedWallet.decode('base64', 'strict'))
        except:
            raise WrongPassword('Unknow login')

        try:
            data = json.loads(data)
        except:
            raise WrongPassword('Incorrect password')

        if 'double_encryption' in data:
            isDoubleEncrypted = bool(data['double_encryption'])
        else:
            isDoubleEncrypted = False

        if 'sharedKey' in data:
            sharedKey = data['sharedKey']
        else:
            sharedKey = None

        for address in data['keys']:
            if not self.isMine(address['addr']):
                address['sharedKey'] = sharedKey
                address['doubleEncrypted'] = isDoubleEncrypted
                if 'tag' not in address:
                    address['tag'] = 0

                if isDoubleEncrypted:
                    address['priv'] = self.decryptPK(address['priv'],
                                                     skey, sharedKey)
                    address['doubleEncrypted'] = False
                self.addresses.append(Address(jsondict=address))

        print 'Importing Blockchain.info MyWallet'
        self.store(passKey)

    def addTransactionHistForAddress(self, addr, transaction):
        for address in self.addresses:
            if addr == address.addr:
                for tx in address.transactions:
                    if tx.hash == transaction.hash:
                        tx.confirmations = transaction.confirmations
                        tx.amount = transaction.amount
                        tx.date = transaction.date
                        return
                address.transactions.append(transaction)
                return

    def getPrivKeyForAddress(self, addr, secondPassword=None):
        '''Return private key for an address'''
        for address in self.addresses:
            if addr == address.addr:
                if address.doubleEncrypted:
                    if not secondPassword:
                        raise WrongPassword('You must provide a'
                                            ' second password for double'
                                            ' encrypted wallet')
                    try:
                        uncryptedKey = self.decryptPK(
                            address.priv,
                            secondPassword,
                            self.sharedKey)
                        if len(b58decode(uncryptedKey, None)) not in (32, 33):
                            raise WrongPassword('Wrong second password')
                        return uncryptedKey
                    except:
                        import traceback
                        traceback.print_exc()
                        raise

                else:
                    return address.priv

    def getActiveAddrAddresses(self,):
        return [address.addr for address in self.addresses if address.tag == 0]

    def getArchivedAddrAddresses(self,):
        return [address.addr for address in self.addresses if address.tag == 2]

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

    def load_txs_from_blockchain(self,):
        req = ('https://blockchain.info/multiaddr'
               + '?format=json&filter=0&offset=0'
               + '&active=%s&archived=%s'
               % ('|'.join(self.getActiveAddrAddresses()),
               '|'.join(self.getArchivedAddrAddresses())))

        data = getDataFromChainblock(req)

        try:
            self.balance = data['wallet']['final_balance']
        except KeyError:
            print 'Final balance not in the json data'

        try:
            for address in data['addresses']:
                try:
                    for addr in self.addresses:
                        if address['address'] == addr.addr:
                            addr.balance = address['final_balance']
                except KeyError, err:
                    print err
        except KeyError:
            print 'None address in json data'

        try:
            for tx in data['txs']:
                try:
                    txAddresses = {}
                    txDst = []
                    confirmations = 0
                    if 'block_height' in tx:
                        confirmations = \
                            data['info']['latest_block']['height'] \
                            - tx['block_height'] + 1
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
                                tx['time'],
                                '\n'.join(list(set(txDst)
                                .difference([txAddress, ]))),
                                txAddresses[txAddress], confirmations))

                except KeyError, err:
                    print err
        except KeyError:
            print 'None tx in json data'

    def update(self, passKey):
        try:
            #self.getRemoteWallet(login, privkey)
            self.load_txs_from_blockchain()
            self.store(passKey)
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
    onWalletUnlocked = Signal()
    onCurrentBalance = Signal()
    onCurrentLabel = Signal()
    onCurrentAddress = Signal()
    onCurrentDoubleEncrypted = Signal()
    onCurrentPassKey = Signal()

    def __init__(self,):
        QObject.__init__(self,)
        self.thread = None
        self._wallet = Wallet()
        self._walletUnlocked = False
        self.settings = Settings()
        self.addressesModel = AddressesModel()
        self.transactionsModel = TransactionsModel()

        if self.settings.storePassKey:
            self._currentPassKey = self.settings.passKey
            try:
                self.unlockWallet(self._currentPassKey)
            except:
                self.onError.emit('Stored pass phrase is invalid')
        else:
            self._currentPassKey = None
        self._balance = '<b>0.00</b>000000'
        self._currentAddressIndex = 0

    @Slot(result=bool)
    def walletExists(self,):
        if not os.path.exists(os.path.join(
                os.path.expanduser('~'),
                '.bitpurse.wallet')):
            return False
        return True

    @Slot(unicode)
    def createWallet(self, passKey):
        self._currentPassKey = passKey
        self._wallet.store(passKey)

    def getCurrentPassKey(self):
        return self._currentPassKey

    def setCurrentPassKey(self, value):
        self._currentPassKey = value
        self.onCurrentPassKey.emit()

    def getCurrentBalance(self):
        try:
            return prettyPBitcoin(self._wallet.addresses[
                self._currentAddressIndex].balance)
        except IndexError:
            return prettyPBitcoin(0)

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

    def getCurrentDoubleEncrypted(self):
        try:
            return self._wallet.addresses[self._currentAddressIndex] \
                .doubleEncrypted
        except IndexError:
            return False

    @Slot(unicode, unicode, unicode)
    def importFromBlockchainInfoWallet(self, guid, key, skey):
        if self.thread:
            if self.thread.isAlive():
                self.onError.emit(
                    u'Please wait, a communication is already in progress')
        self.thread = threading.Thread(None,
                                       self._importFromBlockchainInfoWallet,
                                       None, (guid, key, skey))
        self.thread.start()

    @Slot(unicode)
    def importFromPrivateKey(self, privateKey):
        try:
            self._wallet.importFromPrivateKey(self._currentPassKey, privateKey)
            self.update()
        except Exception, err:
            print err
            import traceback
            traceback.print_exc()
            self.onError.emit(unicode(err))

    def _importFromBlockchainInfoWallet(self, guid, key, skey):
        self.onBusy.emit()
        try:
            self._wallet.importFromBlockchainInfoWallet(self._currentPassKey,
                                                        guid, key, skey)
            self._update()
        except Exception, err:
            print err
            import traceback
            traceback.print_exc()
            self.onError.emit(unicode(err))
        self.onBusy.emit()

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
            self.update()

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
            self._wallet.load_addresses(self._currentPassKey)
            self._walletUnlocked = True
            self.addressesModel.setData(self._wallet.getActiveAddresses())

        except Exception, err:
            self.onError.emit(unicode(err))
            import traceback
            traceback.print_exc()
            return False
        return True

    @Slot()
    def update(self,):
        if self.thread:
            if self.thread.isAlive():
                return
        self.thread = threading.Thread(None, self._update, None, ())
        self.thread.start()

    def _update(self,):
        self.onBusy.emit()
        try:
            self._wallet.update(self._currentPassKey)
            self._balance = prettyPBitcoin(self._wallet.balance)
            self.onBalance.emit()
            #print self._wallet.getActiveAddresses()
            self.addressesModel.setData(self._wallet.getActiveAddresses())
            try:
                self.transactionsModel.setData(
                    self._wallet.addresses[self._currentAddressIndex]
                    .transactions)
            except IndexError:
                print 'index error loading transactions model'
            #self.onDoubleEncrypted.emit()
            #self.onConnected.emit(True)
            #self.setDefaultAddress()
        except urllib2.URLError:
            pass
        except Exception, err:
            print err
            self.onError.emit(unicode(err))
        self.onBusy.emit()

    @Slot(unicode)
    def setCurrentAddress(self, addr):
            self._currentAddressIndex = self._wallet.getIndex(addr)
            self.onCurrentBalance.emit()
            self.onCurrentLabel.emit()
            self.onCurrentAddress.emit()
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

    def getWalletUnlocked(self):
        return self._walletUnlocked

    currentDoubleEncrypted = Property(bool, getCurrentDoubleEncrypted,
                                      notify=onCurrentDoubleEncrypted)
    busy = Property(bool, isBusy,
                    notify=onBusy)
    walletUnlocked = Property(bool, getWalletUnlocked,
                              notify=onWalletUnlocked)
    balance = Property(unicode, getBalance, notify=onBalance)
    currentBalance = Property(unicode,
                              getCurrentBalance,
                              notify=onCurrentBalance)
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