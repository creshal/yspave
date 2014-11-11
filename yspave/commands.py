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
		elif action == 'get':
			self.get (query)
		elif action == 'copy':
			self.copy (query)
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


	def get (self, query):
		headings = [['ID','Title','Password','Details']]
		items = sorted (self.db.finditems (query, True), key=lambda x:x[0])
		if not items: return
		headings.extend (items)
		util.print_table (headings, True)


	def copy (self, query):
		cmd = self.db.cfg.copy_call if hasattr (self.db.cfg, 'copy_call') else 'xsel -pi'

		items = sorted (self.db.finditems (query, True), key=lambda x:x[0])
		if not items: return

		if len (items) == 1:
			chosen = items[0]
		else:
			headings = [['ID', 'Title', 'Details']]
			headings.extend ((i[:2] + (i[3],) for i in items))
			util.print_table (headings, True)

			chosen = None
			while chosen == None:
				idchoice = util.prompt ('Enter ID of the item you want to copy:\n> ')
				for i in items:
					if i[0] == idchoice:
						chosen = i
						break
				else:
					print ('ID not found.')

		try:
			proc = subprocess.Popen (cmd.split(), stdin = subprocess.PIPE)
			proc.communicate (input = chosen[2].encode ("utf8"))
		except FileNotFoundError:
			print ('Configured copy_call `%s` does not exist'%cmd)


	def edit (self, query):
		print ('Leave fields blank if you do not want to change them.')

		try:
			entry = self.db.getitem (query)
		except KeyError:
			print ('ID not found.')
			return

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

