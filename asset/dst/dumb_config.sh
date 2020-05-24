adduser dst
dpkg --add-architecture i386 # If running a 64bit OS
apt-get update
apt-get install lib32gcc1 # If running a 64bit OS
apt-get install lib32stdc++6 # If running a 64bit OS
apt-get install libcurl4-gnutls-dev:i386
apt-get install screen
su - dst
wget https://steamcdn-a.akamaihd.net/client/installer/steamcmd_linux.tar.gz
tar -xvzf steamcmd_linux.tar.gz
mkdir server_dst
printf "login anonymous \n force_install_dir /home/dst/server_dst \n app_update 343050 validate \n quit \n" | ./steamcmd.sh
su - dst
sudo touch /home/dst/server_dst/bin/start.sh && sudo chmod 777 /home/dst/server_dst/bin/start.sh
sudo touch /home/dst/server_dst/bin/start2.sh && sudo chmod 777 /home/dst/server_dst/bin/start2.sh
sudo touch /home/dst/server_dst/bin/restart.sh && sudo chmod 777 /home/dst/server_dst/bin/restart.sh
sudo touch /home/dst/server_dst/bin/restart2.sh && sudo chmod 777 /home/dst/server_dst/bin/restart2.sh
sudo printf "./dontstarve_dedicated_server_nullrenderer -console -cluster MyDediServer -shard Master" | /home/dst/server_dst/bin/start.sh
sudo printf "./dontstarve_dedicated_server_nullrenderer -console -cluster MyDediServer -shard Caves" | /home/dst/server_dst/bin/start2.sh
sudo printf "#!/bin/sh \n name_folder=\"/home/dst/server_dst/bin\" \n start_overworld=\"sh start.sh\" \n cd ${name_folder} \n screen -dmS dst_server1 ${start_overworld}" | /home/dst/server_dst/bin/restart.sh
sudo printf "#!/bin/sh \n name_folder=\"/home/dst/server_dst/bin\" \n start_cave=\"sh start2.sh\" \n cd ${name_folder} \n screen -dmS dst_server2 ${start_cave}" | /home/dst/server_dst/bin/restart2.sh
exit