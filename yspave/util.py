from __future__ import print_function
from . import pave
from colorama import Fore as fg
import sys, scrypt, binascii, colorama, base64
PY2 = sys.version_info < (3, 0, 0, 'final', 0)

def print_table (ls,pretty=False):
	c = max (map (len, ls))
	csz = [max(map(lambda y:len(str(y)), [l[x] for l in ls])) for x in range(c)]
	if pretty: print (fg.BLUE,end='')
	for l in ls:
		print(''.join([str(l[i]).ljust(csz[i]+4)for i in range(c)]).rstrip()+fg.RESET)

def prompt (ps1=''):
	return raw_input(ps1) if PY2 else input (ps1)

def s (d):
	if (not PY2 and isinstance (d, str))\
	    or (PY2 and isinstance (d, unicode)):
		return d.encode (pave.database_encoding)
	return d

def mkhash (data, salt): return tohex (scrypt.hash(s(data), s(salt)))
def tohex (data):        return binascii.hexlify (data).decode('ascii')
def fromhex (data):      return binascii.unhexlify (data)

def to64 (data):         return base64.b64encode(data)
def from64 (data):       return base64.b64decode(data)
