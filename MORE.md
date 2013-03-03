Implementations details
=======================

Wallet
------

Wallet is stored locally in a json file in ~/.bitpurse.wallet

~~~~
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
}
~~~~

Wallet is always stored encrypted.

Encryption
----------
The encryption is made with pycrypto and PBKDF2 python module. It use PBKDF2 to generate the key from password and AES CBC.

Blockchain
----------
As many phone isp block p2p i choose to not implement a full bitcoin client but use blockchain.info api to avoid loading and storing the blockchain (which actually have a size of 4.5Gb).

Wallet balance, address balance and last transactions by address informations are provided by blockchain.info
Transaction are also broadcasted by blockchain.info.

Your private keys is never shared with any services, except if you choose to export your wallet, but even in this case the export is encrypted.

Security
--------

If you use the encryption and didn't want to enter your password each time you load BitPurse, you can use double encryption, your wallet will be stored encrypted, but will be decrypted in memory at startup. With double encryption the private key remains crypted, so without knowing second password, noone can use your phone to emit transactions.    