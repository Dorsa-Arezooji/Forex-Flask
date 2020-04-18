# Forex-Flask
This is a cloud-based RESTful API that has some useful functionalities for forex trading including:

* Forex
  * Get live forex data for any forex currency pair
  * Get historical forex data for any day, dating back to 5 years ago
* Crypto
  * Get live USD-based crytocurrency data
  * Get predictions for crytocurrencies
* Journal
  * Keep track of your trades by entering them here
  * Calculate profits from each trade
  * Delete or update journal entries

**Features**
- dinamically generated REST API
- HTTP services: GET, POST, PUT, DELETE
- use of an external API
- cassandra database
- load balancing implementation
- hash-based authentication
- implementation of user accounts

## Documentation

### 1. Deployment
This app is deployed using AWS. Since there isn't a lot of computationally heavy tasks involved, a t2.medium instance would do just fine.

**Docker**

Here, Docker is used to build an image ot the app and containerize it. 
1. In the terminal, navigate to the folder where you have the app files and build the app image:
```
$ sudo docker build . --tag=forex_app_image:v1
```
2. If everything goes well, now you can deploy the app:
```
$ sudo docker run -p 80:80 forex_app_image:v1
```

**Cassandra**

In this app, Cassandra is used to handle the database. Inside the AWS instance, run a Cassandra container. According to the docs, cassandra uses port 9042 for native protocol clients.
1. In the terminal, navigate to the folder where you have the app files and run a cassandra container:
```
$ sudo docker run --name cassandra-container -p 9042:9042 -d cassandra 
```
2. To be able to run commands inside the cassandra container:
```
$ sudo docker exec -it cassandra-container cqlsh 
```
3. Now using cqlsh create a designated keyspace and then the database:
```
cqlsh> CREATE KEYSPACE journal WITH REPLICATION = {'class' : 'SimpleStrategy', 'replication_factor' : 1}; 
```
```
cqlsh> CREATE TABLE journal.users (name text, email text, password text, apikey text, PRIMARY KEY (email, apikey)); 
 ```
```
cqlsh> CREATE TABLE journal.entry_records (apikey text, api__id text, id text, pair text, type text, volume text, start_time text, close_time text, start_price text, close_price text, profit text, PRIMARY KEY (apikey, api__id, id)); 
```

**Kubernetes**

1. Install Kubernetes by issuing:
```
$ sudo snap install microk8s --classic
```
If the installation was successful, you'll get:
```
microk8s v1.18.1 from Canonical✓ installed
```
2. Create the pod:
```
$ sudo microk8s.kubectl run forex-deployment --image=forex_app_image:v1 --port=80
```
If all goes well, you'll see:
```
pod/forex-deployment created
```
3. To see the pods created:
```
$ sudo microk8s.kubectl get pods
NAME               READY   STATUS             RESTARTS   AGE
forex-deployment   0/1     ImagePullBackOff   0          92s
```

### 2. How to use



* delete entry:
``` 
curl -i -H "Content-Type: application/json" -X DELETE -d '{"apikey":"****","id":"****"}' http://ec2-100-26-191-173.compute-1.amazonaws.com/del_entry/
```

* update entry:
``` 
curl -i -H "Content-Type: application/json" -X PUT -d '{"apikey":"****","id":"****","pair":"****","type":"****","volume":"****","open_time":"****","close_time":"****","open_price":"****","close_price":"****"}' http://ec2-100-26-191-173.compute-1.amazonaws.com/update_entry/
```
