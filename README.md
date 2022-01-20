The environment variables "DISCORD_TOKEN" and "DISCORD_GUILD" must be set to run the bot.
When run locally the boat loads an existing ".env"-file from the same directory as the script.
When running a docker container an ".env"-file can be loaded with "--env-file .env".

docker run -d --env-file .env --mount src=/root/HeidiBot/voicelines,target=/sounds,type=bind registry.gitlab.com/churl/heidibot:latest
