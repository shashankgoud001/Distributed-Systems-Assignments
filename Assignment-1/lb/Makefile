all:
	-docker rm lb

	docker run --privileged --name lb -p 5000:5000 -v /var/run/docker.sock:/var/run/docker.sock \
	--network=my-net -v "$(CURDIR):/app/"  lb:1.1 uvicorn loadbalancer:app --host 0.0.0.0 --port 5000 


build:
	docker build -t lb:1.1 .
	docker build -t serverimg ../server 

create-network:
	docker network create my-net

clean:
	docker rm -f   $$(docker ps -aq)
