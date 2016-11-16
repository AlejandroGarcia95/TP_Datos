#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Archivo donde se definen las clases de tabla de símbolos y de parser 
# de texto (clases encargadas del parseo). El compresor per se y 
# todas sus variantes está definido en el archivo compresores.py

# Listado común de definiciones/nomenclaturas:

# Distinguimos dos tareas que deben hacerse para comprimir las reviews.
# En primer lugar, el PARSEO de las reviews, que corresponde a recorrer
# las mismas, identificando los símbolos, y actualizando sus frecuencias
# en una tabla de símbolos. El parseo en sí no genera ninguna compresión
# (sólo actualiza probabilidades!). La COMPRESIÓN de una review implica
# que cada compresor utilice su "propia técnica" para generar un stream
# binario que represente al texto de la review. Para esto, usa las frec.
# registradas en su tabla de símbolos (frecuencias que surgieron del
# parseo de muchas reviews). En resumen, parsear correspondería a la primer
# pasada del compresor estático donde identifica los símbolos, y la
# compresión corresponde a la segunda pasada en la que se genera el binario
# PERO la gracia está en que ahora la primer pasada se hace sobre todos
# los reviews de un mismo tipo y la segunda pasada sobre cualquier review
# a clasificar.

# Símbolo: en este contexto, un símbolo es cada "elemento" dentro del
# texto de una review que el compresor (y el parser) pueden identificar
# como mínimos y distinguibles. Nosotros siempre trabajamos como símbolos
# a las letras, porque comprimiamos siempre "de a letras" de un archivo,
# pero para clasificar reviews seguramente las letras sean poco convenientes.
# Otras dos alternativas para probar de símbolos se me ocurren pueden
# ser palabras y n-gramas. Importante: un símbolo se detecta sobre el
# review ya procesado, por lo que deberemos aplicar antes sobre cada
# review un proceso de stemming, filtrado de palabras menos usadas, etc.


from collections import Counter


class SymbolTable:
	def __init__(self):
		self.simbolos = Counter()
		
	def agregarSimbolo(self, simbolo):
		self.simbolos[simbolo] = 1	
	
	def verCasosTotales(self):
		casosTotales = 0
		for x in self.simbolos.values():
			casosTotales += x
		return casosTotales
		
	def verSimbolos(self):
		return self.simbolos.keys()
	
	def aumentarFrecuencia(self, simbolo):
		if not self.simbolos.has_key(simbolo):
			self.agregarSimbolo(simbolo)
		else:
			self.simbolos[simbolo] += 1
	
	def combinar(self, otra):
		self.simbolos = self.simbolos + otra.simbolos
	
	def verFrecuencia(self, simbolo):
		if not self.simbolos.has_key(simbolo): #Agregar simbolo ?
			return 1
		else:
			return self.simbolos[simbolo]
	
	def setearFrecuencia(self, simb ,freq):
		self.simbolos[simb] = freq
	
	def verItems(self):
		return self.simbolos.items();
	
	def __str__(self):
		return str(self.simbolos.items())
	
	

		
