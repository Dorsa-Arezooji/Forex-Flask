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
cqlsh> CREATE TABLE journal.users (name text, username text, password text, apikey text, PRIMARY KEY (username, apikey)); 
 ```
```
cqlsh> CREATE TABLE journal.entry_records (apikey text, id text, pair text, type text, volume float, start_time text, close_time text, start_price float, close_price float, profit float, PRIMARY KEY (apikey, id)); 
```

### 2. How to use
