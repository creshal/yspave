import subprocess, math, string

modes = ['external', 'x','xkcd','p','print', 'a','alnum']

class PwGen ():
	def __init__ (self, config):
		self.bits = config.pwgen_bits
		self.mode = config.pwgen_mode
		self.call = config.pwgen_call
		self.dict = config.pwgen_dict
		self.rng  = config.rng

	def entropy_estimate (self, entropy, token_range):
		return int ((entropy*math.log(2))/math.log(token_range))

	def mkpass (self, entropy=None):
		if self.mode == 'external':
			return subprocess.check_output (self.call,shell=True)

		entropy=self.bits if not entropy else int(entropy)
		if self.mode in ['x','xkcd']:
			raise NotImplementedError ()
		else:
			if self.mode in ['p','print']:
				lut = string.ascii_letters+string.digits+string.punctuation
			elif self.mode in ['a','alnum']:
				lut = string.ascii_letters+string.digits
			lutsz = len (lut)
			bytes_needed = self.entropy_estimate (entropy, lutsz)
			return ''.join (map (lambda x: lut[x%lutsz], self.rng.read(bytes_needed)))

