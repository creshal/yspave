import os.path,xdg.BaseDirectory,json,Crypto.Random
from . import pwgen

appname = 'yspave'
appvers = '0.0.2'

default_dir = xdg.BaseDirectory.save_config_path(appname)
db_filename = os.path.join (default_dir, 'default.db')
config_filename = os.path.join (default_dir, 'config.json')

database_version = 3
database_encoding = 'utf8'

class PaveCfg ():
	complex_meta = 0.01
	complex_pass = 1.0
	mem_factor = 64*1024*1024
	saltsize = 32

	pwgen_mode = 'print'
	pwgen_call = None
	pwgen_bits = 64
	pwgen_dict = '/usr/share/dict/words'

	def __init__ (self, filename, override_mode=None):
		self.rng = Crypto.Random.new()
		if override_mode:
			self.pwgen_mode = override_mode
		if not filename: return

		with open (filename) as f:
			cfgsettings=json.loads(''.join(filter(lambda x:x.strip()[0]!='#',
			                       f.readlines())))
		if 'encryption' in cfgsettings:
			encfg = cfgsettings['encryption']
			if 'metadata_complexity' in encfg: self.complex_meta = float(encfg['metadata_complexity'])
			if 'password_complexity' in encfg: self.complex_pass = float(encfg['password_complexity'])
			if 'saltsize'            in encfg: self.saltsize = int(encfg['saltsize'])
			if 'memory_factor'       in encfg:
				factor = encfg['memory_factor']
				suffix = factor[-1].upper()
				if suffix.isdigit(): self.mem_factor = int(factor)
				else:
					factor = int(factor[:-1])
					if suffix == 'G': suffix, factor = 'M', factor*1024
					if suffix == 'M': suffix, factor = 'K', factor*1024
					if suffix == 'K': suffix, factor = None, factor*1024
					if suffix: raise ValueError ('Unknown size prefix %s'%suffix)
					self.mem_factor = factor


		if 'pwgen' in cfgsettings:
			pwcfg = cfgsettings['pwgen']
			if 'mode' in pwcfg and not override_mode: self.pwgen_mode = pwcfg['mode']
			if self.pwgen_mode not in pwgen.modes:
				raise ValueError ('Unknown password generation mode: '+self.pwgen_mode)
			if 'bits' in pwcfg: self.pwgen_bits = int(pwcfg['bits'])
			if 'dict' in pwcfg: self.pwgen_dict = pwcfg['dict']
			if not os.path.exists (self.pwgen_dict):
				raise IOError ('Dictionary %s does not exist!' % self.pwgen_dict)
			if self.pwgen_mode == 'external' and 'call' in pwcfg:
				self.pwgen_call = pwcfg['call']

