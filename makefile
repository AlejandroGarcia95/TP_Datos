
MENSAJE = SVM rdy to go

all:
	jupyter notebook --ip 0.0.0.0


repo: 
	git add --all
	git commit -m"$(MENSAJE)"
	git push --all
