#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
from scipy import optimize

# La clase SVM se entrena para poder diferenciar entre dos categorías distintas de 
# datos, que se referencian con dos posibles resultados +1 o -1. Una vez recibidos 
# los datos del set de prueba, el SVM busca el mejor hiperplano en la dimensión de 
# los datos que genere esta división en dos clases. Este hiperplano es de la forma
# <w, x> + k = 0	donde w es la normal del hiperplano, k una cte y x el vector
# genérico (x1, x2, ...) con la dimensionalidad de los datos.
# Luego de su entrenamiento, SVM puede predecir la categoría de un nuevo dato v según
# de qué lado del hiperplano anterior quedó. Así, la categoría de v puede estimarse
# como signo(<w, v> + k). El entrenamiento entonces del SVM consiste en hallar w y k
# para que el hiperplano <w, x> + k = 0 clasifique bien al set de entrenamiento.
# El modelo de programación lineal cuadrática usado para esto es el sgte: 

#	Función objetivo:
#		min ||w||**2
#	sujeto a:
#		yi (<w, xi> + k)-1 >= 0	para todo dato xi, donde yi es su categoría (1 ó -1)		
# Observar que las restricciones pueden escribirse como:
# 		yi <w, xi> >= 1 - k yi
# Es decir, las restricciones son lineales. Se las plantea así genéricamente como
# Ax <= b	donde A es la matriz de los datos signados según su categoría. 


# Nomenclatura: Clase "A" es la positiva (+1) y clase "B" la negativa (-1)

class SVM:
	# Crea el SVM. Es necesario especificar la dimensión de los datos
	def __init__(self, dim):
		self.dimension = dim
		self.resultados = 0
	
	# Define la función objetivo del modelo de PLC
	def funcion_objetivo(self, x, sign = 1.0):
		norma_w = 0.0
		for i in range(0, self.dimension):
			norma_w += (x[i]*x[i])
		return sign * norma_w
    
    # Define el gradiente a usar para el método de resolución de PLC
    # (básicamente, son las derivadas parciales de la función objetivo)
	def funcion_jac(self, x, sign = 1.0):
		p = np.copy(x.T)
		p[self.dimension] = 0.0
		return sign * p
	
	# Genera la matriz A de restricciones del modelo de PLC
	def generar_matriz_A(self, datos_claseA, datos_claseB):
		A = np.array([])
		nuevoDato = np.array([])
		# Cargo el primer dato en la matriz A para que no esté vacía
		for x in range(0, self.dimension):
			nuevoDato = np.append(nuevoDato, datos_claseB[x])
		nuevoDato = np.append(nuevoDato, 1.0)
		A = np.append(A, nuevoDato)
		A = np.array([A])
		# Concateno en la matriz A todos los demás elementos de claseB
		offset = self.dimension
		while offset < len(datos_claseB):
			nuevoDato = np.array([])
			for x in range(offset, offset + self.dimension):
				nuevoDato = np.append(nuevoDato, datos_claseB[x])
			nuevoDato = np.append(nuevoDato, 1.0)
			A = np.concatenate((A, np.array([nuevoDato])))
			offset += self.dimension
		# Concateno en la matriz A todos los elementos de claseA
		offset = 0
		while offset < len(datos_claseA):
			nuevoDato = np.array([])
			for x in range(offset, offset + self.dimension):
				nuevoDato = np.append(nuevoDato, -1.0*datos_claseA[x])
			nuevoDato = np.append(nuevoDato, -1.0)
			A = np.concatenate((A, np.array([nuevoDato])))
			offset += self.dimension
		return A

	def generar_vector_b(self, datos_claseA, datos_claseB):
		b = np.array([])
		cantDatos = (len(datos_claseB)+len(datos_claseA))/self.dimension
		for x in range(0, cantDatos):
			b = np.append(b, -1.0)
		return b 
		
	# Entrena al SVM con el set de datos recibido. Esta función
	# guarda en el atributo resultados toda la información del
	# optimize de scipy. Los primeros self.dimension valores de
	# resultados.x corresponden al vector w, mientras que el último
	# valor del mismo campo corresponde a k del hiperplano.
	# IMPORTANTE: Los datos recibidos deben respetar el sgte formato:
	# deben ser cada uno una lista de vectores numpy.vector EN FORMATO
	# FLOATING POINT de la dimensión con la que se creó el SVM. Cada una
	# de las dos listas debe contener sólo datos de esa clase (+1 o -1)
	def entrenar(self, datos_claseA, datos_claseB):
		# Primero adapto la lista de vectores al formato requerido:
		# una lista con los números consecutivos
		datos_A = []
		datos_B = []
		for vec in datos_claseA:
			for i in range (0, self.dimension):
				datos_A.append(vec[i])
		for vec in datos_claseB:
			for i in range (0, self.dimension):
				datos_B.append(vec[i])
		# Genero las restricciones del modelo: A y b
		A = self.generar_matriz_A(datos_A, datos_B)
		b = self.generar_vector_b(datos_A, datos_B)
		cons = {'type':'ineq',
		'fun':lambda x: b - np.dot(A,x),
		'jac':lambda x: -A}
		# Vector inicial random
		x0 = np.random.randn(self.dimension+1)
		opt = {'disp':False}
		# Resuelvo el modelo y lo guardo en resultados
		self.resultados = optimize.minimize(self.funcion_objetivo, x0, jac=self.funcion_jac,constraints=cons, method='SLSQP', options=opt)
		print self.resultados
		
	# Predice la categoría del nuevoDato, devolviendo +1.0 o -1.0
	# IMPORTANTE: nuevoDato debe ser de clase numpy.vector, y tiene
	# que ser vector del dato EN FLOATING POINT
	def predecir(self, nuevoDato):
		aux = np.append(nuevoDato, 1.0)
		return np.sign(np.dot(aux, self.resultados.x))	
	

# Zona de tests:

our_svm = SVM(dim = 2)
azules = []
azules.append(np.array([6.0, 5.5]))
azules.append(np.array([5.0, 3.0]))
azules.append(np.array([6.0, 4.0]))
azules.append(np.array([7.0, 6.0])) 
azules.append(np.array([6.5, 6.5]))
azules.append(np.array([5.5, 5.0]))
azules.append(np.array([6.5, 7.5]))
azules.append(np.array([5.5, 2.0]))
azules.append(np.array([7.0, 1.0]))
azules.append(np.array([7.0, 3.5]))
azules.append(np.array([6.0, 3.5]))
azules.append(np.array([4.0, 1.0]))    
rojos = []
rojos.append(np.array([3.0, 3.0]))
rojos.append(np.array([2.5, 2.0]))
rojos.append(np.array([1.0, 1.0]))
rojos.append(np.array([2.0, 4.0]))
rojos.append(np.array([4.0, 7.5]))
rojos.append(np.array([3.5, 6.0]))
rojos.append(np.array([3.0, 5.0]))
rojos.append(np.array([3.0, 5.5]))
rojos.append(np.array([3.5, 4.5]))
rojos.append(np.array([2.0, 6.0]))
our_svm.entrenar(azules, rojos) 

# Azul > 0, Rojo < 0	
#print predecir(np.array([1.0, 2.0]))
#print predecir(np.array([3.0, 5.0]))
#print predecir(np.array([4.0, 0.1]))
#print predecir(np.array([6.0, 0.5]))
#print predecir(np.array([3.0, 4.5]))
#print predecir(np.array([4.0, 7.5]))



