#!/usr/bin/env python
# -*- coding: utf-8 -*-

from parseo import *

class CompresorEstatico:
	def __init__(self, modoParseo):
		self.tabla = SymbolTable()
		self.parser = SymbolParser(modoParseo)
	
	def getSymbolTable(self):
		return self.tabla
		
	def parsearTexto(self, texto):
		self.parser.parsearTexto(texto, self.tabla)
		return texto
		
	def asignarSymbolTable(self, tablaSimbolos):
		self.tabla = tablaSimbolos
		
	def comprimirTexto(self, texto):
		return

# Clase auxiliar que inventó Juan
class Decodificador:
	def __init__(self, codigo):
		self.it = iter(codigo)
		self.lower = 0.0
		self.count = 1
		self.readNext
		
	def getInterval(self):
		return (self.lower, self.upper)
		
	def readNext(self):
		try:
			act = self.it.next()
		except StopIteration:
			act = '0'
			
		#print 'Se leyo el ', act
		if (act == '0'):
			self.upper = self.lower + 1.0/2**self.count
		else:
			self.lower = self.lower + 1.0/2**self.count
			self.upper = self.lower + 1.0/2**self.count
		self.count += 1
	
	def reduce(self):
		self.upper *= 2
		self.upper -= int(self.upper)
		self.lower *= 2
		self.lower -= int(self.lower)
		self.count -= 1

class CompresorAritmetico(CompresorEstatico):
	def comprimirTexto(self, texto):
		intInferior = 0.0
		intSuperior = 1.0
		casosTotales = self.tabla.verCasosTotales()
		simbolos = self.tabla.verSimbolos()
		longMinima = 1.0 / float(casosTotales)

		#opcional:
		simbolos.sort()
		
		codigo = ''
		
		for c in texto:
			longMinima = (intSuperior - intInferior) / float(casosTotales)
			intAcumulado = intInferior
			for simb in simbolos:
				if (simb == c):
					intInferior = intAcumulado
					intSuperior = intAcumulado + (self.tabla.verFrecuencia(simb) * longMinima)
					intInfRounded = int(intInferior * 2)
					intSupRounded = int(intSuperior * 2)
					while(intInfRounded == intSupRounded):
						codigo += str(intInfRounded)
						#print "Intervalo: (", intInferior, ";", intSuperior, ")"
						#print "Emito: ", intInfRounded
						intInferior *= 2
						intInferior -= intInfRounded
						intSuperior *= 2
						intSuperior -= intSupRounded
						intInfRounded = int(intInferior * 2)
						intSupRounded = int(intSuperior * 2)
					next
				else:
					intAcumulado += (self.tabla.verFrecuencia(simb) * longMinima)
		
		# Completo codificando el último intervalo a binario
		valorBin = 0.0
		i = 1
		while((valorBin < intInferior) or (valorBin > intSuperior)):
			aux = 1.0/(2**i)
			if((valorBin + aux) > intSuperior):
				codigo += '0'
			else:
				codigo += '1'
				valorBin += aux
			i += 1
				
		# print 'Intervalo final: (', intInferior, ';', intSuperior, ')' 		
		return codigo
			

	def descomprimirTexto(self, codigo):
		casosTotales = self.tabla.verCasosTotales()
		simbolos = self.tabla.verSimbolos()
		longMinima = 1.0 / float(casosTotales)
		intInferior = 0.0
		intSuperior = 1.0
		decode = ''
		simbolos.sort()
		
		my_deco = Decodificador(codigo)
		my_deco.readNext()
		
		end = False
		
		## Trata de decodificar 500 caracteres (reemplazar luego por EOF)
		while(not end):
			intAcumulado = intInferior
			longMinima = (intSuperior - intInferior) / float(casosTotales)
			for simb in simbolos:
				intSuperior = intAcumulado + (self.tabla.verFrecuencia(simb) * longMinima)
				rango = my_deco.getInterval()
				#print 'Rango del deco: ', rango, ' Simb:', simb, intAcumulado, intSuperior
				if ((rango[0] >= intAcumulado) and (rango[0] < intSuperior)):
					while((rango[1] > intSuperior) and (rango[0] < intSuperior)):
						#print 'Rango del deco: ', rango, ' Simb:', simb, intAcumulado, intSuperior
						my_deco.readNext()
						rango = my_deco.getInterval()
					if((rango[0] >= intAcumulado) and (rango[0] < intSuperior)):
						decode += simb
						if (ord(simb) == 0):
							end = True;
						#print 'Emito ', simb
						intInferior = intAcumulado
						while(int(intInferior * 2) == int(intSuperior * 2)):
							my_deco.reduce()
							intInferior *= 2
							intInferior -= int(intInferior)
							intSuperior *= 2
							intSuperior -= int(intSuperior)
						break
				intAcumulado += (self.tabla.verFrecuencia(simb) * longMinima)

		return decode





#Zona de tests
#cmpr = CompresorAritmetico('letra')
#texto = 'Desert loving in your eyes all the way If I listened to your lies would you say Im a man without conviction Im a man who doesnt know How to sell a contradiction You come and go You come and go Karma Karma Karma Karma Karma Chameleon You come and go You come and go Loving would be easy if your colors were like my dream Red, gold and green Red, gold and green Didnt hear your wicked words every day And you used to be so sweet I heard you say That my love was an addiction When we cling our love is strong When you go youre gone forever You string along You string along Karma Karma Karma Karma Karma Chameleon You come and go You come and go\0'
#texto = 'I was unable to cope with what you said\nSometimes we need to be cruel to be kind\nChild that I was, could not see the reason\nFeelings I had were but sham and a lie?\n\nI have never forgotten your smile\nYour eyes, oh, Shamandalie\n\nTime went by, many memories died\nI\'m writing this down to ease my pain\n\nYou saw us always clearer than me\nHow we were never meant to be\nLove denied meant the friendship would die\nNow I have seen the light\nThese memories make me cry\0'
#texto = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890[]+*-¬|$&%()?°@\0'
#texto = 'AAAAABBBCC\0'
#cmpr.parsearTexto(texto)
#print  'A COMPRIMIR:\n\"', texto, '\"\ncon compresor aritmetico'
#binario = cmpr.comprimirTexto(texto)
#print 'Resultado final normal: ',binario
#print 'Descompresion:\n\"', cmpr.descomprimirTexto(binario), '\"'


