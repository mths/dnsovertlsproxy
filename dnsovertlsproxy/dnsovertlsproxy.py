# @author matheus bessa
import argparse
import logging
import socket
import sys
import ssl
from threading import Thread


class DNSOverTlsProxy:
    udp_buffer_size = 1024
    tcp_buffer_size = 4096
    socket_timeout = 5
    tcp_max_con = 10
    cert_verify = ssl.CERT_REQUIRED

    def __init__(self, debug_mode=False, cert_verify=True, cert_ca_path='/etc/ssl/certs/ca-certificates.crt',
                 listen_ip='0.0.0.0', listen_port=53, dns_tls_server='1.1.1.1', dns_tls_server_port=853):

        # Enable logging if in debug mode
        if debug_mode:
            logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

        if cert_verify is False:
            self.cert_verify = ssl.CERT_NONE

        self.cert_ca_path = cert_ca_path
        self.dns_tls_server = dns_tls_server
        self.dns_tls_server_port = dns_tls_server_port
        self.listen_ip = listen_ip
        self.listen_port = listen_port

    # Request to the DNS TLS server
    def tls_request(self, data):
        try:
            ssl_ctx = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
            ssl_ctx.verify_mode = self.cert_verify
            ssl_ctx.load_verify_locations(self.cert_ca_path)
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0) as tls_sckt:
                tls_sckt.settimeout(self.socket_timeout)
                with ssl_ctx.wrap_socket(tls_sckt, server_hostname=self.dns_tls_server) as wtls_sckt:
                    wtls_sckt.connect((self.dns_tls_server, self.dns_tls_server_port))
                    wtls_sckt.send(data)
                    rtn_data = wtls_sckt.recv(self.tcp_buffer_size)

                    return rtn_data
        except socket.timeout as e:
            print('Timeout when connecting to the DNS TLS server')
            logging.exception(e)
        except FileNotFoundError:
            print('Certificate file not found on path {0}'.format(self.cert_ca_path))

    # Handles udp request
    def handle_client_udp(self, sckt, udp_data, client):
        try:
            dgram_len = b'\x00' + chr(len(udp_data)).encode()
            tcp_data = dgram_len + udp_data
            response_data = self.tls_request(tcp_data)
            logging.info('Handling UDP request from:' + str(client))
            sckt.sendto(response_data[2:], client)
        except Exception as e:
            print('Failed to handle UDP request')
            logging.exception(e)

    # Handles tcp request
    def handle_client_tcp(self, sckt, con, client):
        try:
            tcp_data = con.recv(self.tcp_buffer_size)
            response_data = self.tls_request(tcp_data)
            logging.info('Handling TCP request from:' + str(client))
            con.sendall(response_data)
            con.close()
        except Exception as e:
            print('Failed to handle TCP request')
            logging.exception(e)

    def tcp_server(self):
        # TCP Port listening
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_sckt:
                tcp_sckt.bind((self.listen_ip, self.listen_port))
                tcp_sckt.listen(self.tcp_max_con)
                port = self.listen_port
                print('DNS Proxy to TLS - Listening TCP connections - Port: {0}'.format(port))

                while True:
                    con, client = tcp_sckt.accept()
                    Thread(target=self.handle_client_tcp, kwargs={'sckt': tcp_sckt, 'con': con, 'client': client}).start()
        except PermissionError as e:
            print('Failed to initialize TCP Server. Not enough permissions to initialize the socket. Check port number.')
            logging.exception(e)
        except Exception as e:
            print('Failed to initialize TCP Server.')
            logging.exception(e)

    def udp_server(self):
        # UDP Port listening
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_sckt:
                udp_sckt.bind((self.listen_ip, self.listen_port))
                port = self.listen_port
                print('DNS Proxy to TLS - Listening UDP connections - Port: {0}'.format(port))

                while True:
                    udp_data, client = udp_sckt.recvfrom(self.udp_buffer_size)
                    Thread(target=self.handle_client_udp, kwargs={'sckt': udp_sckt, 'udp_data': udp_data, 'client': client}).start()
        except PermissionError as e:
            print('Failed to initialize UDP Server. Not enough permissions to initialize the socket. Check port number.')
            logging.exception(e)
        except Exception as e:
            print('Failed to initialize UDP Server.')
            logging.exception(e)

    def start(self):
        try:
            # Start UDP server thread
            Thread(target=self.udp_server).start()
            # Start TCP server thread
            Thread(target=self.tcp_server).start()

        except Exception as e:
            print("Error during proxy server execution. Check logs.")
            logging.exception(e)
            sys.exit(2)


def run():
    parser = argparse.ArgumentParser(description='DNS to TLS proxy server')
    parser.add_argument('--listen_port', default=53, type=int, help='Port that the DNS proxy server will listen to')
    parser.add_argument('--listen_ip', default='0.0.0.0', help='IP that the DNS proxy server will listen to')
    parser.add_argument('--cert_verify', type=bool, default=True, help='Set to false to ignore certificate verification')
    parser.add_argument('--cert_ca_path', default='/etc/ssl/certs/ca-certificates.crt', help='Path to the CA root or CA Bundle certificates for verification')
    parser.add_argument('--dns_tls_server', default='1.1.1.1', help='DNS TLS server to proxy to')
    parser.add_argument('--dns_tls_server_port', default=853, type=int, help='DNS TLS server port to proxy to')
    parser.add_argument('--debug_mode', type=bool, default=False, help='Set to true to enable debug mode')
    args = parser.parse_args()
    proxy_srv = DNSOverTlsProxy(**vars(args))
    proxy_srv.start()


if __name__ == '__main__':
    run()
