from __future__ import print_function
from json import dump,load
from . import pave
from .util import *
import scrypt, os, Crypto.Random, time, sys


def enc (data,password,complexity):
	return tohex (scrypt.encrypt (s (data), s (password), maxtime=complexity, maxmem=int(complexity*pave.memory_factor)))

def dec (data,password):
	return scrypt.decrypt (fromhex (data), s(password))



class PaveDB ():
	def __init__ (self, key, database):
		self.rng = Crypto.Random.new()
		self.dbfile = database

		if not os.path.exists (self.dbfile):
			print ('Creating new database `%s`...'%self.dbfile)
			self.db = {
				'version': pave.database_version,
				'salt': tohex (self.rng.read(pave.saltsize)),
				'keys': {}
			}
		else:
			with open (self.dbfile) as f:
				self.db = load (f)
			if not 'version' in self.db or self.db['version'] > pave.database_version:
				raise Exception ('Unknown database format')

		self.key = mkhash (key, self.db['salt'])
		if not 'canary' in self.db:
			self.db['canary']=enc('U'*8, self.key,pave.metadate_complexity)
		else:
			# scrypt automatically raises an exception on wrong password.
			# Without this, we'll only get errors when trying to read existing items,
			# not on inserts, which can potentially corrupt the database
			dec (self.db['canary'],self.key)
		del (key)


	def syncdb (self):
		umask = False if os.path.exists (self.dbfile) else os.umask (0o7077)
		with open (self.dbfile,'w') as f:
			dump (self.db, f)
		if umask: os.umask (umask)


	def delitem (self, key):
		del self.db['keys'][key]

	def edititem (self, key, title, password, details=''):
		self.delitem (key)
		self.additem (title, password, details)


	def additem (self, title, password, details=''):
		key = sorted(map (int,self.db['keys']))[-1]+1 if self.db['keys'] else 0
		value = {
			'Title': enc (title, self.key, pave.metadate_complexity),
			'Password': enc (password, self.key, pave.password_complexity),
			'Details': enc (details, self.key, pave.metadate_complexity)
		}
		self.db['keys'][key] = value


	def getitem (self, key):
		return {
			'Details': dec (self.db['keys'][key]['Details'],self.key),
			'Title':   dec (self.db['keys'][key]['Title'],self.key),
			'Password':self.db['keys'][key]['Password']
		}


	def finditems (self, query, decrypt=False):
		results = []
		query = query.upper()
		for key in self.db['keys']:
			x=self.getitem (key)
			if query in x['Title'].upper() or query in x['Details'].upper():
				results.append ([
				 key,
				 x['Title'],
				 dec (x['Password'],self.key) if decrypt else x['Password'],
				 x['Details']
				])
		return list(results)


#Test suite
if __name__=='__main__':
	totaltime = starttime = time.time()
	testdb = PaveDB (key="foo",database='/tmp/pave.foo.db')
	print ("Init: %f"%(time.time()-starttime),file=sys.stderr);starttime = time.time()
	plain = "Attack at dawn"
	cipher = enc (plain,testdb.key,pave.metadate_complexity)
	assert plain == dec (cipher,testdb.key)
	print ("1 metadata round: %f"%(time.time()-starttime),file=sys.stderr);starttime = time.time()
	testdb.additem ("Longtest",plain*1024)
	testdb.delitem (testdb.finditems("Longtest")[0][0])
	print ("push pop: %f"%(time.time()-starttime),file=sys.stderr);starttime = time.time()
	testdb.additem ("Testentry",plain)
	testdb.additem ("Test2",plain*3,"""Scrypt is useful when encrypting password as it is possible to specify a minimum amount of time to use when encrypting and decrypting. If, for example, a password takes 0.05 seconds to verify, a user won't notice the slight delay when signing in, but doing a brute force search of several billion passwords will take a considerable amount of time. This is in contrast to more traditional hash functions such as MD5 or the SHA family which can be implemented extremely fast on cheap hardware.""")
	print ("2 push: %f"%(time.time()-starttime),file=sys.stderr);starttime = time.time()
	print_table (testdb.finditems("Test", decrypt=True))
	print ("trivial search+decode: %f"%(time.time()-starttime),file=sys.stderr);starttime = time.time()
	testdb.delitem (testdb.finditems("Test")[0][0])
	print ("search-pop: %f"%(time.time()-starttime),file=sys.stderr);starttime = time.time()
	testdb.syncdb()
	print ("writeout: %f\ntotal: %s"%(time.time()-starttime, time.time()-totaltime),file=sys.stderr)

