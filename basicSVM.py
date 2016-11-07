#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
from scipy import optimize

# Ahora actualizado para soft-margin y kernel

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
#		min (||w||**2) + C * sum(Ei)
#	sujeto a:
#		yi (<w, xi> + k)-1 + Ei >= 0	para todo dato xi, donde yi es su 
# categoría (1 ó -1), C es la cte de soft-margin y Ei es cada uno de los
# epsilon sub i (variables de slack) asociadas a cada restricción		
# Observar que las restricciones pueden escribirse como:
# 		yi <w, xi> >= 1 - k yi - Ei
# Es decir, las restricciones son lineales. Se las plantea así genéricamente como
# Ax - E<= b	donde A es matriz de los datos signados según su categoría, y
# E es un vector que posee a los epsilon slacks.

# Además, el SVM puede recibir una función de kernel que redefine el
# prod. interno usado, permitiendo realizar mappeos a dimensiones superiores.


# Nomenclatura: Clase "A" es la positiva (+1) y clase "B" la negativa (-1)

class SVM:
	# Crea el SVM. Es necesario especificar la dimensión de los datos
	# cte_soft_margin es la cte C del método de soft margins (en float plz)
	# kernel_func es la función de kernel a usar... Es decir, es una
	# K(x,y) que cumple ser un P.I. (x,y son numpy.vector)
	def __init__(self, dim, cte_soft_margin, kernel_func):
		self.dimension = dim
		self.resultados = 0
		self.C = cte_soft_margin
		self.kernel = kernel_func
	
	# Define la función objetivo del modelo de PLC
	def funcion_objetivo(self, x, sign = 1.0):
		norma_w = 0.0
		for i in range(0, self.dimension):
			norma_w += (x[i]*x[i])
		suma_epsilon = 0.0
		for i in x[(self.dimension+1)::]:
			suma_epsilon += i
		return sign * (0.5* norma_w + self.C * suma_epsilon)
    
    # Define el gradiente a usar para el método de resolución de PLC
    # (básicamente, son las derivadas parciales de la función objetivo)
	def funcion_jac(self, x, sign = 1.0):
		p = np.copy(x.T)
		p[self.dimension] = 0.0
		vecAux = np.copy(p[(self.dimension+1)::])
		for i in range(0, np.size(vecAux)):
			vecAux[i] = self.C * np.sign(vecAux[i]);
		p[(self.dimension+1)::] = vecAux
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
	
	# Básicamente escribe la parte Ax - E del sistema
	def procesar_ineq_fun(self, A, x):
		x_real = x[0:self.dimension+1:1]
		epsilons = np.copy(x[(self.dimension+1)::])
		# Aplico el producto interno kernealizado
		cantDatos = np.size(A)/(np.size(x_real))
		resultado = np.array([])
		for i in range(0, cantDatos):
			#print A[i][0:self.dimension:1]
			resultado = np.append(resultado, self.kernel(A[i], x_real)) 
		resultado -= epsilons
		return resultado
	
	# Entrena al SVM con el set de datos recibido. Esta función
	# guarda en el atributo resultados toda la información del
	# optimize de scipy. Los primeros self.dimension valores de
	# resultados.x corresponden al vector w, el siguiente valor del 
	# mismo campo corresponde a k del hiperplano. Todos los valores
	# siguientes corresponden a los epsilon[i] (variables de slack) del
	# soft margin.
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
		cantDatos = len(datos_A) + len(datos_B)
		cantDatos /= self.dimension
		#print "CantDatos:", cantDatos
		A = self.generar_matriz_A(datos_A, datos_B)
		b = self.generar_vector_b(datos_A, datos_B)
		cons = {'type':'ineq',
		'fun':lambda x: b - self.procesar_ineq_fun(A, x),
		#'jac':lambda x: -A
		}
		# Vector inicial random
		x0 = np.random.randn(self.dimension + 1 + cantDatos)
		opt = {'disp':False}
		# Resuelvo el modelo y lo guardo en resultados
		self.resultados = optimize.minimize(self.funcion_objetivo, x0, jac=self.funcion_jac,constraints=cons, method='SLSQP', options=opt)
		#print self.resultados
		
	# Predice la categoría del nuevoDato, devolviendo un valor.
	# IMPORTANTE: nuevoDato debe ser de clase numpy.vector, y tiene
	# que ser vector del dato EN FLOATING POINT
	def predecir(self, nuevoDato):
		x_real = self.resultados.x[0:self.dimension+1:1]
		#return np.sign(self.kernel(aux, x_real))
		#return self.kernel(nuevoDato, x_real) 	
		aux = np.append(nuevoDato, 1.0)
		return (self.kernel(aux, x_real))
		
	# Devuelve una tupla (w, k) que representa el hiperplano solución.
	# w es el vector director del hiperplano (numpy.vector) y k la cte
	# asociada según la ecuación <w, x> + k = 0. Válida para usar
	# sólamente luego del training.
	def devolver_hiperplano(self):
		w = np.copy(self.resultados.x[0:self.dimension:1])
		k = self.resultados.x[self.dimension+1]
		return (w, k)
	

# Zona de tests:

def kernel_gaussiano(x, y):
	sigma = 0.15
	dist = np.linalg.norm(x - y)
	return np.exp((-0.5 * dist * dist) / (sigma * sigma) )

#our_svm = SVM(dim = 2, cte_soft_margin = 250.0, kernel_func = np.dot)
#azules = []
#azules.append(np.array([0.0, 0.5]))
#azules.append(np.array([-1.5, 0.5]))
#azules.append(np.array([0.5, 0.5]))
#azules.append(np.array([1.0, -0.5]))
#azules.append(np.array([0.0, -1.0]))
#azules.append(np.array([-1.0, -1.0]))
#azules.append(np.array([1.2, -1.4]))
#azules.append(np.array([-0.6, 0.2]))
#azules.append(np.array([-0.75, -0.4]))
#azules.append(np.array([1.2, 1.1]))
#azules.append(np.array([0.2, -0.1]))
#azules.append(np.array([-0.8, 1.0]))
#azules.append(np.array([0.1, 1.4]))
 
#rojos = []
#rojos.append(np.array([-5.0, 0.0]))
#rojos.append(np.array([-0.1, -4.9]))
#rojos.append(np.array([-0.1, 5.2]))
#rojos.append(np.array([-3.5, 3.6]))
#rojos.append(np.array([-2.0, 4.5]))
#rojos.append(np.array([-4.5, 2.1]))
#rojos.append(np.array([2.5, 4.3]))
#rojos.append(np.array([1.0, 4.75]))
#rojos.append(np.array([4.0, 3.0]))
#rojos.append(np.array([5.0, 0.6]))
#rojos.append(np.array([-1.5, -4.92]))
#rojos.append(np.array([-4.1, -3.3]))
#rojos.append(np.array([-3.0, -3.8]))
#rojos.append(np.array([-4.5, -2.2]))
#rojos.append(np.array([1.3, -4.8]))
#rojos.append(np.array([3.2, -3.7]))
#rojos.append(np.array([4.2, -2.1]))
#rojos.append(np.array([4.4, -1.5]))

#our_svm.entrenar(azules, rojos) 

# Azul > 0, Rojo < 0	
#print "Prediccion de los puntos: (Azul = 1, Rojo = 0)"
#print "(-1.3, -1.0): ", our_svm.predecir(np.array([-1.3, -1.0]))
#print "(2.5, 4.0): ", our_svm.predecir(np.array([2.5, 4.0]))
#print "(0.2, 2.2): ", our_svm.predecir(np.array([0.2, 2.2]))
#print "(-3.0, 3.0): ", our_svm.predecir(np.array([-3.0, 3.0]))
#print "(2.0, -3.5): ", our_svm.predecir(np.array([2.0, -3.5]))
#print "(-2.6, 0.0): ", our_svm.predecir(np.array([-2.6, 0.0]))
#print our_svm.devolver_hiperplano()





