from __future__ import print_function
from json import dump,load
from . import pave
from .util import *
import scrypt, os, Crypto.Random, time, sys



class PaveDB ():
	def __init__ (self, key, database, config):
		self.rng = config.rng
		self.dbfile = database
		self.cfg = config

		if not os.path.exists (self.dbfile):
			print ('Creating new database `%s`...'%self.dbfile)
			self.db = {
				'version': pave.database_version,
				'salt': tohex (self.rng.read(self.cfg.saltsize)),
				'keys': {}
			}
		else:
			with open (self.dbfile) as f:
				self.db = load (f)
			if not 'version' in self.db or self.db['version'] > pave.database_version:
				raise Exception ('Unknown database format')

		self.key = mkhash (key, self.db['salt'])
		del (key)
		if not 'metakey' in self.db:
			# As metadata are encrypted with usually lower complexity standards (to
			# improve overall performance), use a random key for those, not the
			# same as for passwords. Brute force attacks against metadata are much
			# more feasible than against passwords, this is intended to prevent
			# password leaks from metadata attacks.
			self.db['metakey'] = self.enc (tohex(self.rng.read(self.cfg.saltsize)),
			                               self.key, self.cfg.complex_pass)
		# As a side-effect, this forces the entered key to be verified, ensuring
		# the correct one was supplied before attempting to operate on the actual
		# database contents.
		self.key_meta = self.dec (self.db['metakey'], self.key)


	def enc (self, data, password,complexity):
		return tohex (scrypt.encrypt (s (data), s (password),
		        maxtime=complexity, maxmem=int(complexity*self.cfg.mem_factor)))
	def dec (self, data, password):
		return scrypt.decrypt (fromhex (data), s(password))


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
		query = query.upper()
		for key in self.db['keys']:
			x=self.getitem (key)
			if query in x['Title'].upper() or query in x['Details'].upper():
				results.append ((
				 key,
				 x['Title'],
				 self.dec (x['Password'],self.key) if decrypt else x['Password'],
				 x['Details']
				))
		return list(results)

