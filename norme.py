#! /usr/bin/env python

'''
An Epitech norme checker
Usage: python norme.py <dir to scan> [-nocheat] [-verbose] [-score] [-libc]
-verbose: affiche les messages impossible d\'ouvrir
-nocheat: desactive la detection de la triche
-score: affiche le nombre de faute de norme
-libc: active la verification des fonctions de la libc
-malloc: active le controle du malloc
-printline: affiche la ligne provoquant une erreur
-return: active verifier le retour des fonctions (return ;)
-comment: ne pas verifier les commentaire
Non geree:
- Indentation
- +<escape>
- verification de la presence de gl_
Bug:
Il est arrivee que le checker ne trouve aucune faute alors qu\'il en existe, si
ce bug vous arrive maillez moi.
'''

import sys,re,os,pwd

class norme:
	def __init__(self):
		self.user = []
		self.verbose = 0
		self.cheat = 1
		self.comment = 1
		self.score = 0
		self.note = 0
		self.libc = 1
		self.malloc = 0
		self.printline = 0
		self.creturn = 1
		self.ident = 0
		self.prototype = 0
		
	def new_file(self):
		self.Indentation_level = 0
		self.nb_line = 1
		self.nb_return = 0
		self.nb_funcline = 0
		self.nb_func = 0
		self.sys_include = 0
		self.double_inclusion = 0
		self.is_func = 0
		self.typedef = 0
		self.check_malloc1 = 0
		self.one_line = 0
		self.cut = 0
		self.malloc_vars = []
		if self.verbose == 1:
			print "Scan",self.file
	
	def check_header(self):
		if (self.nb_line == 1):
			if (self.line[:2] != '/*'):
				self.print_error('header incorrect')
		elif (self.nb_line == 6):
			if (self.line[:2] != '*/'):
				self.print_error('header incorrect')
		elif self.nb_line == 4 or self.nb_line == 7 or self.nb_line == 8:
			if self.cheat:
				p = re.compile('([\w-]* [\w-]*)$')
				test = re.search(p, self.line)
				if test:
					if not test.group(1) in self.user:
						self.print_error('login '+ test.group(1) +' incorrect')
		elif (self.nb_line == 5):
			if self.cheat:
				p = re.compile('<(.*)@')
				test = re.search(p, self.line)
				if test:
					if not test.group(1) in self.user:
						self.print_error('login '+ test.group(1) +' incorrect')
		else:
			if (self.line[:2] != '**'):
				self.print_error('header incorrect')

	def check_virgule(self):
		n = 0
		quote = 0
		while self.line[n] != '\n' and n < len(self.line)-1:
			if self.line[n] == '\'' or self.line[n] == '"':
				if quote:
					quote = 0
				else:
					quote = 1
			if (self.line[n] == ';' or self.line[n] == ',') and quote == 0:
				if self.line[n + 1] != ' ' and self.line[n + 1] != '\n':
					self.print_error('point-virgule ou virgule mal place')
			n = n + 1

	def check_nbchar(self):
		line = self.line.replace('\t', '        ')
		if (line[80:]):
			self.print_error('chaine de plus de 80 caracteres')

	def check_indentation(self):
		if self.line[:1] != '}' and '}' in self.line and not ';' in self.line:
			self.Indentation_level -= 1
		line = self.line.replace('\t', '        ')
		i = 0
		while line[i] == ' ':
			i += 1
		p = re.compile('(if|else|while|for)')
		test1 = re.search(p, self.line)
		i = i / 8
		#self.print_error("%d %s" % (i, self.line))
		if i != self.Indentation_level and line[:1] != '}' and i != 0 and self.one_line == 0 and self.cut == 0:
			self.print_error("identation incorrecte")
		if self.one_line == 1:
			if (i != self.Indentation_level + 1):
				self.print_error("indentation incorrecte")
			self.one_line = 0
		if test1 and '{' in self.line:
			self.Indentation_level += 1
		if test1 and not '{' in self.line and ')' in self.line:
			self.one_line = 1
		if self.cut > 0 and ')' in self.line:
			self.Indentation_level += 1
			self.cut = 0
		if self.cut > 0 and not ')' in self.line:
			self.cut += 1
		if test1 and not ')' in self.line:
			self.cut = 1
		
		if (i > 3):
			self.print_error("identation superieur a 3")

	def check_return(self):
		if (self.line[:1] == '\n'):
			if (self.nb_return == 1):
				self.print_error('double retour a la ligne')
			else:
				self.nb_return = 1
		else:
			self.nb_return = 0

	def check_nbline(self):
		if self.file[-2:] == ".c":
			if self.line[:1] == '}':
				if (self.check_malloc1 != 0):
					i = 0
					while (i < self.check_malloc1):
						self.print_error(self.malloc_vars[i] + "was not checked")
						i += 1
					self.check_malloc1 = 0
					self.malloc_vars = []
				self.is_func = 0
				self.nb_funcline = 0
			if self.line[:1] == '{' and self.typedef == 0:
				self.is_func = 1
				self.Indentation_level = 1
				self.nb_funcline = 0
				self.nb_func = self.nb_func + 1
				if self.nb_func == 6:
					self.print_error('plus de 5 fonctions dans le fichier')
			else:
				if self.nb_func >= 1 and self.is_func:
					self.nb_funcline = self.nb_funcline + 1
					if self.nb_funcline == 21:
						self.print_error('fonction de plus de 20 lignes')
			if self.is_func == 0 and self.line[0] != '#' and self.line[0] != '}' and len(self.line) > 1 and self.prototype == 1:
				file = open("header", "a")
				line = self.line[0:len(self.line) - 1] + ";\n"
				file.write(line)
				file.close

	def check_cfunc(self):
		p = re.compile('[ \t](if|else|return|while|for)(\()')
		test = re.search(p, self.line)
		if test:
			self.print_error('pas d\'espace apres mot clef')

	def check_arg(self):
		if self.line[-2:] == ")\n" and self.line[:1] != '\t'  and self.line[:1] != ' ':
			p = re.compile('(.*),(.*),(.*),(.*),(.*)\)$')
			test = re.search(p, self.line)
			if test:
				self.print_error('plus de 4 arguments passes en parametre')
				
	def check_sys_include(self):
		if self.line[:1] == "#" and self.line[-2:] == "\"\n":
			self.sys_include = 1
		else:
			if self.line[:1] == "#" and self.line[-2:] == ">\n" and self.sys_include == 1:
				self.print_error('Header systeme mal placee')

	def check_comment(self):
		if self.is_func and self.comment:
			p = re.compile('(//|/\*)')
			test = re.search(p, self.line)
			if test:
				self.print_error('Commentaires dans le code')

	def check_malloc(self):
		p = re.compile('[^x](malloc)(\()')
		test = re.search(p, self.line)
		if self.check_malloc1 > 0:
			i = 0 
			while i < self.check_malloc1:
				word = self.malloc_vars[i] + "== NULL"
				if word in self.line:
					self.malloc_vars.remove(self.malloc_vars[i])
					self.check_malloc1 -= 1
				i += 1
		if test:
			line = self.line.replace('\t', '        ')
			equal = line.find('=')
			j = equal - 2
			while (line[j] != '*' and line[j] != ' ' and j != 0):
				j -= 1
			self.check_malloc1 += 1
			self.malloc_vars.append(line[j+1:equal])


	def check_double(self):
		if self.file[-2:] == ".h":
			if self.line[:1] != '\n':
				if self.double_inclusion != 1:
					if self.line[-4:] != "_H_\n":
						self.print_error('Header non protegee')
					else:
						self.double_inclusion = 1

	def check_operateur(self, op):
		n = 0
		quote = 0
		while self.line[n] != '\n' and n < len(self.line)-1:
			if self.line[n] == '\'' or self.line[n] == '"':
				if quote:
					quote = 0
				else:
					quote = 1
			if (self.line[n] == op) and quote == 0:
				if self.line[n + 1] != ' ' and self.line[n + 1] != ';' and self.line[n + 1] != '=':
					if self.line[n - 1] != op and self.line[n + 1] != op:
						msg = 'Operateur \'%c\' mal place' % op
						self.print_error(msg)
			n = n + 1

	def check_typedef(self):
		if self.line[:7] == "typedef":
			self.typedef = 1
		else:
			self.typedef = 0
	
	def check_regex(self, regex, msg):
		p = re.compile(regex)
		test = re.search(p, self.line)
		if test:
			self.print_error(msg)

	def check_line(self):
		if self.ident == 1:
			self.check_indentation()
		self.check_nbline() # DOIT TOUJORS ETRE EN PREMIER
		self.check_sys_include()
		self.check_virgule()
		self.check_regex('[ \t]$', 'Espace en fin de ligne')
		if self.creturn == 0:
			self.check_regex('return( \(\)| ;|;)', 'Mauvais format de return')
		if self.libc == 0:
			self.check_regex('[^_](printf|atof|atoi|atol|strcmp|strlen|strcat|strncat|strncmp|strcpy|strncpy|fprintf|strstr|strtoc|sprintf|asprintf|perror|strtod|strtol|strtoul)(\()', \
							 'Fonction de la lib C')
		self.check_nbchar()
		self.check_cfunc()
		self.check_arg()
		self.check_comment()
		self.check_return()
		self.check_double()
		self.check_operateur('+')
		self.check_operateur('|')
		self.check_typedef() #DOIT TOUJOURS ETRE EN DERNIER
		if self.malloc:
			self.check_malloc()
		
	def print_error(self, msg):
		self.note = self.note + 1
		print "Erreur dans",self.file,"a la ligne",self.nb_line,":",msg
		if self.printline:
			print self.line

	def cant_open(self, file):
		if (self.verbose or file == sys.argv[1]):
			print "Impossible d'ouvrir",file

	def scandir(self, thedir):
		try:
			dir = os.listdir(thedir)
		except:
			self.cant_open(thedir)
		else:
			if (self.prototype == 1):
				file = open("header", "w")
				file.write("")
			check_makefile(thedir)
			for file in dir:
				if (os.path.isdir(thedir + file)):
					self.scandir(thedir + "/" + file + "/")
				if file[-2:] == '.c' or file[-2:] == '.h':
					self.file = file
					self.new_file()
					file = thedir + file
					try:
						fd = open(file, 'r')
					except IOError:
						self.cant_open(file)
					else:
						for self.line in fd.readlines():
							if self.nb_line <= 6:
								self.check_header()
							else:
								self.check_line()
							self.nb_line = self.nb_line + 1
							fd.close()

	def get_user(self):
		try:
			fd = open(sys.argv[1] + 'auteur')
		except IOError:
			user = os.getenv('USER')
			self.user.append(user)
			self.user.append(pwd.getpwnam(user)[4]) #Recuperation du nom complet de l'utilisateur
		else:
			buffer = fd.read()
			fd.close()
			p = re.compile('([\w]*)')
			test = re.findall(p, buffer)
			for user in test:
				if user:
					self.user.append(user)
					self.user.append(pwd.getpwnam(user)[4])


def check_makefile(thedir):
	file = thedir + "Makefile"
	if os.path.isfile(file):
		try:
			fd = open(file, 'r')
		except IOError:
			print "Impossible d'ouvrir le Makefile"
		else:
			buffer = fd.read()
			p = re.compile('(-g|-pg|-lefence)')
			test = re.search(p, buffer)
			if test:
				print "Options de debug dans le Makefile"
			p = re.compile('(-Wall)')
			test = re.search(p, buffer)
			if not test:
				print "-Wall n'est pas dans le Makefile"
			p = re.compile('(-pedantic)')
			test = re.search(p, buffer)
			if not test:
				print "-pedantic n'est pas dans le Makefile"
			if buffer[:2] != "##":
				print "Header du Makefile invalide"
			fd.close()

def help():
	print "Aide"
	print "Usage: norme.py <dir_to_scan>"
	print "-verbose: affiche les messages impossible d'ouvrir"
	print "-nocheat: desactive la detection de la triche"
	print "-score: affiche le nombre de faute de norme"
	print "-libc: active la verification des fonctions de la libc"
	print "-malloc: desactive le controle du malloc"
	print "-printline: affiche la ligne provoquant une erreur"
	print "-return: active verifier le retour des fonctions (return ;)"
	print "-comment: ne pas verifier les commentaire"
	sys.exit()

def main():
	if len(sys.argv) == 1:
		print "Usage: norme.py <dir_to_scan>"
		sys.exit()
	moulin = norme()
	if '-verbose' in sys.argv[1:]:
		moulin.verbose = 1
	if '-comment' in sys.argv[1:]:
		moulin.comment = 0
	if '-nocheat' in sys.argv[1:]:
		moulin.cheat = 0
	if '-score' in sys.argv[1:]:
		moulin.score = 1
	if '-libc' in sys.argv[1:]:
		moulin.libc = 0
	if '-malloc' in sys.argv[1:]:
		moulin.malloc = 1
	if '-printline' in sys.argv[1:]:
		moulin.printline = 1
	if '-return' in sys.argv[1:]:
		moulin.creturn = 0
	if '-indent' in sys.argv[1:]:
		moulin.ident = 1
	if '-help' in sys.argv[1:]:
		help()
	if '-prototype' in sys.argv[1:]:
		moulin.prototype = 1
	if sys.argv[1][-1:] != '/':
		sys.argv[1] = sys.argv[1] + '/'
	if moulin.cheat == 1:
		moulin.get_user()
	try:
		moulin.scandir(sys.argv[1])
	except NameError:
		print "Usage: norme.py <dir_to_scan>"
	if moulin.score:
		print "Vous avez fait",moulin.note,"fautes de norme"

if __name__ == "__main__":
	main()