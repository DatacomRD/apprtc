""" TWR related handler

This module contains the handler/helper of TWR
"""

import socket
import logging
import select
import errno
import constants


PTN_ISERVER_COMMAND = '{}:{}:{}\r' # userid:command:params

# the iServer Handler
class iServer:
  def __init__(self, ip = None, port = None):
    if ip:
      self.ip = ip
    else:
      self.ip = constants.ISERVER_IP

    if port:
      self.port = port
    else:
      self.port = constants.ISERVER_PORT
      
    self.init_socket()

  def init_socket(self):
    try:
      s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

      logging.info('connecting with iserver, ip: {}. port: {}'.format(self.ip, self.port))

      s.connect((self.ip, self.port))

      self.socket = s
    except Exception as ex:
      logging.error('Failed to init the iserver socket, exception: {}'.format(ex))

  def send_data(self, data):
    """ Send Data to remote server
    Args:
      data: Data to send

    Return:
      The sending result, True if success, False if faield.
    """
    try:
      if not hasattr(self, 'socket'):
        # no socket initialized, try to init once again
        self.init_socket()

      if hasattr(self, 'socket'):
        self.socket.send(data)
        return True
      else:
        logging.info('No socket initialized to send data')
        return False
    except socket.error as e:
      if e.errno == errno.ECONNRESET or e.errno == errno.EPIPE:
        try:
          # if connect disconnect, we will retry once.
          logging.error('Socket of iServer has been disconnected, re-connect and try to send again.')
          self.init_socket()
          self.socket.send(data)

          return True
        except Exception as ex:
          logging.error('Cannot send command to iServer, exception: {}'.format(ex))
          return False
      else:
        logging.error('Cannot send command to iServer, unknown exception')
        return False
    except:
      logging.info('Unknown exception occurrect while sending data')
      return False

  def recv_data(self):
    res = None

    try:
      if not hasattr(self, 'socket'):
        self.init_socket()

      if hasattr(self, 'socket'):
        self.socket.setblocking(0)
        ready = select.select([self.socket], [], [], 1) #  we just wait one second for server response
        if ready and ready[0]:
          res = self.socket.recv(1024)
          logging.debug('received data from iserver: ' + res)
        self.socket.setblocking(1)
      else:
        logging.info('No socket initialized to receive data')
    except socket.error as e:
      if e.errno == errno.ECONNRESET or e.errno == errno.EPIPE:
        try:
          # if connect disconnect, we will retry once.
          logging.error('Socket of iServer has been disconnected, re-connect and try to receive again.')
          self.init_socket()
          self.socket.setblocking(0)
          ready = select.select([self.socket], [], [], 1) #  we just wait one second for server response
          if ready and ready[0]:
            res = self.socket.recv(1024)
            logging.debug('received data from iserver: ' + res)

          self.socket.setblocking(1)
        except Exception as ex:
          logging.error('Cannot send command to iServer, exception: {}'.format(ex))
      else:
        logging.error('Cannot send command to iServer, unknown exception')
    except:
      logging.info('Unknown exception occurrect while receiving data')
      return False

    return res

  def user_enter_concall(self, userId, roomId):
    cmd = PTN_ISERVER_COMMAND.format(userId, 'AppRTCEnter', roomId)

    logging.debug('Sending command to iserver, command: ' + cmd)
    self.send_data(cmd)

    data = self.recv_data()

  def user_leave_concall(self, userId, roomId):
    cmd = PTN_ISERVER_COMMAND.format(userId, 'AppRTCLeave', roomId)

    logging.debug('Sending command to iserver, command: ' + cmd)
    self.send_data(cmd)

    data = self.recv_data()
    

  def close(self):
    self.socket.close()

