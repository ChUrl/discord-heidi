#!/bin/sh

ssh christoph@servenix.local.chriphost.de "rm -rf /home/christoph/heidi-sounds/*"
scp -r ./heidi-sounds/* christoph@servenix.local.chriphost.de:/home/christoph/heidi-sounds/
