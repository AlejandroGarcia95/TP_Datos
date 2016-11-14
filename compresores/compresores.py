#!/usr/bin/env python
# -*- coding: utf-8 -*-

from parseo import *
from heapq import *

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

class NodoHuffman:
	def __init__(self, izq = None, der = None):
		self.izq = izq
		self.der = der


class CompresorHuffman(CompresorEstatico):
	def __init__(self, modoParseo):
		CompresorEstatico.__init__(self, modoParseo)
		self.arbol = None

	
	def asignarCodigo(self, nodo, codigo = "", dic = {}):
		if isinstance(nodo[1].izq[1], NodoHuffman):
			self.asignarCodigo(nodo[1].izq, codigo + "0", dic)
		else:
			dic[nodo[1].izq[1]] = codigo + "0"

		if isinstance(nodo[1].der[1], NodoHuffman):
			self.asignarCodigo(nodo[1].der, codigo + "1", dic)
		else:
			dic[nodo[1].der[1]] = codigo + "1"
		
		return dic
			
	def obtenerArbol(self):
		heap = []
		
		for simbolo, frec in self.tabla.verItems():
			heap.append((frec, simbolo))

		heapify(heap)
		while len(heap) > 1:
			izq = heappop(heap)
			der = heappop(heap)		
			nodo = NodoHuffman(izq,der)
			heappush(heap, (izq[0] + der[0], nodo))

		return heappop(heap)

	def comprimirTexto(self, texto):
		
		codigo = ""
		self.arbol = self.obtenerArbol()
		
		dictSimb = self.asignarCodigo(self.arbol)
		# print dictSimb
		for simbolo in texto:
			codigo += dictSimb[simbolo]
		
		return codigo

	def descomprimirTexto(self, codigo):
		texto = ""
		finalAux = self.arbol[1]
		
		for bit in codigo:
			if bit == '0':
				finalAux = finalAux.izq[1]
				if isinstance(finalAux, basestring):
					texto += finalAux
					finalAux = self.arbol[1]
			else:
				finalAux = finalAux.der[1]
				if isinstance(finalAux, basestring):
					texto += finalAux
					finalAux = self.arbol[1]

		return texto
					
					
		

#Zona de tests
cmpr = CompresorAritmetico('letra')
texto = 'Desert loving in your eyes all the way If I listened to your lies would you say Im a man without conviction Im a man who doesnt know How to sell a contradiction You come and go You come and go Karma Karma Karma Karma Karma Chameleon You come and go You come and go Loving would be easy if your colors were like my dream Red, gold and green Red, gold and green Didnt hear your wicked words every day And you used to be so sweet I heard you say That my love was an addiction When we cling our love is strong When you go youre gone forever You string along You string along Karma Karma Karma Karma Karma Chameleon You come and go You come and go\0'
texto = 'I was unable to cope with what you said\nSometimes we need to be cruel to be kind\nChild that I was, could not see the reason\nFeelings I had were but sham and a lie?\n\nI have never forgotten your smile\nYour eyes, oh, Shamandalie\n\nTime went by, many memories died\nI\'m writing this down to ease my pain\n\nYou saw us always clearer than me\nHow we were never meant to be\nLove denied meant the friendship would die\nNow I have seen the light\nThese memories make me cry\0'
#texto = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890[]+*-¬|$&%()?°@\0'
#texto = 'AAAAABBBCC\0'
cmpr.parsearTexto(texto)
print  'A COMPRIMIR:\n\"', texto, '\"\ncon compresor aritmetico'
#binario = cmpr.comprimirTexto(texto)
binario = "0011101010101100010010010010111100110101101100100000100010000010101101000001001011010000000101011011101000000000110001101001101111101010010111010101100010000100111011111000000001101000010111101011011000010101000111100101010110010001001101111010010110100000101110010000100001000011100110111000111101010011111001100111100111011100101110100011000010001110110001111111111010111100100011000100001101111001111000101100100010011101010101011010001111101000100001011110001010100111011101010101001101000010011001000001011001011001111100100010101101000001101000010100110111101010011000001100101111110101101111011110100110110111010101101000100001001010111110101100001110010000101100110011000011000001110110011111111101011100001111100101110110001010001001001110001110011000111111100100100011010100101100010110100001100001100001010000011111100010100010110101100000010000101100000100001101011001010101111100000110101010111101101000111000010101101001101101011011010111000010100001011101111101010011101011011110100000011111100110100000111100110101000100001100000000001101111111011111000110110101000100000110100111100001111010011001101001000000101000001101110111100111111111011100011100101001010111111110011011111000010100111011000000110101111010111101101000000001110100001010101100000010000000001010010101100110110111001010000001011100110111011010000101000100001111100001000001000101111000110101001001101110100100110110010111110101011110000100110111100111001101111101111001011001100111111101111110000001111101010001111100001110011000001010100010001010100100101001111111010000010111010011000000110011000110101100110111001011111001100101110110010000010001011010111001000100011111110010000010100010010000101110011110011011011011110010101001100110111000100000001111110101011110001010010011011000110110010001011010110010100001010101110001101010001001111100100101000011111101010100001100000110111001010110110110110011101111111011100110000010111010001111001010011001110001100011100111011100111011011011001"
binario = "001110101010110001001001001011110011010110110010000010001001101010110100000011011111010110101110111100100101100001011101011000100111100111010001011011110100011110000101111001110000100111111100001111100110101011010010110000101111111111101011001110100111010101111010010101100101001101100100000100111101100101100011000000000000100001000111011010110101011010100011111001101000001000111100110111111000001101101010001000111100010110110101110100001100011100000101100011010100111011000011110010010111101000000101100010000110000001010111111011000100010000001110100101100111101011011100001010110010001010100111101111000001110010010001100111111011100000010010100111011110000101010001010101001101010111011000111010101001111001010001101010011001101010000010100101011001111110101010111000011111111011000101011011000001100011111011100000000001000110001100100000100011110111011011010000100100100110111110011110000100001011111011101001101100001000011000010110100000000111101000010111001101001101000111010000000110011011111100000111111100110101101110100001100101010111111001011000110110110100000011111101110011010101011101010100010011100100111010111010111011101101111011101100011111010010000101100001011110000111001101101011010101100011011110000101000110010100011110100110011111011111001010001011110111100110100110110010011111001001011010001101001110101101101010001101100101001001101001011100111010101001011110111011111100100111100110111010000011000101000100110111111010111000110110010110110111010011010001100010100100100101111100100101000011001001011000001100101001010111111011001001100101011101011011010101100010111010011101010110100100110100110000001110100111101110000111011001010010000100101011010100101111100010011000110000111100001101110111011001010111101111101110110111110000111110001111101100110101010110010001111011000100110001100010011111110110011010011100001111110011011100001111100110111111001011110110101100110000111100100111111101100110100000010001110000111000010010000001111011111101001"
print 'Resultado final normal: ',binario
print 'Descompresion:\n\"', cmpr.descomprimirTexto(binario), '\"'

#cmpr = CompresorHuffman('letra')
#cmpr.parsearTexto(texto)
#binario = cmpr.comprimirTexto(texto)
#final = cmpr.descomprimirTexto(binario)
#if (texto == final):
#	print "OK"
#print 'Resultado final normal: ',binario
#print 'Descompresion:\n\"', cmpr.descomprimirTexto(binario), '\"'

