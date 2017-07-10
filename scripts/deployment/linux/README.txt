-Deployment with Linux-

Before deploying, you should retrieve the IP address of the server. You will need it when running the scripts. You could use the command:
ifconfig

--Pre installation requirements--
First, you need to install GIT:
sudo apt-get install git

Then, you can clone your project:
git clone <url of the GIT repository>

--Install packages--
First, go to the main folder of your project.
Then, you can run the first script install-linux-dev.sh:
./scripts/deployment/linux/install-linux-dev.sh

It will ask you if you want to install the packages. Say yes.

--Configuration of the database--
First, go to the main folder of your project.
You can run the second script bdd-configuration.sh:
./scripts/deployment/linux/bdd-configuration.sh <IP Address>

You need to provide the ip address to the script for the configuration.
At some point, it will ask you to provide a username, email and password for the superuser of the application.

--Update the code--
First, go to the main folder of your project.
You can use the script update.sh to update the code with this command:
./scripts/deployment/linux/update.sh <IP Address>

You need to provide the ip address for the update.
This script will shutdown the server, update the code and restart the server.






