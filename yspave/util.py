from __future__ import print_function
from . import pave
from colorama import Fore as fg
import sys, scrypt, binascii, colorama, base64, readline
PY2 = sys.version_info < (3, 0, 0, 'final', 0)

def print_table (ls,pretty=False):
	c = max (map (len, ls))
	csz = [max(map(lambda y:len(str(y)), [l[x] for l in ls])) for x in range(c)]
	if pretty: print (fg.BLUE,end='')
	for l in ls:
		print(''.join([str(l[i]).ljust(csz[i]+4)for i in range(c)]).rstrip()+fg.RESET)

def prompt (ps1='', default=''):
	if default: readline.add_history (default)
	i = raw_input(ps1) if PY2 else input (ps1)
	return i if i else default

def s (d):
	if (not PY2 and isinstance (d, str))\
	    or (PY2 and isinstance (d, unicode)):
		return d.encode (pave.database_encoding)
	return d

def mkhash (data, salt): return tohex (scrypt.hash(s(data), s(salt)))
def tohex (data):        return binascii.hexlify (data).decode('ascii')
def fromhex (data):      return binascii.unhexlify (data)

def to64 (data):         return base64.b64encode(data).decode('ascii')
def from64 (data):       return base64.b64decode(data)


def pick (db, query):
	items = sorted (db.finditems (query, True), key=lambda x:x[0])

	if not items:
		print (fg.RED+'No matches found!'+fg.RESET)
		return None

	if len (items) == 1:
		return items[0]

	headings = [['ID', 'Title', 'Details']]
	headings.extend ((i[:2] + (i[3],) for i in items))
	print_table (headings, True)

	while True:
		idchoice = prompt ('Enter an item ID:\n> ')
		for i in items:
			if i[0] == idchoice:
				return i
		print (fg.RED+'ID not found.'+fg.RESET)

