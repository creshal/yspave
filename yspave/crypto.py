from __future__ import print_function
from json import dump,load,loads,dumps
from . import pave
from .util import *
import scrypt, os

class PaveDB ():
	def __init__ (self, key, database, config):
		self.rng = config.rng
		self.dbfile = database
		self.cfg = config

		if not os.path.exists (self.dbfile):
			print ('Creating new database `%s`...'%self.dbfile)
			salt=tohex (self.rng.read(self.cfg.saltsize))
			self.key = mkhash (key, salt)
			self.db = {
				'version': pave.database_version,
				'salt': salt,
				'keys': {},
				'metakey': self.enc (tohex(self.rng.read(self.cfg.saltsize)),
			                       self.key, self.cfg.complex_pass)
			}
		else:
			with open (self.dbfile) as f:
				self.db = load (f)
			if not 'version' in self.db or self.db['version'] >pave.database_version:
				raise Exception ('Unknown database format')
			self.key = mkhash (key, self.db['salt'])
			if self.db['version'] == 1:
				pass
			if self.db['version'] == 2:
				self.db['keys'] = loads (self.dec (self.db['keys'], self.key))
		self.key_meta = self.dec (self.db['metakey'], self.key)


	def enc (self, data, password,complexity):
		return tohex (scrypt.encrypt (s (data), s (password),
		        maxtime=complexity, maxmem=int(complexity*self.cfg.mem_factor)))
	def dec (self, data, password):
		return scrypt.decrypt (fromhex (data), s(password))


	def syncdb (self):
		umask = False if os.path.exists (self.dbfile) else os.umask (0o7077)
		with open (self.dbfile,'w') as f:
			data = dumps ({
				'version': pave.database_version,
				'salt': self.db['salt'],
				'metakey': self.db['metakey'],
				'keys': self.enc (dumps (self.db['keys']),
				                  self.key, self.cfg.complex_pass)
			})
			f.write (data)
		if umask: os.umask (umask)


	def delitem (self, key):
		del self.db['keys'][key]

	def edititem (self, key, title, password, details=''):
		self.delitem (key)
		self.additem (title, password, details)


	def additem (self, title, password, details=''):
		key = sorted(map (int,self.db['keys']))[-1]+1 if self.db['keys'] else 0
		value = {
			'Title':    self.enc (title,   self.key_meta, self.cfg.complex_meta),
			'Password': self.enc (password,self.key,      self.cfg.complex_pass),
			'Details':  self.enc (details, self.key_meta, self.cfg.complex_meta)
		}
		self.db['keys'][key] = value


	def getitem (self, key):
		return {
			'Details': self.dec (self.db['keys'][key]['Details'],self.key_meta),
			'Title':   self.dec (self.db['keys'][key]['Title'],self.key_meta),
			'Password':self.db['keys'][key]['Password']
		}


	def finditems (self, query, decrypt=False):
		results = []
		if query: query = query.upper()
		for key in self.db['keys']:
			x=self.getitem (key)
			# Empty query ==> print whole database
			if not query or query in (x['Title'].upper()+x['Details'].upper()):
				results.append ((
				 key,
				 x['Title'],
				 self.dec (x['Password'],self.key) if decrypt else x['Password'],
				 x['Details']
				))
		return list(results)

