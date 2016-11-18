#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
from scipy import optimize
from basicSVM import *

# El MulticatSVM funciona de forma similar al SVM básico, pero siendo
# capaz de clasificar enésimas categorías. 

class MulticatSVM:
	# Crea el MulticatSVM. Es necesario especificar la dimensión de los datos,
	# la cte C de soft margin (en floating point) y la cant. de categorias.
	def __init__(self, dim, cte_soft_margin, cantCategorias):
		self.dimension = dim
		self.C = cte_soft_margin
		self.categorias = cantCategorias
		self.resultados = 0
		self.kernel = np.dot
		self.sigma = 0.5
		self.delta_C = self.delta_C_lineal
		self.criterio = self.criterio_lineal
	
	# Función que determina si se va a usar o no un kernel específico.
	# Si no se la llama antes del método entrenar, el kernel por defecto
	# es el "linear" (es decir, no hay kernel).
	# Si kernel_func es "linear" o "gaussian", se utiliza ese kernel. El
	# valor de sigma puede ser usado para settear el sigma del kernel
	# gaussiano (si no se usa ese kernel, dicho valor no sirve para nada).
	# Si se desea usar cualquier otra función de kernel externa, puede
	# pasarse a ésta misma a través de kernel_func.
	# La función criterio_func es una función usada en la predicción.
	# Básicamente, la función recibe como parámetro el resultado de la
	# cuenta <w, x> + k  y debe devolver un número mayor a 0 si el x
	# pertenece a la categoría A que divide ese hiperplano o menor a 0
	# si pertenece a la categoría B (ídem como en el SVM básico).
	# La función criterio por defecto es self.criterio_lineal.
	def usar_kernel(self, kernel_func, criterio_func, sigma=0.5):
		self.sigma = sigma
		self.criterio = criterio_func
		if(kernel_func == "linear"):
			self.kernel = np.dot
		elif(kernel_func == "gaussian"):
			self.kernel = self.kernel_gaussiano
		else:
			self.kernel = kernel_func
	
	# Asigna una función delta_C al MulticatSVM. La función delta_C
	# indica cuánto debe variar la cte de soft margin en el cálculo de
	# cada hiperplano. Por ejemplo, si inicialmente C = 100 y se usa
	# delta_C_fun = 0.5*C entonces el primer hiperplano se calculará
	# con C=100, el segundo con C=50, el tercero con C=25 y así.
	# Si no se llama a este método antes del método entrenar, la función
	# delta_C por defecto es self.delta_C_lineal.
	def asignar_delta_C(self, delta_C_func):
		self.delta_c = delta_C_func	
		
	# Kernel gaussiano pre-disponible para el MulticatSVM.
	# Propiedad de Alejandro García, no tocar.	
	def kernel_gaussiano(x, y):
		s = self.sigma
		dist = np.linalg.norm(x - y)
		return np.exp((-0.5 * dist * dist) / (s * s) )
	
	# Entrena al MulticatSVM con los datos recibidos. Los datos deben respetar
	# el siguiente formato loco: datos es una lista de listas de numpy.vector
	# en floating point. Cada una de estas sublistas con numpy.vector corresponde
	# a los datos de una determinada categoría. Por ejemplo, si datos es:
	# [ [A, B, C] , [D, E, F, G, H] , [I, J], [K, L, M] ] quiere decir que hay
	# cuatro categorías y que A,B,C corresponden a la categoría 1, I,J a la 3, etc.
	# Notar que las categorías se numeran como 1, 2, 3,...
	# Los hiperplanos resultantes se guardan en self.resultados en el sgte
	# formato: una lista de tuplas (w, k), donde w es la normal del hiperplano
	# y k su cte según la nomenclatura del SVM básico. 	
	def entrenar(self, datos):
		if(len(datos) != self.categorias):
			print "Fatal error: category amount mismatched!"
			return
		self.resultados = []
		for k in range(0, self.categorias-1):
			catA = datos[k]
			catB = []
			for i in datos[k+1::]:
				catB.extend(i)
			# Entreno el SVM básico como una categoría vs. todas las demás
			basicSVM = SVM(dim = self.dimension, cte_soft_margin = self.C, kernel_func = self.kernel)
			basicSVM.entrenar(datos_claseA = catA, datos_claseB = catB)
			self.resultados.insert(0, basicSVM.devolver_hiperplano())
			self.C = self.delta_C(self.C)
		#print self.resultados
	
	# Función delta_C por defecto. Cambiar 0.55 por 1? Sólo puedo decir que 0.55 me funcionó relativamente bien
	def delta_C_lineal(self, viejoC):
			return viejoC * 0.55
	
	
	def criterio_lineal(self, producto):
		return producto		
	
	# Predice la categoría del nuevoDato, devolviendo un valor.
	# IMPORTANTE: nuevoDato debe ser de clase numpy.vector, y tiene
	# que ser vector del dato EN FLOATING POINT
	def predecir(self, nuevoDato):
		for i in range(0, self.categorias-1):
			aux = np.append(nuevoDato, 1.0)
			hiperplano = np.copy(self.resultados[i][0])
			hiperplano = np.append(hiperplano, self.resultados[i][1])
			elResult = self.kernel(aux, hiperplano)
			if(self.criterio_lineal(elResult) > 0):
				return i+1
		return self.categorias
	

	

# Zona de tests:
"""
def kernel_gaussiano(x, y):
	sigma = 0.15
	dist = np.linalg.norm(x - y)
	return np.exp((-0.5 * dist * dist) / (sigma * sigma) )

our_svm = MulticatSVM(dim = 2, cte_soft_margin = 9000.0, cantCategorias = 4)

azules = []
azules.append(np.array([0.00, 4.00]))
azules.append(np.array([-1.00, 4.30]))
azules.append(np.array([-1.20, 3.80]))
azules.append(np.array([0.50, 5.00]))
azules.append(np.array([-0.25, 4.75]))
azules.append(np.array([1.00, 5.50]))
azules.append(np.array([-1.00, 5.60]))
azules.append(np.array([-2.10, 5.30]))
azules.append(np.array([0.80, 4.30]))
azules.append(np.array([-0.60, 3.60]))

 
rojos = []
rojos.append(np.array([-5.00, -4.00]))
rojos.append(np.array([-3.70, -2.90]))
rojos.append(np.array([-4.00, -1.00]))
rojos.append(np.array([-4.50, -2.50]))
rojos.append(np.array([-5.20, 2.20]))
rojos.append(np.array([-5.00, 0.50]))
rojos.append(np.array([-4.50, 2.50]))
rojos.append(np.array([-4.80, -1.80]))
rojos.append(np.array([-4.00, 1.00]))
rojos.append(np.array([-5.00, -1.00]))
rojos.append(np.array([-4.60, 1.30]))

verdes = []
verdes.append(np.array([2.00, -3.50]))
verdes.append(np.array([3.00, -4.00]))
verdes.append(np.array([0.50, -4.10]))
verdes.append(np.array([3.30, -3.60]))
verdes.append(np.array([1.50, -4.50]))
verdes.append(np.array([1.10, -5.10]))
verdes.append(np.array([2.60, -4.60]))
verdes.append(np.array([4.00, -4.40]))
verdes.append(np.array([1.30, -3.00]))


violetas = []
violetas.append(np.array([5.10, 0.50]))
violetas.append(np.array([3.80, -0.10]))
violetas.append(np.array([4.10, 1.20]))
violetas.append(np.array([3.50, 2.00]))
violetas.append(np.array([4.20, -0.70]))
violetas.append(np.array([4.60, 1.10]))
violetas.append(np.array([4.40, 0.10]))
violetas.append(np.array([5.10, -0.40]))
violetas.append(np.array([5.30, 1.80]))
violetas.append(np.array([5.50, -1.40]))

puntos = []
puntos.append(azules)
puntos.append(rojos)
puntos.append(verdes)
puntos.append(violetas)

our_svm.entrenar(puntos) 

# Azul > 0, Rojo < 0	
print "Prediccion de los puntos marrones" 
print "(Azul = 1, Rojo = 2, Verde = 3, Violeta = 4)\n"
print "(0.2, 3.8): ", our_svm.predecir(np.array([0.2, 3.8]))
print "(1.1, -2.2): ", our_svm.predecir(np.array([1.1, -2.2]))
print "(3.2, 1.4): ", our_svm.predecir(np.array([3.2, 1.4]))
print "(-3.0, -3.0): ", our_svm.predecir(np.array([-3.0, -3.0]))
print "(2.0, 5.0): ", our_svm.predecir(np.array([2.0, 5.0]))
print "(4.5, 2.5): ", our_svm.predecir(np.array([4.5, 2.5]))
print "(-3.0, 2.0): ", our_svm.predecir(np.array([-3.0, 2.0]))
print "(-0.1, -2.9): ", our_svm.predecir(np.array([-0.1, -2.9]))
print "(1.5, 3.5): ", our_svm.predecir(np.array([1.5, 3.5]))
print "(-3.1, 0.0): ", our_svm.predecir(np.array([-3.1, 0.0]))
"""


