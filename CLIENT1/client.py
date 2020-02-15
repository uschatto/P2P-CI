#!/usr/bin/python
#This is the client side code

from socket import *
import os
import random
import threading
import time
import datetime
import sys
import platform

hostname=gethostname()

def select_option():
    print('************Select option*******************')
    print('1. Add RFC\n')
    print('2. List RFCs\n')
    print('3. Lookup RFC\n')
    print('4. Download RFC\n')
    print('5. Exit\n')
    return raw_input('Enter your choice number:')

def upload_connection():
        global upload_client_port_number
        upload_client_port_number=int(raw_input("Enter the upload port for this peer: "))
        upload_socket = socket(AF_INET,SOCK_STREAM)
        host = '0.0.0.0'
        try:
                upload_socket.bind((host,upload_client_port_number))
                print ("Binding of the socket to the local port established")
        except error:
                print ("Binding of socket to current client port failed")
                sys.exit()
        upload_socket.listen(5)
        while True:
                        dwnldsocket,dwnldaddress = upload_socket.accept()
                        print '\nConnection initialized on local port : ',dwnldaddress[1]
                        message=dwnldsocket.recv(1024)
                        request=message.split(' ')
                        get_info1 = request[3].split('\n')
                        host = get_info1[1]
                        get_info2 = request[4].split('\n')
                        OS = get_info2[1]
                        rfc_number_requested=request[2]
                        #Get the current working directory
                        current_dir=os.getcwd() + "/RFC"
                        rfc_list=os.listdir(current_dir)
                        rfc_found=False
                        #Check for valid request
                        if request[0]=="GET" and request[1]=="RFC" and host=="Host:" and OS=="OS:":
                                #Check for version
                                if 'P2P-CI/1.0' in get_info1[0]:
                                        #Check for the rfc in the available list
                                        for rfc in rfc_list:
                                                if rfc_number_requested in rfc:
                                                        rfc_found=True
                                                        file_path = current_dir + "/" + rfc
                                                        opened_rfc = open(file_path,'r')
                                                        data = opened_rfc.read()
                                                        opened_rfc.close()
                                                        last_modified = time.strftime("%a, %d %b %Y %H:%M:%S ",time.gmtime(os.path.getmtime(file_path))) + 'GMT\n'
                                                        OS = platform.platform()
                                                        curr_time = time.strftime("%a, %d %b %Y %H:%M:%S",time.gmtime()) + 'GMT\n'
                                                        reply_message = "P2P-CI/1.0 200 OK\r\n"\
                                                                        "Date: " + str(curr_time) + "\r\n"\
                                                                        "OS: " + str(OS) + "\r\n"\
                                                                        "Last-Modified: " + str(last_modified) + "\r\n"\
                                                                        "Content-Length: " + str(len(data)) + "\r\n"\
                                                                        "Content-Type: text/text\r\n"
                                                        reply_message=reply_message+data
                                                        break
                                        if rfc_found==False:
                                                reply_message="404 not Found\r\n"
                                else:
                                        reply_message="505 P2P-CI Version Not Supported\r\n"
                        else:
                                reply_message="400 Bad Request\r\n"
                        dwnldsocket.sendall(reply_message)
                        dwnldsocket.close()
                        sys.exit(0)
        upload_socket.close()
        sys.exit(0)


def connect_to_server():
        servername = raw_input('Enter the server IP: ')
        serverport=7734
        client_socket = socket(AF_INET, SOCK_STREAM)
        client_socket.connect((servername,serverport))
        print ('Connected to server at address: '+str(servername)+" and port: "+str(serverport))
        rfcs_number_list,rfcs_title_list=initial_rfc_info()
        for rfc in range(len(rfcs_number_list)):
                add_RFC(client_socket,rfcs_number_list[rfc],rfcs_title_list[rfc])
        while True:
                choice = select_option()
                if choice == '1':
                        rfc_number = raw_input('Enter the RFC number: ')
                        rfc_title = raw_input('Enter the RFC title : ')
                        add_RFC(client_socket,rfc_number,rfc_title)
                elif choice == '2':
                        list_RFC(client_socket)
                elif choice == '3':
                        lookup_RFC(client_socket)
                elif choice == '4':
                        peer_hostname = raw_input('Enter hostname of peer server: ')
                        peer_upload_port = raw_input('Enter upload port of peer: ')
                        peer_socket = socket(AF_INET, SOCK_STREAM)
                        peer_socket.connect((peer_hostname,int(peer_upload_port)))
                        peer_download(peer_socket,peer_hostname)
                else:
                       delete_peer(client_socket)
                       client_socket.close()
                       sys.exit(0)

def delete_peer(client_socket):
        delete_msg="DEL PEER P2P-CI/1.0\r\n"\
		   "HOST: " + str(hostname)+"\r\n"\
                   "Port: "+str(upload_client_port_number)+"\r\n"
        reply = socket_send_receive(delete_msg,client_socket)
        print (reply)
        print("Closing the connection")

def socket_send_receive(message,client_socket):
        client_socket.send(message)
        reply_message=client_socket.recv(1024)
        return reply_message

def add_RFC(client_socket,rfc_number,rfc_title):
        add_message = "ADD RFC " + str(rfc_number)+" P2P-CI/1.0\r\n"\
                      "Host: "+str(hostname)+"\r\n"\
                      "Port: "+str(upload_client_port_number)+"\r\n"\
                      "Title: "+str(rfc_title)+"\r\n"
        reply=socket_send_receive(add_message,client_socket)
        print (reply)

def list_RFC(client_socket):
        list_message = "LIST ALL P2P-CI/1.0\r\n"\
                        "Host: "+str(hostname)+"\r\n"\
                        "Port: "+str(upload_client_port_number)+"\r\n"
        reply=socket_send_receive(list_message,client_socket)
        print (reply)

def lookup_RFC(client_socket):
        rfc_number = raw_input('Enter the RFC number: ')
        rfc_title = raw_input('Enter the RFC title : ')
        lookup_message = "LOOKUP RFC "+str(rfc_number)+" P2P-CI/1.0\r\n"\
                  "Host: "+str(hostname)+"\r\n"\
                  "Port: "+str(upload_client_port_number)+"\r\n"\
                  "Title: "+str(rfc_title)+"\r\n"
        reply=socket_send_receive(lookup_message,client_socket)
        print (reply)

def peer_download(peer_socket,peer_hostname):
        rfc_requested_number = raw_input('Enter RFC Number to be downloaded')
        rfc_requested_title = raw_input('Enter RFC Title to be downloaded')
        download_message = "GET RFC "+str(rfc_requested_number)+" P2P-CI/1.0\r\n"\
                           "Host: "+str(hostname)+"\r\n"\
                           "OS: "+platform.platform()+"\r\n"
        peer_socket.send(download_message)
        reply=""
        reply=peer_socket.recv(1024)
        if 'P2P-CI/1.0 200 OK' in reply.split("\r\n")[0]:
                filename=rfc_requested_number+"-"+rfc_requested_title+".txt"
                file_path = os.getcwd() + "/RFC/" + filename
                content_line = reply.split("\r\n")[4]
                content_len = int(content_line[content_line.find('Content-Length: ')+16:])
                reply = reply + peer_socket.recv(content_len)
                data=reply[reply.find('text/text\r\n')+11:]
                with open(file_path,'w') as file:
                     file.write(data)
                file.close()
                print ("File received and saved successfully")
                peer_socket.close()
        elif "404 not Found" in reply.split("\r\n")[0]:
                print ("404 not Found")
        elif "505 P2P-CI Version Not Supported" in reply.split("\r\n")[0]:
                print ("Version not supported")
        else:
                print ("Bad Request")

def initial_rfc_info():
        current_dir=os.getcwd()+"/RFC"
        rfc_list=os.listdir(current_dir)
        rfcs_number_list=list()
        rfcs_title_list=list()
        for rfc in rfc_list:
                rfcs_number_list.append(rfc.split('.')[0].split('-')[0])
                rfcs_title_list.append(rfc.split('.')[0].split('-')[1])
        return rfcs_number_list,rfcs_title_list

def main():
        try:
                upload_client_thread = threading.Thread(name = 'Upload Connection',target = upload_connection)
                upload_client_thread.setDaemon(True)
                upload_client_thread.start()
                server_connect_thread = threading.Thread(name = 'Server Connection',target = connect_to_server)
                server_connect_thread.setDaemon(True)
                server_connect_thread.start()
                server_connect_thread.join()
                time.sleep(5)
                sys.exit(0)
        except KeyboardInterrupt:
                sys.exit(1)

if __name__ == '__main__':
        main()
        print "Closing the main thread"
        sys.exit(0)
