#!/bin/sh

docker run -d --env-file .env --mount src=/root/HeidiBot/voicelines,target=/sounds,type=bind --name heidibot registry.gitlab.com/churl/heidibot
