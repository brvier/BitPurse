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

from PySide.QtCore import Signal, QObject
from PySide.QtGui import QApplication
import json
from PBKDF2 import PBKDF2
from Crypto.Cipher import AES
import os.path

from address import Address, TransactionHist
from settings import Settings

from utils import unpadding, \
    getDataFromChainblock, \
    padding, getAddrFromPrivateKey, \
    EC_KEY, getSecret, \
    SecretToASecret


class WrongPassword(Exception):
    pass


class DataError(Exception):
    pass


class Wallet(QObject):
    onNewTransaction = Signal(str, str, int)

    def __init__(self,):
        QObject.__init__(self)
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
                                              payload.decode('base64',
                                                             'strict')))
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
                self.onNewTransaction.emit(
                    addr, transaction.address, transaction.amount)
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

    def remove(self, addr):
        del self.addresses[self.getIndex(addr)]

    def getLabelForAddr(self, addr):
        return self.addresses[self.getIndex(addr)].label

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
