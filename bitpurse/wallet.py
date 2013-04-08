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


class WrongPassword(Exception):
    pass


class DataError(Exception):
    pass


class Wallet(object):
    def __init__(self,):
        self.addresses = []
        self.balance = 0
        self.settings = Settings()

    def createAddr(self, doubleKey):
        if doubleKey:
            self.testDoublePK(doubleKey)

        # eckey = EC_KEY(int(os.urandom(32).encode('hex'), 16))
        pk = EC_KEY(int(os.urandom(32).encode('hex'), 16))
        addr = Address()
        addr.priv = SecretToASecret(getSecret(pk), True)
        addr.addr = getAddrFromPrivateKey(addr.priv)
        addr.sharedKey = 'BitPurse'
        if doubleKey:
            addr.priv = self.encryptPK(addr.priv, doubleKey, addr.sharedKey)
            addr.doubleEncrypted = True

        self.addresses.append(addr)

    def load_addresses(self, passKey):
        '''Load wallet from a json file
         {
            'keys':[{'addr':unicode,
                     'priv':unicode,
                     'label':unicode,
                     'doubleEncrypted': bool,
                     'sharedKey':unicode},
                     'tag':int,
                     'balance':int,
                     'txs:[],]
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

    def encryptPK(self, data, password, sharedKey):
        iv = os.urandom(16)
        data = padding(data)
        key = PBKDF2(sharedKey + password, iv, iterations=10).read(32)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        return (iv + cipher.encrypt(data)).encode('base64')

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

    def doubleEncryptPrivKeys(self, secondPass):
        if any([addr.doubleEncrypted is True for addr in self.addresses
                if not addr.watchOnly]):
            raise DataError('Some keys are already double encrypted')
        for addr in [address for address in self.addresses
                     if not address.watchOnly]:
            oldpk = addr.priv
            if addr.sharedKey is None:
                addr.sharedKey = 'BitPurse'
            addr.priv = self.encryptPK(addr.priv, secondPass,
                                       addr.sharedKey)
            addr.doubleEncrypted = True
            assert oldpk == self.decryptPK(addr.priv, secondPass,
                                           addr.sharedKey)
            QApplication.processEvents()
        self.settings.useDoubleEncryption = False

    def testDoublePK(self, secondPass):
        # Test if password match at least for the first key
        addresses = [address for address in self.addresses
                     if not address.watchOnly]
        if len(addresses) < 1:
            return

        try:
            if (getAddrFromPrivateKey(self.decryptPK(addresses[0]
                                                     .priv,
                                                     secondPass,
                                                     addresses[0]
                                                     .sharedKey))
                    != addresses[0].addr):
                raise DataError('Double Password didn\'t match '
                                'with other keys')
        except:
            raise DataError('Double Password didn\'t match with other keys')

    def doubleDecryptPrivKeys(self, secondPass):
        if any([addr.doubleEncrypted is False for addr in self.addresses
                if not addr.watchOnly]):
            raise DataError('Some keys are not double encrypted')

        self.testDoublePK(secondPass)

        for addr in [address for address in self.addresses
                     if not address.watchOnly]:
            if addr.sharedKey is None:
                addr.sharedKey = 'BitPurse'
            addr.priv = self.decryptPK(addr.priv, secondPass,
                                       addr.sharedKey)
            addr.doubleEncrypted = False
            assert addr.addr == getAddrFromPrivateKey(addr.priv)
            QApplication.processEvents()
        self.settings.useDoubleEncryption = True

    def exportToBlockchainInfoWallet(self, guid, key):
        '''Export wallet to BlockChain.info MyWallet services'''
        # TODO
        pass

    def exportDecryptedAsText(self, secondPass):
        if secondPass:
            self.testDoublePK(secondPass)

        txt = ('Uncrypted wallet export\n'
               '-----------------------\n\n')
        for addr in self.addresses:
            txt += 'Label: %s\n' % addr.label
            txt += 'Address: %s\n' % addr.addr
            if addr.doubleEncrypted:
                pk = self.decryptPK(addr.priv, secondPass,
                                    addr.sharedKey)
            else:
                pk = addr.priv
            if not addr.watchOnly:
                txt += 'Private Key: %s\n\n' % pk
            else:
                txt += 'Watch only\n\n'

        return txt

    def importWatchOnly(self, passKey, address, label='Undefined'):
        addr = Address()
        addr.addr = address
        addr.sharedKey = 'BitPurse'
        addr.watchOnly = True
        addr.priv = ''
        addr.label = label

        self.addresses.append(addr)
        self.store(passKey)

    def importFromPrivateKey(self, passKey, privateKey,
                             label='Undefined', doubleKey=''):

        # Test if password match at least for the first key
        if doubleKey:
            self.testDoublePK(doubleKey)

        privateKey = privateKey.strip('\n')
        bc = getAddrFromPrivateKey(privateKey)
        if bc in self.getAddrAddresses():
            raise DataError('This private key is already in the wallet')

        addr = Address()
        addr.addr = bc
        addr.sharedKey = 'BitPurse'
        if doubleKey:
            privateKey = self.encryptPK(privateKey, doubleKey, addr.sharedKey)
            addr.doubleEncrypted = True
        addr.priv = privateKey
        addr.label = label

        self.addresses.append(addr)
        self.store(passKey)

    def importFromBlockchainInfoWallet(self, passKey, guid, key,
                                       skey, doubleKey=''):
        '''Import wallet from BlockChain.info MyWallet services'''

        # Test if password match at least for the first key
        if doubleKey:
            self.testDoublePK(doubleKey)

        req = 'https://blockchain.info/wallet/' \
              + '%s?format=json&resend_code=false' % (guid)

        # opener = urllib2.build_opener()
        # fh = opener.open(req)
        # encryptedWallet = json.loads(fh.read())['payload']
        encryptedWallet = getDataFromChainblock(req)['payload']

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
            sharedKey = 'BitPurse'

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
                    if doubleKey:
                        address['priv'] = self.encryptPK(address['priv'],
                                                         doubleKey,
                                                         address['sharedKey'])
                        address['doubleEncrypted'] = True

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
                            address.sharedKey)
                        try:
                            if getAddrFromPrivateKey(uncryptedKey) \
                                    != address.addr:
                                raise WrongPassword('Wrong second password')
                        except:
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

    @Slot(unicode)
    def remove(self, addr):
        del self.addresses[self.getIndex(addr)]

    @Slot(unicode)
    def getLabelForAddr(self, addr):
        return self.addresses[self.getIndex(addr)].label

    @Slot(unicode, unicode)
    def setLabelForAddr(self, addr, label):
        self.addresses[self.getIndex(addr)].label = label

    def update(self, passKey):
        try:
            # self.getRemoteWallet(login, privkey)
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
            self._update()
        except Exception, err:
            print err
            import traceback
            traceback.print_exc()
            self.onError.emit(unicode(err))
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
            try:
                self._wallet.load_addresses(self._currentPassKey)
            except ValueError:
                raise WrongPassword('Wrong passphrase')
            self._updateFiat()
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
