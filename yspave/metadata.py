# vim: set tabstop=8 shiftwidth=8 colorcolumn=80:
appname = 'yspave'
appvers = '0.1.1'

database_version = 3
database_encoding = 'utf8'

verbs = [
	'new', 'add', 'del',
	'imp', 'get', 'list',
	'copy', 'edit', 'pwgen',
	'migrate'
]

actions = '''scrypt based password manager.

Actions:
	new	Prompts for title/description and generates a new password
		with supplied entropy (default: %i bit)

	add	Prompts for title, description and password

	edit	Edits an entry matching the query string

	del	Deletes the entry with the supplied ID

	get	Searches the DB for the supplied query string
		Shows the whole database if no query is supplied, this can
		take a while.

	list	Same as get, but does not show passwords, only metadata.

	copy	Same as 'get', uses `copy_command` on (selectable) query result.
		Default: Calls xsel to copy the result to primary selection.

	pwgen	Generate a random password with supplied entropy and print it
		(default: %i bit)

	import	Imports passwords from a CSV file.
		Column order is title, description, password
		The format is the default Excel/Calc format (comma separation,
		quoting optional).

	migrate	Re-syncs the database, migrating it to new database formats
		and doing other maintenance if necessary.
		This is also done automatically on all writing operations
		(i.e., add/del/edit/new/import).

Password generator options:
	x, xkcd		Random word generator as per XKCD 936
	a, alnum	Random letters/numbers
	p, print	Random characters (letters, digits, punctuation)

'''

examples = '''Examples:
	yspavectl pwgen 192
		Generates a random alphanumeric password and prints it

	yspavectl -m x pwgen
		Generates a random "sentence"

	yspavectl get foobar
		Shows all passwords matching "foobar" in their
		description or title

	yspavectl new
		Generates a new password and saves it together with
		supplied metadata

	yspavectl edit foobar
		Prompts you to pick an entry matching "foobar" to edit
'''

