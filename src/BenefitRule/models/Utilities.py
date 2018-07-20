SUFFIXES = {1: 'st', 2: 'nd', 3: 'rd'}
def ordinal(num):
	# I'm checking for 10-20 because those are the digits that
	# don't follow the normal counting scheme. 
	if 10 <= num % 100 <= 20:
		suffix = 'th'
	else:
		# the second parameter is a default.
		suffix = SUFFIXES.get(num % 10, 'th')
	return str(num) + suffix

# note: currency(money) rounds when it shouldnt. expected $839.19 when it is $839.20 for final pia
def currency(num):
	return "${:,.2f}".format(num)

def percentage(num, places=2):
	return "{number:.{places}%}".format(number=num, places=places)