import urllib2
import json


url = 'https://blockchain.info/wallet/wallet.aes.json?guid=3124d635-f3ce-a03e-aa10-45388dacd9a0&sharedKey=12345678-1234-1234-1234-123456789012'
req = urllib2.Request(url, None, {'user-agent':'KhtBitcoin'})
opener = urllib2.build_opener()
f = opener.open(req)
payload = f.read()      

#print payload
#payload = "FvNrY0dU5ybl9d76z3RHMRBYaxPyz2xVoFhoqlcmJeSAPmBvuIxSd5IbklVDBN1Bt72LNZdLqaMrSCK57l/1dS4DKXgt4cgCfM/fPE3r/BXnL8mbDRbcWiJXcW0uLHuoTIwYpA7rsqDu+rI2E+t4rXFD6NMJgQ2UZdvfzCrGHLA0OXcHxAfwgU+3oxjSLqU2QPpZUsoJ6mZLSjS4+zWs4XqlF14qZifVpbMQMxaAiIQDOgnQyRINlbhTir6DfwTAX34jHO0Q0xnqkwdhZbS8d3VC1FHXMqeVb2I/7RZNOjjCpGWjcP3482e/5lNAXtZlaId2N0IifusatpXYz0Ggaw=="
from PBKDF2 import PBKDF2
from Crypto.Cipher import AES
import os
cipherdata = payload.decode('base64', 'strict')
print len(cipherdata)
salt = os.urandom(8)   
iv = cipherdata[:16]     # 128-bit IV
key = PBKDF2(u"Ki0UZk|+cB", iv, iterations=10).read(32) # 256-bit key
cipher = AES.new(key, AES.MODE_CBC, iv)
data = cipher.decrypt(cipherdata[16:])
#pad = data.find('\0x01')
unpad = lambda s : s[0:-ord(s[-1])]
BS = 16
pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS) 
print unpad(data)
print data.encode('hex')  