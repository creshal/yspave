from Crypto.Hash import SHA256 as hashfn
from scrypt import encrypt, decrypt
from json import dumps,loads
import binascii, os, pave, util, Crypto.Random

BLKSIZE=32

def mkhash (data):
	if type(data) is not bytes: data=data.encode (pave.database_encoding)
	return hashfn.new(data).digest()

def tohex (data): return binascii.hexlify (data).decode('ascii')
def fromhex (data): return binascii.unhexlify (data)

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
				self.db = loads (decrypt (f.read(), self.key))
			if not version in self.db or self.db['version'] > pave.database_version:
				raise Exception ('Unknown database format')
		self.dbkey = fromhex (self.db['db_key'])


	def sync_db (self):
		umask = False if os.path.exists (self.dbfile) else os.umask (0o7077)
		with open (self.dbfile,'w') as f:
			db_dumpable = encrypt (serialize (self.db), self.key, maxtime=pave.database_complexity)
			f.write (db_dumpable)
		if umask: os.umask (umask)


	def delitem (self, key):
		del self.db['keys'][key]

	def additem (self, title, password, details=''):
		key = sorted(self.db['keys'])[-1]+1 if self.db['keys'] else 0
		value = {
			'Title': encrypt (title, self.dbkey, maxtime=pave.metadate_complexity),
			'Password': encrypt (password, self.dbkey, maxtime=pave.password_complexity),
			'Details': encrypt (details, self.dbkey, maxtime=pave.metadate_complexity)
		}
		self.db['keys'][key] = value

	def edititem (self, key, title, password, details=''):
		self.delitem (key)
		self.additem (title, password, details)

	def getitem (self, key):
		return {
			'Details': decrypt (self.db['keys'][key]['Details'],self.dbkey),
			'Title':   decrypt (self.db['keys'][key]['Title'],self.dbkey),
			'Password':self.db['keys'][key]['Password']
		}

	def finditems (self, query):
		results = []
		for key in self.db['keys']:
			x=self.getitem (key)
			if query in x['Title'] or query in x['Details']:
				results.append ([key,x['Title'],decrypt (x['Password'],self.dbkey),x['Details']])
		return list(results)


if __name__=='__main__':
	testdb = PaveDB (key="foo",database='/tmp/pave.foo.db')
	plain = "Attack at dawn"
	cipher = encrypt (plain,testdb.dbkey,maxtime=pave.metadate_complexity)
	assert plain == decrypt (cipher,testdb.dbkey,maxtime=pave.metadate_complexity)
	testdb.additem ("Longtest",plain*1024)
	testdb.delitem (testdb.finditems("Longtest")[0][0])
	testdb.additem ("Testentry",plain)
	testdb.additem ("Test2",plain*3,"""Scrypt is useful when encrypting password as it is possible to specify a minimum amount of time to use when encrypting and decrypting. If, for example, a password takes 0.05 seconds to verify, a user won't notice the slight delay when signing in, but doing a brute force search of several billion passwords will take a considerable amount of time. This is in contrast to more traditional hash functions such as MD5 or the SHA family which can be implemented extremely fast on cheap hardware.""")
	import util
	util.print_table (testdb.finditems("Test"))
	testdb.delitem (0)
	testdb.syncdb()

