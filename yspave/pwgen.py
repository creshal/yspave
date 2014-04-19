import subprocess, math, string

modes = ['external', 'x','xkcd','p','print', 'a','alnum']

class PwGen ():
	def __init__ (self, config):
		self.bits = config.pwgen_bits
		self.mode = config.pwgen_mode
		self.call = config.pwgen_call
		self.dict = config.pwgen_dict
		self.rng  = config.rng

	def new (self):
		if self.mode == 'external':
			return subprocess.check_output (self.call,shell=True)

		if mode in ['x','xkcd']:
			raise NotImplementedError ()
		elif mode in ['p','print']:
			bytes_needed = int ((self.bits*math.log(2))/math.log(94))
			return ''.join (map (lambda x: chr(x%94+21), self.rng.read(bytes_needed)))
		elif mode in ['a','alnum']:
			lut = string.ascii_letters+string.digits
			lutsz = len (lut)
			bytes_needed = int ((self.bits*math.log(2))/math.log(lutsz))
			return ''.join (map (lambda x: lut[x%lutsz], self.rng.read(bytes_needed)))

