from . import pwgen, util
from colorama import Fore as fg
import getpass, readline, csv, subprocess,errno

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
		title = util.prompt (fg.CYAN+'Title: '+fg.RESET)
		desc  = util.prompt (fg.CYAN+'Description: '+fg.RESET)

		if generate:
			pw = self.gen.mkpass (entropy)
			print (fg.CYAN+'Generated password: '+fg.YELLOW+pw+fg.RESET)
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
		chosen = util.pick (self.db, query)
		if not chosen: return

		try:
			proc = subprocess.Popen (cmd.split(), stdin = subprocess.PIPE)
			proc.communicate (input = chosen[2].encode ("utf8"))
		except OSError as e: #python2
			if e.errno == errno.ENOENT:
				print ('Configured copy_call `%s` does not exist'%cmd)
		except subprocess.FileNotFoundError: #python3
			print ('Configured copy_call `%s` does not exist'%cmd)


	def edit (self, query):
		eid = util.pick (self.db, query)[0]
		entry = self.db.getitem (eid)
		if not entry: return

		print ('Leave fields blank if you do not want to change them.')
		nt=util.prompt ((fg.CYAN+'Title:'+fg.YELLOW+' %s\n'+fg.RESET+'New: ')\
		                  % entry['Title'],   entry['Title'])
		nd=util.prompt ((fg.CYAN+'Description:'+fg.YELLOW+' %s\n'+fg.RESET+'New: ')\
		                  % entry['Details'], entry['Details'])

		pwchoice = util.prompt ('Change password? [(y)es/(N)o/(g)enerate] ').lower()
		if pwchoice == 'y':
			print ('Old password: %s'%self.db.dec (entry['Password'],self.db.key))
			np = getpass.getpass ('New: ')
		elif pwchoice == 'g':
			print ('Old password: %s'%self.db.dec (entry['Password'],self.db.key))
			np = self.gen.mkpass ()
			print ('Generated password: '+fg.YELLOW+np+fg.RESET)
		else:
			np = self.db.dec (entry['Password'],self.db.key)

		self.db.edititem (eid, nt, np, nd)

