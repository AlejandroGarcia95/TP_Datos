#coding=utf-8

from ppmc import *

texto = 'I was unable to cope with what you said\nSometimes we need to be cruel to be kind\nChild that I was, could not see the reason\nFeelings I had were but sham and a lie?\n\nI have never forgotten your smile\nYour eyes, oh, Shamandalie\n\nTime went by, many memories died\nI\'m writing this down to ease my pain\n\nYou saw us always clearer than me\nHow we were never meant to be\nLove denied meant the friendship would die\nNow I have seen the light\nThese memories make me cry\0'
#texto = 'Holaaaaaadasdasdasdad\0'


file = open("sonata.txt")
texto = ''
for line in file:
	texto += line
texto += '\0'

texto = 'I was unable to cope with what you said\nSometimes we need to be cruel to be kind\nChild that I was, could not see the reason\nFeelings I had were but sham and a lie?\n\nI have never forgotten your smile\nYour eyes, oh, Shamandalie\n\nTime went by, many memories died\nI\'m writing this down to ease my pain\n\nYou saw us always clearer than me\nHow we were never meant to be\nLove denied meant the friendship would die\nNow I have seen the light\nThese memories make me cry\0'

#print texto
print "-----"

for i in range(0, 25):
	cmpr = CompresorEstatico(i)
	cmpr.entrenar(texto)
	binario = cmpr.comprimir(texto)
	#print binario
	#print "\n"
	texto2 = cmpr.descomprimir(binario)
	#print texto2
	print i
	if (texto2 == texto):
		print "SUCCESS!!!"
	else:
		print "ERROR: NOT MATCHING STRINGS"
	print "------"
	print "\n\n"
