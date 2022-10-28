#!/bin/sh

cd /home/christoph/HeidiBot
git pull

docker pull registry.gitlab.com/churl/heidibot
docker container rm -f heidibot
docker run -d --env-file /home/christoph/HeidiBot/.env --mount src=/home/christoph/HeidiBot/voicelines,target=/sounds,type=bind --name heidibot registry.gitlab.com/churl/heidibot
docker image prune -f
