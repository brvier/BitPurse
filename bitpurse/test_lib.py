#!/usr/bin/env python
#-*- coding:utf-8 -*-

import bitcoinrpc

conn = bitcoinrpc.connect_to_remote('3124d635-f3ce-a03e-aa10-45388dacd9a0',
                                    'Ki0UZk|+cB',
                                    host='blockchain.info', port=443,
                                    use_https=True)
print "Your balance is %f" % (conn.getbalance(),)
print "List account :"
print conn.listaccounts()
print "Received :"
print conn.listreceivedbyaddress()
print "Get address by account"
for account in conn.listaccounts():
    print conn.getaddressesbyaccount(account)
