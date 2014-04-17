from . import pave
import sys, scrypt, binascii
PY2 = sys.version_info < (3, 0, 0, 'final', 0)

def print_table (ls):
	c = max (map (len, ls))
	csz = [max(map(lambda y:len(str(y)), [l[x] for l in ls])) for x in range(c)]
	for l in ls:
		print ("".join([str(l[i]).ljust(csz[i]+4) for i in range(c)]).rstrip())

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


if __name__=='__main__':
	testcase = [
		["foo"*2, "baz", "basdfdsfdsfdsfdsfds"],
		["foobarfoo","batbatbat", "asd"]]
	table = [["", "taste", "land speed", "life"],
		["spam", 300101, 4, 1003],
		["eggs", 105, 13, 42],
		["lumberjacks", 13, 105, 10]]
	print_table (testcase)
	print ()
	print_table (table)

