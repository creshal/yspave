from Crypto.Hash import SHA256 as hashfn
from scrypt import encrypt, decrypt
from json import dumps,loads
from . import pave
import binascii, os, Crypto.Random, base64,time,sys

BLKSIZE=32

def mkhash (data):
	if type(data) is not bytes: data=data.encode (pave.database_encoding)
	return hashfn.new(data).digest()

def tohex (data): return binascii.hexlify (data).decode('ascii')
def fromhex (data): return binascii.unhexlify (data)

def enc (data,password,complexity):
	if type (data) is not bytes:
		data = data.encode (pave.database_encoding)
	return tohex(encrypt(data,password,maxtime=complexity, maxmem=int(complexity*pave.memory_factor)))

def dec (data,password):
	return decrypt(fromhex(data),password)

class PaveDB ():
	def __init__ (self, key=None, keyfile=None, database=pave.default_db_filename):
		self.rng = Crypto.Random.new()
		if not any ([key,keyfile]):
			raise KeyError ('Neither password nor password file supplied, aborting.')

		if key: self.key = mkhash (key)
		elif keyfile:
			with open (keyfile) as f:
				self.key = mkhash (f.read())

		self.dbfile = database
		if not os.path.exists (self.dbfile):
			print ('Creating new database `%s`...'%self.dbfile)
			self.db = {
				'version': pave.database_version,
				'db_key': tohex (mkhash (self.rng.read(BLKSIZE))),
				'keys': {}
			}
		else:
			with open (self.dbfile) as f:
				self.db = loads (dec (f.read(), self.key))
			if not 'version' in self.db or self.db['version'] > pave.database_version:
				raise Exception ('Unknown database format')
		self.dbkey = fromhex (self.db['db_key'])


	def syncdb (self):
		umask = False if os.path.exists (self.dbfile) else os.umask (0o7077)
		with open (self.dbfile,'w') as f:
			f.write (enc(dumps(self.db),self.key,pave.database_complexity))
		if umask: os.umask (umask)


	def delitem (self, key):
		del self.db['keys'][key]

	def additem (self, title, password, details=''):
		key = sorted(map (int,self.db['keys']))[-1]+1 if self.db['keys'] else 0
		value = {
			'Title': enc (title, self.dbkey, pave.metadate_complexity),
			'Password': enc (password, self.dbkey, pave.password_complexity),
			'Details': enc (details, self.dbkey, pave.metadate_complexity)
		}
		self.db['keys'][key] = value

	def edititem (self, key, title, password, details=''):
		self.delitem (key)
		self.additem (title, password, details)

	def getitem (self, key):
		return {
			'Details': dec (self.db['keys'][key]['Details'],self.dbkey),
			'Title':   dec (self.db['keys'][key]['Title'],self.dbkey),
			'Password':self.db['keys'][key]['Password']
		}

	def finditems (self, query):
		results = []
		for key in self.db['keys']:
			x=self.getitem (key)
			if query in x['Title'] or query in x['Details']:
				results.append ([key,x['Title'],dec (x['Password'],self.dbkey),x['Details']])
		return list(results)


if __name__=='__main__':
	starttime = time.time()
	testdb = PaveDB (key="foo",database='/tmp/pave.foo.db')
	print ("Init: %f"%(time.time()-starttime),file=sys.stderr);starttime = time.time()
	plain = "Attack at dawn"
	cipher = enc (plain,testdb.dbkey,pave.metadate_complexity)
	assert plain == dec (cipher,testdb.dbkey)
	print ("1 round: %f"%(time.time()-starttime),file=sys.stderr);starttime = time.time()
	testdb.additem ("Longtest",plain*1024)
	testdb.delitem (testdb.finditems("Longtest")[0][0])
	print ("push pop: %f"%(time.time()-starttime),file=sys.stderr);starttime = time.time()
	testdb.additem ("Testentry",plain)
	testdb.additem ("Test2",plain*3,"""Scrypt is useful when encrypting password as it is possible to specify a minimum amount of time to use when encrypting and decrypting. If, for example, a password takes 0.05 seconds to verify, a user won't notice the slight delay when signing in, but doing a brute force search of several billion passwords will take a considerable amount of time. This is in contrast to more traditional hash functions such as MD5 or the SHA family which can be implemented extremely fast on cheap hardware.""")
	import util
	print ("2 rounds: %f"%(time.time()-starttime),file=sys.stderr);starttime = time.time()
	util.print_table (testdb.finditems("Test"))
	print ("trivial search: %f"%(time.time()-starttime),file=sys.stderr);starttime = time.time()
	testdb.delitem (testdb.finditems("Test")[0][0])
	testdb.syncdb()

