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
## GNU General Public License


from utils import \
    is_valid, int_to_hex, bc_address_to_hash_160, var_int, \
    getDataFromChainblock, Hash, \
    SECP256k1, getSecretFromPrivateKey, \
    filter

import urllib
import urllib2

import ecdsa


class TransactionError(Exception):
    pass


class TransactionSubmitted(Exception):
    pass


class Transaction(object):
    def __init__(self, from_addr, outputs, privKey, fee=None,
                 change_addr=None):
        if not change_addr:
            change_addr = from_addr
        if fee is None:
            fee = 100
        for address, value in outputs:
            assert is_valid(address)

        amount = sum(map(lambda x: x[1], outputs))
        inputs = self.getInputs(from_addr)
        total = sum(map(lambda x: x[1], inputs))
        change_amount = total - (amount + fee)

        print 'Change:', change_amount
        print 'Total:', total
        print 'Amount:', amount

        if change_amount < 0:
            raise TransactionError('Not enought funds, or transaction using'
                                   ' all inputs need to be confirmed')

        if amount < 1000000 and fee < 50000:
            raise TransactionError("Not enought fee :"
                                   " a fee of 0.0005 is required for"
                                   " small transactions")

        outputs.append((change_addr, change_amount))

        self.tx = self.signed_tx(inputs, outputs, privKey)

        print self.tx

        #Broken do not push
        #if not self.pushTx():
        #    raise TransactionError("An error occur while sending transaction")
        #else:
        #    raise TransactionSubmitted("Transaction successfully transmitted")

    def reverse_hash(self, rhash):
        return "".join(reversed([rhash[i: i + 2]
                                 for i in range(0, len(rhash), 2)]))

    def pushTx(self):
        url = 'https://blockchain.info/pushtx'
        body = urllib.urlencode({'tx': self.tx})
        req = urllib2.Request(url,
                              body,
                              {'user-agent': 'KhtBitcoin',
                               'Content-Type':
                               'application/x-www-form-urlencoded',
                               'Accept': 'application/json'})
        opener = urllib2.build_opener()
        fh = opener.open(req)
        result = fh.read()
        if unicode(result.strip()) == u'Transaction Submitted':
            return True
        else:
            print type(result), result
        return False

    def getInputs(self, addr):
        inputs = []
        request = 'http://blockchain.info/unspent?address=%s' % addr
        for unspent in getDataFromChainblock(request)['unspent_outputs']:
            inputs.append((addr,
                           unspent['value'],
                           self.reverse_hash(unspent['tx_hash']),
                           unspent['tx_output_n'],
                           unspent['script'],
                           None,
                           None))
        return inputs

    def signed_tx(self, inputs, outputs, privKey):
        s_inputs = self.sign_inputs(inputs, outputs, privKey)
        tx = filter(self.raw_tx(s_inputs, outputs))
        return tx

    def sign_inputs(self, inputs, outputs, privKey):
        s_inputs = []
        for i in range(len(inputs)):
            addr, v, p_hash, p_pos, p_scriptPubKey, _, _ = inputs[i]
            print 'privKey:', privKey
            secexp = getSecretFromPrivateKey(privKey)
            private_key = \
                ecdsa.SigningKey.from_secret_exponent(secexp,
                                                      curve=SECP256k1)
            public_key = private_key.get_verifying_key()
            pubkey = public_key.to_string()
            tx = filter(self.raw_tx(inputs, outputs, for_sig=i))
            sig = private_key.sign_digest(Hash(tx.decode('hex')),
                                          sigencode=ecdsa.util.sigencode_der)
            assert public_key.verify_digest(sig,
                                            Hash(tx.decode('hex')),
                                            sigdecode=ecdsa.util.sigdecode_der)
            s_inputs.append((addr,
                             v,
                             p_hash,
                             p_pos,
                             p_scriptPubKey,
                             pubkey,
                             sig))
        return s_inputs

    #def get_private_key(self, key):
    #    """  Privatekey(type,n) = Master_private_key + H(n|S|type)  """
    #    return b58decode(key)

    # https://en.bitcoin.it/wiki/Protocol_specification#Variable_length_integer
    def raw_tx(self, inputs, outputs, for_sig=None):
        s = int_to_hex(1, 4) + ' version\n'
        s += var_int(len(inputs)) + ' number of inputs\n'
        for i in range(len(inputs)):
            _, _, p_hash, p_index, p_script, pubkey, sig = inputs[i]
            s += p_hash.decode('hex')[::-1].encode('hex') + ' prev hash\n'
            s += int_to_hex(p_index, 4) + ' prev index\n'
            if for_sig is None:
                sig = sig + chr(1)  # hashtype
                script = int_to_hex(len(sig)) + ' push %d bytes\n' % len(sig)
                script += sig.encode('hex') + ' sig\n'
                pubkey = chr(4) + pubkey
                script += int_to_hex(len(pubkey))
                script += ' push %d bytes\n' % len(pubkey)
                script += pubkey.encode('hex') + ' pubkey\n'
            elif for_sig == i:
                script = p_script + ' scriptsig \n'
            else:
                script = ''
            s += var_int(len(filter(script)) / 2) + ' script length \n'
            s += script
            s += "ffffffff" + ' sequence\n'
        s += var_int(len(outputs)) + ' number of outputs\n'
        for output in outputs:
            addr, amount = output
            s += int_to_hex(amount, 8) + ' amount: %d\n' % amount
            script = '76a9'  # op_dup, op_hash_160
            script += '14'  # push 0x14 bytes
            script += bc_address_to_hash_160(addr).encode('hex')
            script += '88ac'  # op_equalverify, op_checksig
            s += var_int(len(filter(script)) / 2) + ' script length \n'
            s += script + ' script \n'
        s += int_to_hex(0, 4)  # lock time
        if for_sig is not None:
            s += int_to_hex(1, 4)   # hash type
        return s
