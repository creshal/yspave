from __future__ import print_function
from json import dump,load,loads,dumps
from . import pave
from .util import *
import scrypt, os, shutil

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
				print ('Obsolete database version. Migrate as soon as possible.')
			if self.db['version'] in [2,3]:
				self.db['keys'] = loads (self.dec (self.db['keys'], self.key))
		self.key_meta = self.dec (self.db['metakey'], self.key)


	def enc (self, data, password,complexity):
		return to64 (scrypt.encrypt (s (data), s (password),
		        maxtime=complexity, maxmem=int(complexity*self.cfg.mem_factor)))
	def dec (self, data, password):
		if self.db['version'] < 3:
			return scrypt.decrypt (fromhex (data), s(password))
		else:
			return scrypt.decrypt (from64 (data), s(password))


	def syncdb (self):
		umask = os.umask (0o7077)
		if self.db['version'] < 3:
			print ("Migrating database to new version...")
			for key in self.db['keys']:
				for prop in self.db['keys'][key]:
					self.db['keys'][key][prop]=to64(fromhex(self.db['keys'][key][prop]))
			self.db['metakey']=to64(fromhex(self.db['metakey']))
		data = dumps ({
			'version': pave.database_version,
			'salt': self.db['salt'],
			'metakey': self.db['metakey'],
			'keys': self.enc (dumps (self.db['keys']),
			                  self.key, self.cfg.complex_pass)
		})
		if os.path.exists (self.dbfile):
			shutil.copyfile (self.dbfile,self.dbfile+'~')
		with open (self.dbfile,'w') as f:
			f.write (data)
		os.umask (umask)


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
			if not query or key == query \
			   or query in (x['Title'].upper()+x['Details'].upper()):
				results.append ((
				 key,
				 x['Title'],
				 self.dec (x['Password'],self.key) if decrypt else x['Password'],
				 x['Details']
				))
		return list(results)

