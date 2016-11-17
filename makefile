
MENSAJE = Pre-procesamiento hecho

all:
	jupyter notebook --ip 0.0.0.0


repo: 
	git add --all
	git commit -m"$(MENSAJE)"
	git push --all
