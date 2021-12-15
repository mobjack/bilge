
# Lets encrypt!

docker volume create portainer_data

docker run -d -p 8000:8000 -p 9443:9443 --name portainer \
    --restart=always \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -v docker_data/portainer:/data \
    cr.portainer.io/portainer/portainer-ce:2.9.3
