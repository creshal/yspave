import Crypto.Random, subprocess, scrypt, math, string
from . import pave,util

def new (entropy=None,mode=pave.pwgen_mode,call=None):
	if mode == 'external':
		return subprocess.check_output (call,shell=True)

	entropy = int (entropy) if entropy and int(entropy)>32 else pave.password_bits

	rng = Crypto.Random.new()

	if mode in ['x','xkcd']:
		raise NotImplementedError ()
	elif mode in ['p','print']:
		bytes_needed = int ((entropy*math.log(2))/math.log(94))
		return ''.join (map (lambda x: chr(x%94+21), rng.read(bytes_needed)))
	elif mode in ['a','alnum']:
		lut = string.ascii_letters+string.digits
		lutsz = len (lut)
		bytes_needed = int ((entropy*math.log(2))/math.log(lutsz))
		return ''.join (map (lambda x: lut[x%lutsz], rng.read(bytes_needed)))
	else:
		return util.tohex (util.mkhash (rng.read (pave.password_bits/8),''))

