#coding=utf-8

from ppmc import *

texto = 'I was unable to cope with what you said\nSometimes we need to be cruel to be kind\nChild that I was, could not see the reason\nFeelings I had were but sham and a lie?\n\nI have never forgotten your smile\nYour eyes, oh, Shamandalie\n\nTime went by, many memories died\nI\'m writing this down to ease my pain\n\nYou saw us always clearer than me\nHow we were never meant to be\nLove denied meant the friendship would die\nNow I have seen the light\nThese memories make me cry\0'

file = open("sonata.txt")
texto = ''
for line in file:
	texto += line
texto += '\0'
print "-----"

# Modo de uso del compresor hibrido:
# entrenar(texto)			---- entrena al compresor
# clean()					---- elimina todo entrenamiento previo
# descomprimir(binario, n) 	---- decodifica hasta n caracteres del binario comprimido
# testearCompresion(texto)	---- pasa texto por el compresor y el descompresor, y compara el resultado con el texto original
# 
#	EL MAS UTIL:
#
#		ratioCompresion(texto)	---- comprime el texto y divide las longitudes del binario y del texto original para obtener el ratio de compresión

# Ejemplo: entreno con un archivo y luego compruebo que funcione bien y obtengo el ratio para cada linea del mismo
cmpr = CompresorHibrido(5)
cmpr.entrenar(texto)

print (cmpr.testearCompresion('w'))

#for line in texto.split('\n'):
#	test = cmpr.testearCompresion(line)
#	if (not test):
#		print "|" + line + "|"
#		raise StopIteration
	
file.close()
