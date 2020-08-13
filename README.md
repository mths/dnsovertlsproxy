# DNS over tls proxy

This python module (dnsovertlsproxy) is a simple implementation of a DNS to TLS proxy server that allows services to route their unencrypted DNS queries to an encrypted DNS server endpoint.

**Implementation**

Supports UDP and TCP connection.

Because of the multithreaded implementation, the proxy server allows incoming requests at the same time, even if its an UDP or TCP request.

**Security concerns**

The traffic between the client and the DNS Proxy is not encrypted, because of that is highly recommended that the proxy server runs inside a DMZ protected zone and "closest" as possible to the client service to reduce the attack surface of a man in the middle attack.

For testing purposes, the proxy has an optional parameter that allows ignoring the certificate verification. This can become a security issue if the proxy server connects to an untrusted DNS server. In a production environment, this is a bad practice.

**Integrating to a distributed, microservices-oriented and containerized architecture**

I believe that in a production container environment like Kubernetes the best approach is to use the dnsovertlsproxy container as a sidecar to the service(dns client) container. You can configure the service container to DNS resolve to the sidecar dnsovertlsproxy container so the DNS queries go through the sidecar assuring that all communication (inbound and outbound) exiting the pod to the DNS server is encrypted.

It also makes harder to an attacker to sniff/spoof the communication between the service and the dnsovertlsproxy since the exposed surface is inside the POD.

**Future improvements**

* Add support to environment variables as configuration parameters to facilitate the use on containers.
* Do a few tests with multiprocessing instead of multithreading because of the global interpreter lock when working with threads.
* Improve error messages and exception handling.

## Usage

**How to use - CLI Daemon**

The module requires Python 3+. If needed, configure a virtualenv on the project folder.

> `virtualenv venv -p python3`
> `source venv/bin/active`

Build/Install the pip module

> `python setup.py install`

Run the dnsovertlsproxy module with debug mode enabled

> `dnsovertlsproxy --debug_mode=True`

**How to use - Docker container**

Build a local docker image

> `docker build . -t dns-proxy-server:0.1.0`

Run the docker image and expose the port 53 of the container as 10053 on the host (You can expose port 53 if you want to) for TCP and UPD connections

> `docker run -tid -p 10053:50053 -p 10053:50053/udp dns-proxy-server:0.1.0`

**How to test the DNS queries to the DNS proxy server**

After the proxy server is running, run the following commands:

> `nslookup google.com 127.0.0.1 -port=10053` (UDP connection)

> `dig @127.0.0.1 -p 10053 google.com +tcp` (TCP connection)

**Additional Arguments**

You can pass the following arguments to the dnsovertlsproxy cli. Ex: dnsovertlsproxy --listen_port 123456

| argument | description | default |
| ------ | ------ | ------ |
| --listen_port | Port that the DNS proxy server will listen to | 0.0.0.0 |
| --listen_ip | Ip that the DNS proxy server will listen to | 53 |
| --cert_verify | Set to false to ignore certificate verification | True |
| --cert_ca_path |Path to the CA root or CA Bundle certificates for verification | /etc/ssl/certs/ca-certificates.crt |
| --dns_tls_server | DNS TLS server to proxy to | 1.1.1.1 |
| --dns_tls_server_port | DNS TLS server port to proxy to | 853 |
| --debug_mode | Set to true to enable debug mode | False |

## Authors

* **Matheus Bessa**
