from setuptools import setup
from yspave import pave

setup (
	name=pave.appname,
	version=pave.appvers,
	install_requires=['scrypt','pycrypto','colorama','pyxdg'],
	data_files=[
	 ('/usr/share/doc/yspave',['COPYING','HACKING.md','README.md','config.json.example']),
	 ('/usr/bin','yspavectl')
	],
	packages=['yspave'],
	description='scrypt based CLI password manager',
	author='Samuel Vincent Creshal',
	author_email='samuel@creshal.de',
	license='GPLv3',
	classifiers=[
		'Development Status :: 4 - Beta',
		'Programming Language :: Python :: 2.7',
		'Programming Language :: Python :: 3'
	]
)

