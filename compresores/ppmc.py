#!/usr/bin/env python
#coding=utf-8

from parseo import *

MAX_INT =    0xFFFFFFFFF	
MIN_INT =    0x000000000
FIRST_QUAD = 0x400000000
HALF_INT = 	 0x800000000
THIRD_QUAD = 0xc00000000
INT_BITS = 36

class CompresorAritmetico:
	
	def __init__(self):
		self.codigo = ''
		self.intInferior = MIN_INT
		self.intSuperior = MAX_INT
		self.E3count = 0
	
	def comprimirSimbolo(self, c, tabla):
		casosTotales = tabla.verCasosTotales()
		simbolos = tabla.verSimbolos()
		
		simbolos.sort()
		
		if (len(simbolos) == 1):
			#print c, (float(self.intInferior)/MAX_INT, float(self.intSuperior)/MAX_INT), len(simbolos), casosTotales
			return
		
		longMinima = (self.intSuperior - self.intInferior) / casosTotales
		resto = (self.intSuperior - self.intInferior) - (longMinima * casosTotales)
		intAcumulado = self.intInferior
		
		if (not c in simbolos):
			print "ERROR AL COMPRIMIR: SIMBOLO NO ENCONTRADO EN LA TABLA"
			return
			
		for simb in simbolos:
			if (simb == c):
				self.intInferior = intAcumulado
				self.intSuperior = intAcumulado + (tabla.verFrecuencia(simb) * longMinima)
				
				#print simb, (float(intAcumulado)/MAX_INT, float(self.intSuperior)/MAX_INT), len(simbolos), casosTotales
				
				
				# Testeo por redimensión
				E1_resize = self.intInferior < HALF_INT and self.intSuperior < HALF_INT
				E2_resize = self.intInferior >= HALF_INT and self.intSuperior >= HALF_INT
				E3_resize = self.intInferior >= FIRST_QUAD and self.intSuperior < THIRD_QUAD
				

				# Testeo por redimensión tipo E1-E2
				# Si ambos límites pasan a estar en la misma mitad
				while(E1_resize or E2_resize or E3_resize):
						
					E3bit = '0'
					if(E1_resize):
						self.codigo += '0'
						E3bit = '1'
						self.intInferior = self.intInferior * 2
						self.intSuperior = self.intSuperior * 2 + 1
						while (self.E3count > 0):
							self.codigo += E3bit
							self.E3count -= 1						
					elif(E2_resize):
						self.codigo += '1'
						E3bit = '0'
						self.intInferior = (self.intInferior - HALF_INT) * 2
						self.intSuperior = (self.intSuperior - HALF_INT) * 2 + 1
						while (self.E3count > 0):
							self.codigo += E3bit
							self.E3count -= 1	
					elif (E3_resize):
						self.E3count += 1
						self.intInferior = (self.intInferior - FIRST_QUAD) * 2
						self.intSuperior = (self.intSuperior - FIRST_QUAD) * 2 + 1	

					E3_resize = self.intInferior >= FIRST_QUAD and self.intSuperior < THIRD_QUAD					
					E1_resize = self.intInferior < HALF_INT and self.intSuperior < HALF_INT
					E2_resize = self.intInferior >= HALF_INT and self.intSuperior >= HALF_INT

				return	
				
			else:
				intAcumulado += (tabla.verFrecuencia(simb) * longMinima)
		
		print "ERROR AL COMPRIMIR: NO SE COMPRIMIO NINGUN SIMBOLO"



	def obtener_codigo(self):
		# Completo codificando el último intervalo a binario
		
		valorBin = MIN_INT
		i = 1
		lastBits = ''

		while((valorBin <= self.intInferior) or (valorBin >= self.intSuperior)):
			aux = HALF_INT >> (i-1)
			if((valorBin + aux) >= self.intSuperior):
				lastBits += '0'
			else:
				lastBits += '1'
				valorBin += aux
			i += 1
			
		E3bit = '1'
		if (valorBin < HALF_INT):
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
		self.value = MIN_INT
		for i in range(0, INT_BITS):
			self.value = self.value << 1
			self.readNext()
		
	#def getInterval(self):
	#	return (self.lower, self.upper)
	
	def getValue(self):
		return self.value
	
	def getWidth(self):
		return (self.upper - self.lower)
		
	def print_float(self):
		print (float(self.lower)/MAX_INT, float(self.upper)/MAX_INT)
		
	def readNext(self):
		try:
			act = self.it.next()
		except StopIteration:
			#print "WARNING: READING MORE BITS"
			act = '0'
			
		if (act == '1'):
			self.value += 1		
		
	def reduce_E1(self):
		self.value = self.value * 2
		self.readNext()
	
	def reduce_E2(self):
		self.value = (self.value - HALF_INT) * 2
		self.readNext()
	
	def reduce_E3(self):
		self.value = (self.value - FIRST_QUAD) * 2
		self.readNext()
	
	
class DecompresorAritmetico:
	def __init__(self, codigo):
		self.intInferior = MIN_INT
		self.intSuperior = MAX_INT
		self.deco = Decodificador(codigo)
		
	def getInterval(self):
		return (self.intInferior, self.intSuperior)
				
				
	def decomprimirSimbolo(self, tabla):
		casosTotales = tabla.verCasosTotales()
		simbolos = tabla.verSimbolos()
		
		simbolos.sort()
				
		if (len(simbolos) == 1):
			#print simbolos[0], (float(self.intInferior)/MAX_INT, float(self.intSuperior)/MAX_INT), len(simbolos), casosTotales
			return simbolos[0]
		
		longMinima = (self.intSuperior - self.intInferior) / casosTotales
		resto = (self.intSuperior - self.intInferior) - (longMinima * casosTotales)
		intAcumulado = self.intInferior
		decode = ''
		
		target = self.deco.getValue()
		
		for simb in simbolos:
			self.intSuperior = intAcumulado + (tabla.verFrecuencia(simb) * longMinima)
			
			
			if ((target >= intAcumulado) and (target < self.intSuperior)):
				
				#print simb, (float(intAcumulado)/MAX_INT, float(self.intSuperior)/MAX_INT), len(simbolos), casosTotales
				decode = simb
					
				self.intInferior = intAcumulado
				
						
				# Testeo por redimensión
				E1_resize = self.intInferior < HALF_INT and self.intSuperior < HALF_INT
				E2_resize = self.intInferior >= HALF_INT and self.intSuperior >= HALF_INT
				E3_resize = self.intInferior >= FIRST_QUAD and self.intSuperior < THIRD_QUAD
				
				while(E1_resize or E2_resize or E3_resize):
					if(E1_resize):
						self.intInferior = self.intInferior * 2
						self.intSuperior = self.intSuperior * 2 + 1
						self.deco.reduce_E1()
					elif(E2_resize):
						self.intInferior = (self.intInferior - HALF_INT) * 2
						self.intSuperior = (self.intSuperior - HALF_INT) * 2 + 1
						self.deco.reduce_E2()
					elif(E3_resize):
						self.deco.reduce_E3()
						self.intInferior = (self.intInferior - FIRST_QUAD) * 2
						self.intSuperior = (self.intSuperior - FIRST_QUAD) * 2 + 1
				
					E3_resize = self.intInferior >= FIRST_QUAD and self.intSuperior < THIRD_QUAD
					E1_resize = self.intInferior < HALF_INT and self.intSuperior < HALF_INT
					E2_resize = self.intInferior >= HALF_INT and self.intSuperior >= HALF_INT
						
				return decode
			
			intAcumulado = self.intSuperior
		
		print "ERROR AL DESCOMPRIMIR: NO SE PUDO DESCOMPRIMIR"
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
		
