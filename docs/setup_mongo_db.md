# Setting up Mongo DB for saving the json data coming from the Spotify API
## Install MongoDB - Ubuntu 22.04 (Jammy)
### Import the public key used by the package management system
```bash
sudo apt-get install gnupg curl
```
### import MongoDB public gpg key
```bash
curl -fsSL https://www.mongodb.org/static/pgp/server-7.0.asc | \
   sudo gpg -o /usr/share/keyrings/mongodb-server-7.0.gpg \
   --dearmor
```
### Create a list file for MongoDB
```bash
echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-7.0.gpg ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list
```
### Reload local package database
```bash
sudo apt-get update
```
### Install the MongoDB packages
```bash
sudo apt-get install -y mongodb-org
```
### Start MongoDB - systemd (systemctl)
```bash
sudo systemctl start mongod
```
### in case of error, try to start the service with the following command
```bash
sudo systemctl daemon-reload
```
### Verify that MongoDB has started successfully
```bash
sudo systemctl status mongod
```
### Enable autostart MongoDB
```bash
sudo systemctl enable mongod
```
### Stop MongoDB
```bash
sudo systemctl stop mongod
```
### Restart MongoDB
```bash
sudo systemctl restart mongod
```
### start MongoDB shell
```bash
mongosh
```


## Install PyMongo
```bash
pip install pymongo
```

