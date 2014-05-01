# Database formats

## Version 1
Never used in a public release, equal to V2 except:
* version is 1 (duh)
* keys is not encrypted

## Version 2
The database is now encrypted as well. Previously, only the fields were
encrypted, making it trivial to tamper with the database by replacing,
deleting or adding passwords (thus corrupting the database in a non-detectable
way).

<pre>{
	'version': 2,
	'salt': hex(RANDOM_BYTES),
	'metadata_key': encrypt_strong (RANDOM_BYTES),
	'keys': encrypt_strong ( database_key, {
		str(id): {
			'Title': encrypt_simple (metadata_key, str),
			'Details': encrypt_simple (metadata_key, str),
			'Password': encrypt_strong (str)
		},
		...
	})
}</pre>

# Overall architecture description/rationale
## JSON
Serialization/deserialization happens at most four times per program run
(open DB, open keys, serialize keys, serialize db). As such simplicity and
robustness was deemed more important than performance. SQLite would give little
benefits, and XML is madness even on a good day.
## Scrypt
Scrypt is used as PBKDF for hashing the user-supplied password, as well as for
encrypting/decrypting data (using its builtin `scryptenc_buf` and
`scryptdec_buf` functions, which internally use AES-CTR in stream cipher mode).

Scrypt was chosen for its versatility (covers all required crypto operations)
and maturity – while keccak+salsa20 *might* be more secure, implementations
are not necessarily as well-tested or provide the memory hardness of scrypt.

Additionally, scrypt provides checksumming during en-/decryption, increasing
tamper resistance and giving a built-in password verification mechanism.
### Complexity parameters and performance impact
As searches have to operate on metadata, these are encrypted by default at
rather low complexity parameters (10ms/640k), to keep the performance bearable.
The performance impact on searches is `2*complexity*total_password_count`
(there are two separate metadata fields) and `2*complexity` on inserts/edits.

The database itself and the passwords are encrypted at a considerably higher
complexity (1s/64M). The performance impact is `2*complexity` on each startup
and writes, plus `complexity` on inserts/edits, and for each found password on
searches.
## Key and encryption usage
The user-supplied password is stretched with a random 32 byte salt before
being hashed using scrypt. This PBK is used to decrypt the database and the
metadata key, as well as actual passwords.

Actual metadata are encrypted using a randomly generated (again 32 byte long)
password, to prevent brute-force attacks on the PBK due to their lower
complexity parameters.
## Random number generation
Crypto.Random is used to create the cryptographic RNG, which seems to default
to a Fortuna-based RNG with a 16K seed.

