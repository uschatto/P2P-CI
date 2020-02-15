import socket
import sys
import threading

host = ''
port = 7734 # Hard coding the port that the server would be listening on
active_peers_list = []
rfc_index_list = []

#############################################################################################################################
def main():
   server_sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
   try:
      server_sock.bind((host,port))
   except socket.error,exception_msg:
      print "Caught exception while binding due to socket error code: ",exception_msg[0]," and error message: ",exception_msg[1]
      sys.exit(1)

   print "Server is successfully binded to port : ",port
   server_sock.listen(50)

   while True:
      try:
          conn_obj,address = server_sock.accept()
          print "Got connection from host : ",address[0]," and port : ",address[1]
          thread_server = threading.Thread(target =  active_peer_thread, args = (conn_obj,))
          thread_server.start()
      except KeyboardInterrupt:
          server_sock.close()
          sys.exit(0)
#############################################################################################################################
class ActivePeer:
   def __init__(self,host='None',upload_port='None'):
      self.host = host
      self.upload_port = upload_port

   def __str__(self):
      message = "Hostname of the peer is: "+str(self.host)+"\r\n"\
                "Port: " + str(self.upload_port)+"\r\n"
      return message
#############################################################################################################################
class RFCIndex:
   def __init__(self,rfc_num='None',rfc_title='None',active_peer=ActivePeer()):
      self.rfc_num = rfc_num
      self.rfc_title = rfc_title
      self.rfc_active_peer = active_peer

   def __str__(self):
      message =   "RFC "+str(self.rfc_num)+"\r\n"\
                  "Host: "+str(self.rfc_active_peer.host)+"\r\n"\
                  "Port: "+str(self.rfc_active_peer.upload_port)+"\r\n"\
                  "Title: "+str(self.rfc_title)+"\r\n"
      return message
#############################################################################################################################
def active_peer_thread(socket):
    try:
       while True:
         response_from_peer = socket.recv(1024)
         print(response_from_peer)
         if len(response_from_peer)==0:
            socket.close()
            return
         i = 0
         for i in xrange(len(response_from_peer)):
            if response_from_peer[i] == '!':
               break
         response = response_from_peer[:i]
         arr = response.split(' ');
         action = arr[0]
         if action=='ADD':
            tokens = response.split(' ')
            rfc_no = tokens[2]
            subarray = tokens[4].split('\n')
            host = subarray[0]
            subarray2 = tokens[5].split('\n')
            upload_port = subarray2[0]
            rfc_title = tokens[6:]
            rfc_title = ' '.join(rfc_title)
            if rfc_title and rfc_no:
               peer = ActivePeer(host,upload_port)
               if peer not in active_peers_list:
                  active_peers_list.append(peer)
               rfc = RFCIndex(rfc_no,rfc_title,peer)
               if rfc not in rfc_index_list:
                  rfc_index_list.append(rfc)
               msg = 'P2P-CI/1.0 200 OK\n' + str(rfc) + "\n"
            else: 
               msg = 'P2P-CI/1.0 400 Bad Request'
            msg = add_padding(msg)
            socket.send(msg)
         elif action=='LOOKUP':
            tokens = response.split(' ');
            rfc_no = tokens[2]
            rfc_title = tokens[6:]
            rfc_title = ' '.join(rfc_title)
            
            msg = 'P2P-CI/1.0 404 NOT FOUND'
            if len(rfc_index_list) > 0:
               for active_RFC in rfc_index_list:
                   if active_RFC.rfc_num == rfc_no and active_RFC.rfc_title==rfc_title :
                       msg = 'P2P-CI/1.0 200 OK\n'
                       msg += str(active_RFC)+ '\n'
            msg = add_padding(msg)
            socket.send(msg)
         elif action=='LIST':
            msg = 'P2P-CI/1.0 404 NOT FOUND'
            if len(rfc_index_list) > 0:
               msg = 'P2P-CI/1.0 200 OK \n'
               for active_RFC in rfc_index_list:
                  msg += str(active_RFC)+ '\n'
            msg = add_padding(msg)
            socket.send(msg)
	 elif action=='DEL':
	    arr = response.split(' ');
            temp = arr[3].split('\n')
            hostname = temp[0]
            temp = arr[4].split('\n')
            upload_port = temp[0]
            
            copy_active_RFCS=[]
            for rfc in rfc_index_list:
               if rfc.rfc_active_peer.host == hostname and rfc.rfc_active_peer.upload_port== upload_port:
                  continue
               else:
                  copy_active_RFCS.append(rfc)
            rfc_index_list[:]=copy_active_RFCS

            copy_active_peers=[]
            for peer in active_peers_list:
               if peer.host == hostname and peer.upload_port == upload_port:
                  continue
               else:
                  copy_active_peers.append(peer)
            active_peers_list[:]=copy_active_peers
            msg = 'P2P-CI/1.0 200 OK \n'
            msg = add_padding(msg)
            socket.send(msg) 
    except KeyboardInterrupt:
        socket.close()
        sys.exit(0)
#############################################################################################################################
def add_padding(msg):
    length = len(msg)
    while length < 1024:
        msg += '!'
        length += 1
    return msg
#############################################################################################################################
if __name__ == "__main__":
   main()
