"""Bluetooth motion tracker module.
Copyright 2017 Mark Mitterdorfer

Class to read from a Bluetooth MPU6050 device.
Obtain acceleration, angular velocity, angle and temperature
"""

import threading
import socket
import re

class MotionTracker(object):
    """Class to track movement from TCP Mobile device.
    """

    def __init__(self, bd_addr, port):
        """Initialization for tracker object.

        Args:
            bd_addr (str) : ip address
            port (int, optional) : Port, defaults to 1
        Attributes:
            bd_addr (str): ip address
            port (int): Port
            sock (bluetooth.bluez.BluetoothSocket) : Bluetooth socket object
            acc_x (float) : acceleration in X
            acc_y (float) : acceleration in Y
            acc_z (float) : acceleration in Z
            angv_x (float) : angular velocity in X
            angv_y (float) : angular velocity in Y
            angv_z (float) : angular velocity in Z
            ang_x (float) : angle degrees in X
            ang_y (float) : angle degrees in Y
            ang_z (float) : angle degrees in Z
            temperature (float) : temperature in degrees celsius
            __thread_read_device_data (threading.Thread) : Read input thread
        """
        self.bd_addr = bd_addr
        self.port = port

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print 'Socket created'

        #Bind socket to local host and port
        try:
            self.sock.bind((self.bd_addr, self.port))
        except socket.error as msg:
            print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
            sys.exit()

        print 'Socket bind complete'

        #Start listening on socket
        self.sock.listen(10)
        print 'Socket now listening'

        self.acc_x = 0.0
        self.acc_y = 0.0
        self.acc_z = 0.0

        self.angv_x = 0.0
        self.angv_y = 0.0
        self.angv_z = 0.0

        self.ang_x = 0.0
        self.ang_y = 0.0
        self.ang_z = 0.0

        self.temperature = 0.0
        self.__thread_read_device_data = None

    def start_read_data(self):
        """Start reading from device. Wait for a second or two before
        reading class attributes to allow values to 'settle' in.
        Non blocking I/O performed via a private read thread.
        """

        self.__thread_read_device_data = threading.Thread(target=self.__read_device_data)
        self.__thread_read_device_data.is_running = True
        self.__thread_read_device_data.start()

    def stop_read_data(self):
        """Stop reading from device. Join back to main thread and
        close the socket.
        """

        self.__thread_read_device_data.is_running = False
        self.__thread_read_device_data.join()
        self.sock.close()

    def __read_device_data(self):
        """Private method to read device data in 9 byte blocks.
        """
        #wait to accept a connection - blocking call
        conn, addr = self.sock.accept()
        print 'Connected with ' + addr[0] + ':' + str(addr[1])

        while self.__thread_read_device_data.is_running:
            while True:

                #Receiving from client
                data = conn.recv(1024)
                print data
                # data = heard('$$$$') + type(0/1) + acc + gyro + g + mag + omt
                ll = re.findall(r"\d+\.?\d*", data)

                self.acc_x = float('%.6f' % float(ll[2]))
                self.acc_x = float('%.6f' % float(ll[3]))
                self.acc_x = float('%.6f' % float(ll[4]))
                print("acc(g):%.6f %.6f %.6f" % (self.acc_x,self.acc_y,self.acc_z))

                self.angv_x = float('%.6f' % float(ll[5]))
                self.angv_y = float('%.6f' % float(ll[6]))
                self.angv_z = float('%.6f' % float(ll[7]))
                print("angv(g):%.6f %.6f %.6f" % (self.angv_x,self.angv_y,self.angv_z))

                self.ang_x = float('%.6f' % float(ll[8]))
                self.ang_y = float('%.6f' % float(ll[9]))
                self.ang_z = float('%.6f' % float(ll[10]))
                print("ang(g):%.6f %.6f %.6f" % (self.ang_x,self.ang_y,self.ang_z))

                reply = 'OK...' + data
                if not data: 
                    break

                #conn.sendall(reply)

            #came out of loop
            conn.close()



def main():
    """Test driver stub.
    """

    try:
        session = MotionTracker(bd_addr="127.0.0.1", port=10000)
        session.start_read_data()

        while True:
            print("ang_x:", session.ang_x, "ang_y:", session.ang_y, "ang_z:", session.ang_z)

    except KeyboardInterrupt:
        session.stop_read_data()


if __name__ == "__main__":
    main()
