all:
	-docker rm lb
	# @echo $(CURDIR)
	docker run --privileged --name lb -p 6060:6060 -v /var/run/docker.sock:/var/run/docker.sock \
	--network=my-net -v "$(CURDIR):/app/"  lb:1.1


build:
	docker build -t lb:1.1 .

create-network:
	docker network create my-net
