def print_table (lines):
	cols = max (map (len, lines))
	colsizes = [max (map (lambda y: len(str(y)), [l[x] for l in lines])) for x in range (cols)]
	for line in lines:
		print ("".join([str(line[i]).ljust(colsizes[i]+4) for i in range (cols)]).rstrip())

if __name__=='__main__':
	testcase = [
		["foo"*2, "baz", "basdfdsfdsfdsfdsfds"],
		["foobarfoo","batbatbat", "asd"]]
	table = [["", "taste", "land speed", "life"],
		["spam", 300101, 4, 1003],
		["eggs", 105, 13, 42],
		["lumberjacks", 13, 105, 10]]
	print_table (testcase)
	print ()
	print_table (table)

