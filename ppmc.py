#!/usr/bin/env python
#coding=utf-8

from comp_arit import *
from parseo import *

MODELO_MENOS_UNO = -1
ESCAPE_CODE = 'ESC'
MODELO_CERO = 0

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
		
		self.comp.terminar_compresion()
		
		return self.first + self.comp.obtener_codigo()
		
		
	def descomprimir(self, binario):
		u"""Descomprime usando la tabla de símbolos aprendida"""
		print 
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
	




class CompresorHibrido:
	u""" Compresor híbrido de órden parametrizable.
	
	Funciona como PPMC pero con las tablas estáticas. Si no se encuentra
	un contexto, se emite un ESC y se busca en el contexto de orden menor.
	Si se llega al orden 0 sin encontrar el caracter, se pasa a un modelo
	de orden -1 que contiene a todos los caracteres posibles.
	"""
	
	def __init__(self, ordenMax = 8):
		self.orden = ordenMax
		
		# Instancio un compresor
		self.comp = CompresorAritmetico()
		
		self.clean()
		
		
	def clean(self):
		u"""Limpia al compresor cualquier entrenamiento.
		
		Elimina todas las tablas de símbolos existentes, salvo la que
		corresponde al modelo de orden -1
		"""
		self.tablas = {}
		
		# Tabla de emergencia en caso de que un contexto no exista
		self.tabla_ESC = SymbolTable()
		self.tabla_ESC.agregarSimbolo(ESCAPE_CODE)
		
		# Tabla del modelo de orden -1
		modelo_n1 = SymbolTable()
		for i in range(0, 256):
			modelo_n1.agregarSimbolo(chr(i))
		self.tablas[MODELO_MENOS_UNO] = modelo_n1
		
		self.comp.clean()
		
	def entrenar(self, texto):	
		context = ''		
		for c in texto:			
			# Agrego el simbolo al contexto de orden 0
			if (not self.tablas.has_key(MODELO_CERO)):
				self.tablas[MODELO_CERO] = SymbolTable()
				self.tablas[MODELO_CERO].agregarSimbolo(ESCAPE_CODE)
			self.tablas[MODELO_CERO].aumentarFrecuencia(c)
			
			# Agrego el simbolo a cada contexto de orden mayor a 0
			for i in range(0, len(context)):
				l = len(context)
				act = context[l-i-1:]
					
				if (not self.tablas.has_key(act)):
					self.tablas[act] = SymbolTable()
					self.tablas[act].agregarSimbolo(ESCAPE_CODE)
				self.tablas[act].aumentarFrecuencia(c)
			
			if (len(context) < self.orden):
				context = context + c
			elif(self.orden == len(context) and self.orden > 0):
				context = context[1:len(context)] + c
			
		
	def comprimir(self, texto):
		context = ''	
		for c in texto:
			#print "COMPRIMO", c
			context_act = context
			
			# Primero trato de comprimir con el contexto mayor
			emitido = False
			while(len(context_act) > 0 and not emitido):
				if (context_act not in self.tablas):
					#print "CONTEXT NOT FOUND", context_act
					self.comp.comprimirSimbolo(ESCAPE_CODE, self.tabla_ESC)
					context_act = context_act[1:len(context_act)]
					
				elif (c not in self.tablas[context_act].verSimbolos()):
					#print "CHAR ", c, " NOT FOUND IN ", context_act
					self.comp.comprimirSimbolo(ESCAPE_CODE, self.tablas[context_act])
					context_act = context_act[1:len(context_act)]
				else:
					#print "CHAR ", c, " FOUND IN ", context_act
					self.comp.comprimirSimbolo(c, self.tablas[context_act])
					emitido = True
			
			if (not emitido):
				if (c not in self.tablas[MODELO_CERO].verSimbolos()):
					#print "CHAR ", c, " NOT FOUND IN ZERO"
					self.comp.comprimirSimbolo(ESCAPE_CODE, self.tablas[MODELO_CERO])
					self.comp.comprimirSimbolo(c, self.tablas[MODELO_MENOS_UNO])
				else:
					#print "CHAR ", c, " FOUND IN ZERO"
					#print self.tablas[MODELO_CERO].verCasosTotales()
					#print self.tablas[MODELO_CERO].verItems()
					self.comp.comprimirSimbolo(c, self.tablas[MODELO_CERO])
			
			if (len(context) < self.orden):
				context = context + c
			elif(self.orden == len(context) and self.orden > 0):
				context = context[1:len(context)] + c
		
		
		texto = self.comp.terminar_compresion()
		self.comp.clean()
		return texto
			
		
	def descomprimir(self, binario, n):
		""" Trata de descomprimir n caracteres del binario """
		count = 0		
		texto = ''
		context = ''
		deco = DecompresorAritmetico(binario)
		while (count < n):
			context_act = context
			#print context_act, context_act in self.tablas
			# Primero trato de comprimir con el contexto mayor
			emitido = False
			while(len(context_act) > 0 and not emitido):
				
				if (context_act not in self.tablas):
					#print "CONTEXT NOT FOUND", context_act
					simb = deco.decomprimirSimbolo(self.tabla_ESC)
					if (not simb == ESCAPE_CODE):
						print "ERROR: EXPECTED EOF"
					context_act = context_act[1:len(context_act)]
				else:
					simb = deco.decomprimirSimbolo(self.tablas[context_act])
					if (simb == ESCAPE_CODE):
						#print "FOUND CONTEXT, GOT ESC", context_act
						context_act = context_act[1:len(context_act)]
					else:
						#print "FOUND CONTEXT, GOT CHAR", context_act, simb
						texto += simb
						count += 1
						emitido = True
			
			if (not emitido):
				#print "TRYING MODEL ZERO"
				#print self.tablas[MODELO_CERO].verItems()
				simb = deco.decomprimirSimbolo(self.tablas[MODELO_CERO])
				if (simb == ESCAPE_CODE):
					#print "GOT ESC, TRY MODEL -1"
					simb = deco.decomprimirSimbolo(self.tablas[MODELO_MENOS_UNO])
					
				#print "GOT", simb
				texto += simb
				count += 1
				emitido = True
			
			if (len(context) < self.orden):
				context = context + simb
			elif(self.orden == len(context) and self.orden > 0):
				context = context[1:len(context)] + simb
		
		return texto
		
		
	def testearCompresion(self, texto):
		u"""Test de compresión correcta para un dado texto
		
		IMPORTANTE: el compresor debe entrenarse previamente, de lo
		contrario siempre emitirá caracteres del modelo -1
		"""
		binario = self.comprimir(texto)
		texto_descomp = self.descomprimir(binario, len(texto))
		return (texto_descomp == texto)
		
	def ratioCompresion(self, texto):
		u"""Devuelve el ratio de compresión para un texto en particular
		
		IMPORTANTE: el compresor debe entrenarse previamente, de lo
		contrario siempre emitirá caracteres del modelo -1
		"""
		binario = self.comprimir(texto)
		l = len(texto)
		b = float(len(binario))/8
		return b/l


