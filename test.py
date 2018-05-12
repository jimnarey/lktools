
a = {'a':1, 'b':1, 'c':1, 'd':1, 'e':1, 'f':1}
b = {'d':1, 'e':1, 'f':1, 'g':1, 'h':1, 'i':1}

def sola(dict1, dict2):
	return filter(dict1.has_key, dict2.keys())

def solb(dict1, dict2):
	return [i for i in dict1 if i in dict2]

c = sola(a, b)

d = solb(a, b)