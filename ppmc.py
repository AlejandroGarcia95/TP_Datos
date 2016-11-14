#!/usr/bin/env python
#coding=utf-8

from comp_arit import *
from parseo import *

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
		
