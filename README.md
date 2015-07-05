# yspave – CLI password manager

See below for usage information and `HACKING.md` for architectural information.

## Usage

	usage: yspave [-h] [--version] [--file [FILE]] [--config-file [CONFIG_FILE]]
	              [--pwgen-mode [{print,p,alnum,a,xkcd,x}]]
	              [{migrate,new,add,edit,del,get,copy,pwgen,import}] [query]

	scrypt based password manager.

	Actions:
		new	Prompts for title/description and generates a new password
			with supplied entropy (default: 64 bit)
		add	Prompts for title, description and password
		edit	Edits an entry matching the query string
		del	Deletes the entry with the supplied ID
		get	Searches the DB for the supplied query string
			Shows the whole database if no query is supplied, this can
			take a while.
		copy	Same as 'get', uses `copy_command` on (selectable) query result.
			Default: Calls xsel to copy the result to primary selection.
		pwgen	Generate a random password with supplied entropy and print it
			(default: 64 bit)
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

	positional arguments:
		{migrate,new,add,edit,del,get,copy,pwgen,import}
		query                 Search string

	optional arguments:
		-h, --help            show this help message and exit
		--version, -v         show program's version number and exit
		--file [FILE], -f [FILE]
		                      Database file
		--config-file [CONFIG_FILE], -c [CONFIG_FILE]
		                      Configuration file
		--pwgen-mode [{print,p,alnum,a,xkcd,x}], -m [{print,p,alnum,a,xkcd,x}]

	Examples:
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


## Files
`~/.config/yspave/default.db` – Default database

`~/.config/yspave/config.json` – Default configuration file. See `/usr/share/doc/yspave/config.json.example` for a sample.

