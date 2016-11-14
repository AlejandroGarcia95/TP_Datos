#!/usr/bin/env python
#coding=utf-8

from parseo import *

class CompresorAritmetico:
	def __init__(self):
		self.codigo = ''
		self.intInferior = 0.0
		self.intSuperior = 1.0
		self.E3count = 0
	
	def comprimirSimbolo(self, c, tabla):
		casosTotales = tabla.verCasosTotales()
		simbolos = tabla.verSimbolos()
		longMinima = 1.0 / float(casosTotales)
		
		simbolos.sort()
		longMinima = (self.intSuperior - self.intInferior) / float(casosTotales)
		intAcumulado = self.intInferior
		if (not c in simbolos):
			print "ERROR"
			return
		for simb in simbolos:
			if (simb == c):
				self.intInferior = intAcumulado
				self.intSuperior = intAcumulado + (tabla.verFrecuencia(simb) * longMinima)
				
				# Testeo por redimensión tipo E1-E2
				# Si ambos límites pasan a estar en la misma mitad
				intInfRounded = int(self.intInferior * 2)
				intSupRounded = int(self.intSuperior * 2)
				while(intInfRounded == intSupRounded):
					self.codigo += str(intInfRounded)
					while (self.E3count > 0):
						self.E3count -= 1
						if (intInfRounded == 0):
							self.codigo += str(1)
						else:
							self.codigo += str(0)
					self.intInferior *= 2
					self.intInferior -= intInfRounded
					self.intSuperior *= 2
					self.intSuperior -= intSupRounded
					intInfRounded = int(self.intInferior * 2)
					intSupRounded = int(self.intSuperior * 2)
					
				# Testeo por redimensión tipo E3
				while ((self.intInferior >= 0.25) and (self.intSuperior < 0.75)):
					self.E3count += 1
					self.intInferior -= 0.25
					self.intInferior *= 2
					self.intSuperior -= 0.25
					self.intSuperior *= 2
			else:
				intAcumulado += (tabla.verFrecuencia(simb) * longMinima)


	def obtener_codigo(self):
		# Completo codificando el último intervalo a binario
		
		valorBin = 0.0
		i = 1
		lastBits = ''

		while((valorBin <= self.intInferior) or (valorBin >= self.intSuperior)):
			aux = 1.0/(2**i)
			if((valorBin + aux) >= self.intSuperior):
				lastBits += '0'
			else:
				lastBits += '1'
				valorBin += aux
			i += 1
			
		E3bit = '1'
		if (valorBin < 0.5):
			E3bit = '0'
			
		if (self.E3count > 0):
			self.codigo += E3bit
			while (self.E3count > 0):
				self.E3count -= 1
				if (E3bit == '0'):
					self.codigo += str(1)
				else:
					self.codigo += str(0)
			self.codigo += lastBits[1:len(lastBits)]
		else:
			self.codigo += lastBits
		return self.codigo

class Decodificador:
	def __init__(self, codigo):
		self.it = iter(codigo)
		self.lower = 0.0
		self.upper = 1.0
		self.count = 1
		self.readNext
		
	def getInterval(self):
		return (self.lower, self.upper)
		
	def getWidth(self):
		return (self.upper - self.lower)
		
	def readNext(self):
		try:
			act = self.it.next()
		except StopIteration:
			act = '0'
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
		
	def reduce_E3(self):
		self.upper -= 0.25
		self.upper *= 2
		self.lower -= 0.25
		self.lower *= 2
		self.count -= 1
		
class DecompresorAritmetico:
	def __init__(self, codigo):
		self.intInferior = 0.0
		self.intSuperior = 1.0
		self.deco = Decodificador(codigo)
		
	def verIntervalo(self):
		return self.deco.getInterval()
		
	def decomprimirSimbolo(self, tabla):
		casosTotales = tabla.verCasosTotales()
		simbolos = tabla.verSimbolos()
		longMinima = 1.0 / float(casosTotales)
		
		simbolos.sort()
		
		
		if (len(simbolos) == 1):
			return simbolos[0]
		
		intAcumulado = self.intInferior
		longMinima = (self.intSuperior - self.intInferior) / float(casosTotales)
		decode = ''

		for simb in simbolos:
			self.intSuperior = intAcumulado + (tabla.verFrecuencia(simb) * longMinima)
			rango = self.deco.getInterval()
			
			if ((rango[0] >= intAcumulado) and (rango[0] < self.intSuperior)):
				
				while((rango[1] >= self.intSuperior) and (rango[0] < self.intSuperior)):
					self.deco.readNext()
					rango = self.deco.getInterval()
				
				if((rango[0] >= intAcumulado) and (rango[0] < self.intSuperior)):
					decode = simb
					
					#print 'Emito ', simb
					self.intInferior = intAcumulado
				
					# Redimensión del intervalo, caso E1-E2
					# (inf y sup en la misma mitad)
					while(int(self.intInferior * 2) == int(self.intSuperior * 2)):
						self.deco.reduce()
						self.intInferior *= 2
						self.intInferior -= int(self.intInferior)
						self.intSuperior *= 2
						self.intSuperior -= int(self.intSuperior)
						
					# Caso E3
					# Ambos límites del intervalo convergen al centro,
					# pero sup-inf ocupa menos de la mitad del intervalo
					while ((self.intInferior >= 0.25) and (self.intSuperior < 0.75)):
						self.deco.reduce_E3()
						self.intInferior -= 0.25
						self.intInferior *= 2
						self.intSuperior -= 0.25
						self.intSuperior *= 2
					break
			intAcumulado += (tabla.verFrecuencia(simb) * longMinima)
		
		return decode

class CompresorEstatico:
	u"""Compresor aritmético estático de orden parametrizable."""
	
	def __init__(self, orden=8):
		self.tablas = {}
		self.orden = orden
		self.first = ''
		self.comp = CompresorAritmetico()
	
	def entrenar(self, texto):
		u"""Solo actualiza las frecuencias.
	
		Parsea el texto de entrada actualizando para cada contexto la
		frecuencia de los caracteres observados. No realiza compresión."""
		self.first = texto[0:self.orden]
		
		context = self.first
		
		for c in texto[self.orden:len(texto)]:
			if (not self.tablas.has_key(context)):
				self.tablas[context] = SymbolTable()
			self.tablas[context].aumentarFrecuencia(c)
			if not (self.orden == 0):
				context = context[1:len(context)] + c
			
	def comprimir(self, texto):
		u"""Comprime el texto sin alterar la tabla de símbolos."""
		
		self.first = texto[0:self.orden]
		context = self.first
		
		for c in texto[self.orden:len(texto)]:
			self.comp.comprimirSimbolo(c, self.tablas[context])
			if not (self.orden == 0):
				context = context[1:len(context)] + c
				
		return self.first + self.comp.obtener_codigo()
		
		
	def descomprimir(self, binario):
		u"""Descomprime usando la tabla de símbolos aprendida"""
		texto = binario[0:self.orden]
		context = texto
		
		codigo = binario[self.orden:len(binario)]
		decom = DecompresorAritmetico(codigo)
		end = False
		count = 0
		while not end:
			leido = decom.decomprimirSimbolo(self.tablas[context])
			if (leido == '\0'):
				end = True
			texto = texto + leido
			if not (self.orden == 0):
				context = context[1:len(context)] + leido
			count += 1
			#if count > 1000:
			#	end = True
		return texto

texto = 'I was unable to cope with what you said\nSometimes we need to be cruel to be kind\nChild that I was, could not see the reason\nFeelings I had were but sham and a lie?\n\nI have never forgotten your smile\nYour eyes, oh, Shamandalie\n\nTime went by, many memories died\nI\'m writing this down to ease my pain\n\nYou saw us always clearer than me\nHow we were never meant to be\nLove denied meant the friendship would die\nNow I have seen the light\nThese memories make me cry\0'
print texto
print "-----"

file = open("sonata.txt")
texto = ''
for line in file:
	texto += line
texto += '\0'

cmpr = CompresorEstatico(0)
cmpr.entrenar(texto)
binario = cmpr.comprimir(texto)
print binario
print "\n"
texto2 = cmpr.descomprimir(binario)
print texto2
print "------"

if (texto2 == texto):
	print "SUCCESS!!!"
else:
	print "ERROR"
