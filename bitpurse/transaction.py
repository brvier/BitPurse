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
    filter, getPubKeyFromPrivateKey, \
    HTTPSHandlerV3

import urllib
import urllib2
import re
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

        if not self.pushTx():
            raise TransactionError("An error occur while sending transaction")
        else:
            raise TransactionSubmitted("Transaction successfully transmitted")

    def reverse_hash(self, rhash):
        return "".join(reversed([rhash[i: i + 2]
                                 for i in range(0, len(rhash), 2)]))

    def pushTx(self):
        url = 'https://blockchain.info/pushtx'
        body = urllib.urlencode({'tx': self.tx})
        req = urllib2.Request(url,
                              body,
                              {'user-agent': 'BitPurse',
                               'Content-Type':
                               'application/x-www-form-urlencoded',
                               'Accept': 'application/json'})
        opener = urllib2.build_opener(HTTPSHandlerV3)
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
                           [(None,
                           None)]))
        return inputs

    def signed_tx(self, inputs, outputs, privKey):
        s_inputs = self.sign_inputs(inputs, outputs, privKey)
        tx = filter(self.raw_tx(s_inputs, outputs))
        return tx

    def sign_inputs(self, inputs, outputs, privKey):
        s_inputs = []
        for i in range(len(inputs)):
            addr, v, p_hash, p_pos, p_scriptPubKey, _ = inputs[i]
            secexp = getSecretFromPrivateKey(privKey)
            private_key = \
                ecdsa.SigningKey.from_secret_exponent(secexp,
                                                      curve=SECP256k1)
            public_key = private_key.get_verifying_key()
            pubkey = getPubKeyFromPrivateKey(privKey)
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
                             [(pubkey,
                             sig)]))
        return s_inputs

    def tx_filter(self, s):
        out = re.sub('( [^\n]*|)\n', '', s)
        out = out.replace(' ', '')
        out = out.replace('\n', '')
        return out

    #def get_private_key(self, key):
    #    """  Privatekey(type,n) = Master_private_key + H(n|S|type)  """
    #    return b58decode(key)

    # https://en.bitcoin.it/wiki/Protocol_specification#Variable_length_integer
    def raw_tx(self, inputs, outputs, for_sig=None):
        s = int_to_hex(1, 4)                                 # version
        s += var_int(len(inputs))                            # number of inputs
        for i in range(len(inputs)):
            _, _, p_hash, p_index, p_script, pubkeysig = inputs[i]
            s += p_hash.decode('hex')[::-1].encode('hex')    # prev hash
            s += int_to_hex(p_index, 4)                    # prev index

            if for_sig is None:
                if len(pubkeysig) == 1:
                    pubkey, sig = pubkeysig[0]
                    sig = sig + chr(1)                               # hashtype
                    script = int_to_hex(len(sig))
                    script += sig.encode('hex')
                    script += int_to_hex(len(pubkey))
                    script += pubkey.encode('hex')
                else:
                    pubkey0, sig0 = pubkeysig[0]
                    pubkey1, sig1 = pubkeysig[1]
                    sig0 = sig0 + chr(1)
                    sig1 = sig1 + chr(1)
                    inner_script = self.multisig_script([pubkey0, pubkey1])
                    script = '00'                                    # op_0
                    script += int_to_hex(len(sig0))
                    script += sig0.encode('hex')
                    script += int_to_hex(len(sig1))
                    script += sig1.encode('hex')
                    script += var_int(len(inner_script) / 2)
                    script += inner_script

            elif for_sig == i:
                if len(pubkeysig) > 1:
                    script = self.multisig_script(pubkeysig)  # p2sh uses the
                                                              # inner script
                else:
                    script = p_script                         # scriptsig
            else:
                script = ''
            s += var_int(len(self.tx_filter(script)) / 2)    # script length
            s += script
            s += "ffffffff"                                   # sequence

        s += var_int(len(outputs))                      # number of outputs
        for output in outputs:
            addr, amount = output
            s += int_to_hex(amount, 8)                              # amount
            addrtype, hash_160 = bc_address_to_hash_160(addr)
            if addrtype == 0:
                script = '76a9'                         # op_dup, op_hash_160
                script += '14'                          # push 0x14 bytes
                script += hash_160.encode('hex')
                script += '88ac'                 # op_equalverify, op_checksig
            elif addrtype == 5:
                script = 'a9'                           # op_hash_160
                script += '14'                          # push 0x14 bytes
                script += hash_160.encode('hex')
                script += '87'                          # op_equal
            else:
                raise

            s += var_int(len(self.tx_filter(script)) / 2)  # script length
            s += script                                    # script
        s += int_to_hex(0, 4)                               # lock time
        if for_sig is not None:
            s += int_to_hex(1, 4)      # hash type
        return self.tx_filter(s)

    def multisig_script(self, public_keys):
        # supports only "2 of 2", and "2 of 3" transactions
        n = len(public_keys)
        s = '52'
        for k in public_keys:
            s += var_int(len(k) / 2)
            s += k
        if n == 2:
            s += '52'
        elif n == 3:
            s += '53'
        else:
            raise
        s += 'ae'
        return s
