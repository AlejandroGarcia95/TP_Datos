#!/usr/bin/env python
#coding=utf-8

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
	
	def clean(self):
		self.codigo = ''
		self.intInferior = MIN_INT
		self.intSuperior = MAX_INT
		self.E3count = 0		
	
	def emit(self, bit):
		if (bit == 0):
			self.codigo += '0'
		else:
			self.codigo += '1'
	
	def comprimirSimbolo(self, c, tabla):
		casosTotales = tabla.verCasosTotales()
		simbolos = tabla.verSimbolos()
		
		simbolos.sort()
		
		if (len(simbolos) == 1):
			return
		
		longMinima = (self.intSuperior - self.intInferior) / casosTotales
		
		# Posibilidad de usar el resto para optimizar?
		#resto = (self.intSuperior - self.intInferior) - (longMinima * casosTotales)
		
		if (not c in simbolos):
			print "ERROR AL COMPRIMIR: SIMBOLO NO ENCONTRADO EN LA TABLA"
			return
			
		for simb in simbolos:
			if (simb == c):
				self.intSuperior = self.intInferior + (tabla.verFrecuencia(simb) * longMinima)
				
				# Testeo por redimensión
				E1_resize = self.intInferior < HALF_INT and self.intSuperior < HALF_INT
				E2_resize = self.intInferior >= HALF_INT and self.intSuperior >= HALF_INT
				E3_resize = self.intInferior >= FIRST_QUAD and self.intSuperior < THIRD_QUAD

				while(E1_resize or E2_resize or E3_resize):
					E3bit = 0
					if(E1_resize):
						self.emit(0)
						E3bit = 1
						self.intInferior = self.intInferior * 2
						self.intSuperior = self.intSuperior * 2 + 1
						while (self.E3count > 0):
							self.emit(E3bit)
							self.E3count -= 1			
					elif(E2_resize):
						self.emit(1)
						E3bit = 0
						self.intInferior = (self.intInferior - HALF_INT) * 2
						self.intSuperior = (self.intSuperior - HALF_INT) * 2 + 1
						while (self.E3count > 0):
							self.emit(E3bit)
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
				self.intInferior += (tabla.verFrecuencia(simb) * longMinima)
		
		print "ERROR AL COMPRIMIR: NO SE COMPRIMIO NINGUN SIMBOLO"

	def terminar_compresion(self):
		# Completo codificando el último intervalo a binario
		valorBin = MIN_INT
		i = 1
		lastBits = ''

		while((valorBin <= self.intInferior)):# or (valorBin >= self.intSuperior)):
			aux = HALF_INT >> (i-1)
			if((valorBin + aux) >= self.intSuperior):
				lastBits += '0'
			else:
				lastBits += '1'
				valorBin += aux
			i += 1
			
		E3bit = 1
		if (valorBin < HALF_INT):
			E3bit = 0
			
		if (self.E3count > 0):
			self.emit(E3bit)
			while (self.E3count > 0):
				self.E3count -= 1
				if (E3bit == 0):
					self.emit(1)
				else:
					self.emit(0)
			#lastBits += lastBits[1:len(lastBits)]
			
		for c in lastBits:
			if (c == '0'):
				self.emit(0)
			else:
				self.emit(1)
	
		return self.codigo
		
	def obtener_codigo(self):
		return self.codigo
		
class Decodificador:
	def __init__(self, codigo):
		self.it = iter(codigo)
		self.value = MIN_INT
		for i in range(0, INT_BITS):
			self.value = self.value << 1
			self.readNext()
	
	def getValue(self):
		return self.value
		
	def print_float(self):
		print (float(self.lower)/MAX_INT, float(self.upper)/MAX_INT)
		
	def readNext(self):
		try:
			act = self.it.next()
		except StopIteration:
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
		self.cuenta = 0
		self.texto = ''
			
	def getInterval():
		return (float(self.intInferior)/MAX_INT, float(self.intSueprior)/MAX_INT)
		
	def getText():
		return self.texto
		
	def getCount():
		return self.cuenta
		
	def emitirSimbolo(self, simb):
		self.texto += simb
		self.cuenta += 1
		return simb
				
	def decomprimirSimbolo(self, tabla):
		casosTotales = tabla.verCasosTotales()
		simbolos = tabla.verSimbolos()
		
		simbolos.sort()
				
		if (len(simbolos) == 1):
			return self.emitirSimbolo(simbolos[0])
		
		longMinima = (self.intSuperior - self.intInferior) / casosTotales
		# Posibilidad de usar el resto para optimizar
		#resto = (self.intSuperior - self.intInferior) - (longMinima * casosTotales)
				
		target = self.deco.getValue()
		
		for simb in simbolos:
			self.intSuperior = self.intInferior + (tabla.verFrecuencia(simb) * longMinima)
			print simb, " --- ", self.intInferior, self.intSuperior
			
			if ((target >= self.intInferior) and (target < self.intSuperior)):
							
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
						
				return self.emitirSimbolo(simb)
			
			self.intInferior += (tabla.verFrecuencia(simb) * longMinima)
		
		print "ERROR AL DESCOMPRIMIR: NO SE PUDO DESCOMPRIMIR"
		return ''
		
