from . import pwgen, util, metadata
from colorama import Fore as fg
import getpass, readline, csv, subprocess,errno

class Commands ():
	def __init__ (self, config, db):
		self.gen = pwgen.PwGen (config)
		self.db  = db

	def dispatch (self, action, query):
		if action in metadata.verbs:
			if action == 'import': action = 'imp' #reserved keyword
			elif action == 'del':  action = 'dele'
			getattr (self, action)(query)
		else:
			print (fg.RED+'Unknown action!'+fg.RESET)

		# Sync after writing actions; this also implicitly migrates
		if action not in ['pwgen', 'get', 'list']:
			self.db.syncdb ()


	def add (self, entropy, generate=False):
		title = util.prompt (fg.CYAN+'Title: '+fg.RESET)
		desc  = util.prompt (fg.CYAN+'Description: '+fg.RESET)

		if generate:
			pw = self.gen.mkpass (entropy)
			print (fg.CYAN+'Generated password: '+fg.YELLOW+pw+fg.RESET)
		else: pw = getpass.getpass()

		self.db.additem (title, pw, desc)


	def new (self, entropy): self.add (entropy, True)
	def migrate (self, arg): pass #Already done in dispatch()
	def pwgen (self, query): print (self.gen.mkpass (query))


	def imp (self, source):
		with open (source, newline='') as f:
			r = csv.DictReader (f, fieldnames=('title','details','password'))
			for line in r:
				self.db.additem (**line)


	def get (self, query, decrypt=True):
		headings = [['ID','Title','Password','Details']]
		items = sorted (self.db.finditems (query, decrypt), key=lambda x:x[0])
		if not items: return
		headings.extend (items)
		util.print_table (headings if decrypt else
		                  [(x[0],x[1],x[3]) for x in headings], #prune pw column
		                  True)

	def list (self, query): self.get (query, False)


	def dele (self, query):
		eid, title, pw, desc = util.pick (self.db, query)

		if util.prompt (fg.RED+ 'Are you sure you want to delete this item? [yN] '\
		                + fg.RESET).lower () == 'y':
			self.db.delitem (eid)
			print (fg.RED+'Deleted'+fg.RESET)


	def copy (self, query):
		cmd = self.db.cfg.copy_call
		chosen = util.pick (self.db, query)
		if not chosen: return

		if self.db.cfg.copy_show_details:
			print (fg.CYAN+'Title: '+fg.YELLOW+chosen[1]+fg.RESET)
			print (fg.CYAN+'Details: '+fg.YELLOW+chosen[3]+fg.RESET)

		try:
			proc = subprocess.Popen (cmd.split(), stdin = subprocess.PIPE)
			proc.communicate (input = chosen[2].encode ("utf8"))
		except OSError as e: #python2
			if e.errno == errno.ENOENT:
				print ('Configured copy_call `%s` does not exist'%cmd)
			else: raise e #Unknown error, bail
		except subprocess.FileNotFoundError: #python3
			print ('Configured copy_call `%s` does not exist'%cmd)


	def edit (self, query):
		entry = util.pick (self.db, query)
		if not entry: return
		eid, ot, pw, od = entry

		print ('Leave fields blank if you do not want to change them.')
		nt=util.prompt ((fg.CYAN+'Title:'+fg.YELLOW+' %s\n'+fg.RESET+'New: ')\
		                  % ot, ot)
		nd=util.prompt ((fg.CYAN+'Description:'+fg.YELLOW+' %s\n'+fg.RESET+'New: ')\
		                  % od, od)

		pwchoice = util.prompt ('Change password? [(y)es/(N)o/(g)enerate] ').lower()
		if pwchoice == 'y':
			print ('Old password: %s' % pw)
			pw = getpass.getpass ('New: ')
		elif pwchoice == 'g':
			print ('Old password: %s' % pw)
			pw = self.gen.mkpass ()
			print ('Generated password: '+fg.YELLOW+np+fg.RESET)

		self.db.edititem (eid, nt, pw, nd)

