# Introduction

How does the Google manages to respond to our query within seconds? Good question! Most users of the web are unaware of the sheer scale of the search engine responsible for bringing content across the Internet. The boom in the digital revolution has resulted in increased usage of the Internet with Google facing the heat of the increasing demand in terms of million requests per second to serve their loyal customers.

Sites like Google which bring in high-volume traffic may inadvertently be faced with frequent server upgrades, so that page speed and, in turn, usability, doesn’t suffer for their loyal customers. Often, however, simple hardware upgrades aren’t enough to handle the vast traffic that some sites draw.

So how do Google ensures that it won’t burst into figurative flames as page visits skyrocket? The concept of Load Balancing comes into picture.

> **Load balancing** refers to efficiently distributing incoming network traffic across a group of backend servers, also known as a server farm or server pool.

![Load Balancing](./images/LoadBalancerDiagram.png)

A load balancer acts as the “traffic cop” sitting in front of your servers and routing client requests across all servers capable of fulfilling those requests in a manner that maximizes speed and capacity utilization and ensures that no one server is overworked, which could degrade performance.

If a single server goes down, the load balancer redirects traffic to the remaining online servers. When a new server is added to the server group, the load balancer automatically starts to send requests to it.
Loads are broken up based on a set of predefined metrics, such as by geographical location, or by the number of concurrent site visitors.

Members of a certain group — such as ‘people living in Europe’, for example, may be directed to a server within Europe, while members of another group take, for instance, ‘North Americans’ may be directed to another server, closer to them.

In this Micro-byte, we will learn how to balance the load between Applications using HAProxy using different available strategies. So let's dive in !!!


# Pre-Requisites

Before starting, make sure you are logged in as a user with sudo privileges on your Linux machine and you don’t have Apache or any other web server running on port 80 or 443.

1. Install HAProxy using apt tool
    >$ sudo apt -y install haproxy 

    Once the installation is completed, HAProxy service will start automatically. You can check the status of the service with the following command:

    >$ sudo systemctl status haproxy

    The output will look something like this:
    ```
    ● haproxy.service - HAProxy Load Balancer
     Loaded: loaded (/lib/systemd/system/haproxy.service; enabled; vendor prese>
     Active: active (running) since Sun 2020-10-25 22:18:44 IST; 7min ago
       Docs: man:haproxy(1)
             file:/usr/share/doc/haproxy/configuration.txt.gz
   Main PID: 52978 (haproxy)
      Tasks: 7 (limit: 8734)
     Memory: 3.4M
     CGroup: /system.slice/haproxy.service
             ├─52978 /usr/sbin/haproxy -Ws -f /etc/haproxy/haproxy.cfg -p run/>
             └─52979 /usr/sbin/haproxy -Ws -f /etc/haproxy/haproxy.cfg -p /run/>
    ```
2. Install `dnsutils` package if not present to get information from DNS name servers.
    >$ sudo apt -y install dnsutils

3. Python 3.6 is recommended to be installed in the system.
4. Python package `flask` is required to be able to build application service.
    >$ pip3 install flask


# Activities

## Activity 1 - Case Study: DNS Load Balancing in google.com
---

Let's start with understanding what is DNS Load Balancing: -

> ***DNS load balancing*** is the practice of configuring a domain in the > Domain Name System (DNS) such that client requests to the domain are distributed across a group of server machines. A domain can correspond to a website, a mail system, a print server, or another service that is made accessible via the Internet.

Ok. Well that went over my head. How about understanding the above definition by exploring it in practical manner. Let's **dig** it.

- Open your favorite shell or terminal ( mine is **zsh** :P ) and type the following command:-
    > $ dig google.com +short

    The output will look something like this:

    ```
    216.58.203.174
    ```
    Don't blame me if it is not the output. Try running the command until you get the above output.

    <details> 
    <summary>You are allowed to expand when you get the above output right!</summary>
    
    Did you noticed something strange?

    Each execution of above command produced some repetitive set of IP address.
    ```
     $ dig google.com +short
        216.58.203.206

     $ dig google.com +short
        172.217.166.174

     $ dig google.com +short
        172.217.160.206

     $ dig google.com +short
        172.217.174.78

     $ dig google.com +short
        172.217.174.78

     $ dig google.com +short
        216.58.203.206

     $ dig google.com +short
        172.217.160.206

     $ dig google.com +short
        216.58.203.206
    ```
    DNS serves as the “phone book” for the Internet: it maps domain names like google.com, which are the equivalent of personal or business names in the phone book, to Internet Protocol (IP) addresses like *216.58.203.174* , which are the equivalent of phone numbers.

    Let’s understand it step-by-step:

    1. DNS can hold multiple records for the same domain name (google.com).
    2. DNS can return the list of IP addresses for the same domain name.
    3. With each DNS response, the IP address sequence in the list is permuted on the basis of term `round robin`.
    4. When a web-browser requests a web-site, it will try these IP addresses one-by-one, until it gets a response.
    5. That's how we probably get different IPs on each different DNS request.

    > **NOTE**:- The different IP address in the output are the IPs of load balancers which further load balances the actual application servers of the search engine.

    So, now you can go back to the original definition of **DNS Load Balancing** which will make much more sense now after understanding it in a practical way.

    You can paste each IP Address into the browser and will notice that each of them displays Google homepage served by different application servers across the globe. 
    
    </details>

    ### Micro-Challenge:-
    > Try the above commands on various mostly used websites like 
     facebook.com, outlook.com, yahoo.com and understand how do they DNS load balance their services.
    

    Let's hop in to next activity to actually try out by load balancing few application servers on the machine.

---
## Activity 2 - Spin up multiple application servers.
---

In real-world scenario, there are application servers where each might be running on different physical hardware located geographically apart from each other.

In this micro-Byte, we will simulate the scenario by launching flask server in seperate terminal and logically seperating them by assigning different port numbers to each of them.

 - Copy the app.py from `src/activity-2/app.py` in any location as per your preference.
 - Launch a shell and run the flask server file in following syntax:-
    >$ python3 app.py < Unused port number >
    
    For eg:- 
    ``` 
    $ python3 app.py 8080
    ```
- Launch 3-4 servers with different port numbers in each seperate terminal and make sure not to close the terminal otherwise it will kill the server process.

The output will look something like this for each individual process in respective shell with different port numbers:

```
 * Serving Flask app "app" (lazy loading)
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: off
 * Running on http://127.0.0.1:8080/ (Press CTRL+C to quit)

```

> Curious Question:- What would happen if I launch another server process with port number which is already used by previous instance of process??

---
## Activity 3 - Configure HAProxy Load Balancer
---
HA-Proxy is a free and open source, software High Performance TCP/HTTP load balancer that powers many distributed systems, web applications and web sites.

HAProxy's logic comes from a config file (haproxy.cfg)
- Predefine location:- `/etc/haproxy/haproxy.cfg`
- Command to run custom HAProxy conf: 
```
$ haproxy -f < Path of haproxy configuration >
```

Instead of using default config file we'll create a new configuration file.

### Activity 3.1
---

> Copy the file from src/activity-3/myhaproxy.cfg and fill the require data as mentioned.

- After the required data is filled, start the load balancer with the command mentioned above.
- Head to the browser and type `localhost:3000` and keep on refreshing and note down the results.

You might notice that the response is served from different application servers.

> **Note:-** Kill `Ctrl+C` the active HAproxy command and enter it again after making any changes to the custom configuration file.

## #Activity 3.2
---
- Change ` server server01 localhost:8080 ` to ` server server01 localhost:8080 weight 4 ` in the configuration file.
- Similarly append `" weight < Any number > ( For now only add 1 ) " ` to all the backend application nodes.
- Head to the browser and type `localhost:3000` and keep on refreshing and note down the results.

<details>
<summary>Expand to know if you saw something strange.</summary>
This kind of load balancing strategy is called as weighted round robin.

Where does this strategy helps? Good question.

> Well that's a micro-challenge. Google it out :)
</details>

### Activity 3.3
---
- Kill one of the server by sending a  `Ctrl + C` signal through shell.
- Head to the browser and type `localhost:3000` and keep on refreshing and note down the results.

<details>
<summary>Expand to know if you saw something strange.</summary>
The HAProxy loadbalancer didn't know the server is not available and still attempted to forward request to it leading to HTTP 503 error code.
Well. That's quite a dumb move. Don't you think so.

How to make load balancer aware about active status of the server? Nice Question.

> Well that's a next activity to fix it. Cheers:)
</details>

### Activity 3.4
----

To make HAProxy aware about the failure or re-spawn of the server, we need to add a `check` keyword.
 Replace 
 ``` 
server server01 localhost:8080 weight 4 
```
with 
```
server server01 localhost:8080 weight 4 check
```
to each of the application nodes configuration.

Now HAproxy will keep on polling to the servers to check whether it is alive or not and add or remove the server IP from the round robin list.

---
## Activity 4- Enable live monitoring and statistics 
---

***Why is it Important to Monitor Your Load Balancers?***

- Monitoring load balancer metrics provides you with insight into how your system is performing.
- The load balancer can tell you how many clients are accessing your services and how long it’s taking your service to respond to these requests.
- By monitoring these metrics, you will be able to immediately determine if there is an operational problem that affects your web services. 
- When there is a critical production issue, you need to be aware and respond immediately to contain the damage and reduce impact on customers. Since the load balancer is always checking the health of a service, it can inform you of potential issues in your service before they overwhelm your system.
- If you just released a new version of your service and the error count suddenly increases, you can perform a rollback before your customers know there’s an issue.
- Additionally, this information can help you quantify customer growth and gives you a baseline or benchmark for system performance. It enables you to monitor traffic patterns and provides you with insight into the time of day your system is used and respond to spikes in demand so you can provision capacity appropriately.  

>Comment out the lines after `#> listen- combine both backend and frontend (Optional)` to enable statistics page.
-  Head to the browser and type `localhost:83` to view stats page.
- Check around the stats page by making requests to localhost:3000 or killing and re-spawning the server. The realtime data will be reflected on the stats page.

## Mega-Challenge:-
> Try out load balancing with actual cloud instances of server from AWS, GCP whichever you prefer.
>
> It will be a challenging task to complete but now you know the basics so just dive in!!!

# Conclusion
Congratulations!! You made it. That was a quite a daunting and amazing ride!. You can checkout the following links about some good discussions about load balancers:-

[1] [What is load Balancing?](https://avinetworks.com/what-is-load-balancing/)

[2] [Introduction to architecting systems](https://lethain.com/introduction-to-architecting-systems-for-scale/)

[3] [Benefits of Load Balancing](https://medium.com/@abdurrakib0/5-benefits-of-load-balancer-in-digital-ocean-very-cheap-cd40bd7ea269)


# References

1. [What is load balancer and how it works](https://medium.com/@itIsMadhavan/what-is-load-balancer-and-how-it-works-f7796a230034)
2. [An In-Depth Guide to Load Balancer Monitoring](
    https://blog.appoptics.com/an-in-depth-guide-to-load-balancer-monitoring/
)
3. [How to Use HAProxy for Load Balancing](
    https://www.linode.com/docs/guides/how-to-use-haproxy-for-load-balancing/
)
4. [What is round-robin DNS?](
    https://www.cloudflare.com/en-in/learning/dns/glossary/round-robin-dns/
)















