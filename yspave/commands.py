from . import pwgen, util
from colorama import Fore as fg
import getpass, readline, csv, subprocess

class Commands ():
	def __init__ (self, config, db):
		self.gen = pwgen.PwGen (config)
		self.db  = db

	def dispatch (self, action, query):
		if action in ('new','add'):
			self.add (query, action == 'new')
		elif action == 'del':
			self.db.delitem (query)
		elif action == 'import':
			self.imp (query)
		elif action in ('get', 'copy'):
			self.get (query, action == 'copy')
		elif action == 'edit':
			self.edit (query)
		elif action == 'pwgen':
			print (self.gen.mkpass (query))

		#action == migrate is handled implicitly by this
		if action not in ['get','pwgen']:
			self.db.syncdb()


	def add (self, entropy, generate=True):
		title, desc = util.prompt ('Title: '), util.prompt ('Description: ')

		if generate:
			pw = self.gen.mkpass (entropy)
			print ('Generated password: '+fg.YELLOW+pw+fg.RESET)
		else: pw = getpass.getpass()

		self.db.additem (title, pw, desc)


	def imp (self, source):
		with open (source, newline='') as f:
			r = csv.DictReader (f, fieldnames=('title','details','password'))
			for line in r:
				self.db.additem (**line)


	def get (self, query, copy = False):
		items = sorted (self.db.finditems (query, True), key=lambda x:x[0])
		if not items:
			print ('No results to query `%s`.' % query)
			return

		if copy:
			proc = subprocess.Popen (["xsel", "-bi"],
				stdin = subprocess.PIPE)
			proc.communicate (input = items [0] [2].encode ("utf8"))
		else:
			headings = [['ID','Title','Password','Details']]
			headings.extend (items)
			util.print_table (headings, True)


	def edit (self, query):
		print ('Leave fields blank if you do not want to change them.')

		entry = self.db.getitem (query)
		nt = util.prompt ('Title: %s\nNew: '      %entry['Title'],   entry['Title'])
		nd = util.prompt ('Description: %s\nNew: '%entry['Details'], entry['Details'])

		pwchoice = util.prompt ('Change password? [(y)es/(N)o/(g)enerate]').lower()
		if pwchoice == 'y':
			print ('Password: %s'%self.db.dec (entry['Password'],self.db.key))
			np = getpass.getpass ('New: ')
		elif pwchoice == 'g':
			np = self.gen.mkpass ()
			print ('Generated password: '+fg.YELLOW+np+fg.RESET)
		else:
			np = self.db.dec (entry['Password'],self.db.key)

		self.db.edititem (query, nt, np, nd)

