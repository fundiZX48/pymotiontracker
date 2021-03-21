#coding:UTF-8
"""Bluetooth motion tracker module.
Copyright 2017 Mark Mitterdorfer

Class to read from a Bluetooth MPU6050 device.
Obtain acceleration, angular velocity, angle and temperature
"""
import threading
import serial

#############################################
#    Accelerometer
#############################################
ACCData=[0.0]*8
GYROData=[0.0]*8
AngleData=[0.0]*8          
FrameState = 0            #通过0x后面的值判断属于哪一种情况
Bytenum = 0               #读取到这一段的第几位
CheckSum = 0              #求和校验位         
 
a = [0.0]*3
w = [0.0]*3
Angle = [0.0]*3
sp = 0.0

def DueData(inputdata):   #新增的核心程序，对读取的数据进行划分，各自读到对应的数组里
    global  FrameState    #在局部修改全局变量，要进行global的定义
    global  Bytenum
    global  CheckSum
    global  a
    global  w
    global  Angle
    global  sp
    global  l
    for data in inputdata:  #在输入的数据进行遍历
        data = ord(data)
        if FrameState==0:   #当未确定状态的时候，进入以下判断
            if data==0x55 and Bytenum==0: #0x55位于第一位时候，开始读取数据，增大bytenum
                CheckSum=data
                Bytenum=1
                continue
            elif data==0x51 and Bytenum==1:#在byte不为0 且 识别到 0x51 的时候，改变frame
                CheckSum+=data
                FrameState=1
                Bytenum=2
            elif data==0x52 and Bytenum==1: #同理
                CheckSum+=data
                FrameState=2
                Bytenum=2
            elif data==0x53 and Bytenum==1:
                CheckSum+=data
                FrameState=3
                Bytenum=2
        elif FrameState==1: # acc    #已确定数据代表加速度
            
            if Bytenum<10:            # 读取8个数据
                ACCData[Bytenum-2]=data # 从0开始
                CheckSum+=data
                Bytenum+=1
            else:
                if data == (CheckSum&0xff):  #假如校验位正确
                    a = get_acc(ACCData)
                CheckSum=0                  #各数据归零，进行新的循环判断
                Bytenum=0
                FrameState=0
        elif FrameState==2: # gyro
            
            if Bytenum<10:
                GYROData[Bytenum-2]=data
                CheckSum+=data
                Bytenum+=1
            else:
                if data == (CheckSum&0xff):
                    w = get_gyro(GYROData)
                CheckSum=0
                Bytenum=0
                FrameState=0
        elif FrameState==3: # angle
            
            if Bytenum<10:
                AngleData[Bytenum-2]=data
                CheckSum+=data
                Bytenum+=1
            else:
                if data == (CheckSum&0xff):
                    Angle = get_angle(AngleData)

                    # d = a + w + Angle
                    # print("a(g):%10.6f %10.6f %10.6f w(deg/s):%10.6f %10.6f %10.6f Angle(deg):%10.6f %10.6f %10.6f" % d)

                    #d = list(a)+list(w)+list(Angle)
                    #print("a(g):%10.6f %10.6f %10.6f w(deg/s):%10.6f %10.6f %10.6f Angle(deg):%10.6f %10.6f %10.6f" \
                    #            % (a[0],a[1],a[2],w[0],w[1],w[2],Angle[0],Angle[1],Angle[2]))
                     
                    #sp = math.sqrt(math.pow(a[0],2) + math.pow(a[1],2) + math.pow(a[2],2))
                    #print("sp:%10.6f" % sp)

                CheckSum=0
                Bytenum=0
                FrameState=0
 
 
def get_acc(datahex):  
    axl = datahex[0]                                        
    axh = datahex[1]
    ayl = datahex[2]                                        
    ayh = datahex[3]
    azl = datahex[4]                                        
    azh = datahex[5]
    
    k_acc = 16.0
 
    acc_x = (axh << 8 | axl) / 32768.0 * k_acc
    acc_y = (ayh << 8 | ayl) / 32768.0 * k_acc
    acc_z = (azh << 8 | azl) / 32768.0 * k_acc
    if acc_x >= k_acc:
        acc_x -= 2 * k_acc
    if acc_y >= k_acc:
        acc_y -= 2 * k_acc
    if acc_z >= k_acc:
        acc_z-= 2 * k_acc
    
    return acc_x,acc_y,acc_z
 
 
def get_gyro(datahex):                                      
    wxl = datahex[0]                                        
    wxh = datahex[1]
    wyl = datahex[2]                                        
    wyh = datahex[3]
    wzl = datahex[4]                                        
    wzh = datahex[5]
    k_gyro = 2000.0
 
    gyro_x = (wxh << 8 | wxl) / 32768.0 * k_gyro
    gyro_y = (wyh << 8 | wyl) / 32768.0 * k_gyro
    gyro_z = (wzh << 8 | wzl) / 32768.0 * k_gyro
    if gyro_x >= k_gyro:
        gyro_x -= 2 * k_gyro
    if gyro_y >= k_gyro:
        gyro_y -= 2 * k_gyro
    if gyro_z >=k_gyro:
        gyro_z-= 2 * k_gyro
    return gyro_x,gyro_y,gyro_z
 
 
def get_angle(datahex):                                 
    rxl = datahex[0]                                        
    rxh = datahex[1]
    ryl = datahex[2]                                        
    ryh = datahex[3]
    rzl = datahex[4]                                        
    rzh = datahex[5]
    k_angle = 180.0
 
    angle_x = (rxh << 8 | rxl) / 32768.0 * k_angle
    angle_y = (ryh << 8 | ryl) / 32768.0 * k_angle
    angle_z = (rzh << 8 | rzl) / 32768.0 * k_angle
    if angle_x >= k_angle:
        angle_x -= 2 * k_angle
    if angle_y >= k_angle:
        angle_y -= 2 * k_angle
    if angle_z >=k_angle:
        angle_z-= 2 * k_angle
 
    return angle_x,angle_y,angle_z


class MotionTracker(object):
    """Class to track movement from MPU6050 Seila device.
    """

    def __init__(self):
        """Initialization for tracker object.

        Args:

        Attributes:
            sock (serial) : serial object
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

        self.sock = serial.Serial('/dev/ttyUSB0', '115200', timeout=0.5)
        print(self.sock.is_open)

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

        while self.__thread_read_device_data.is_running:

            datahex = self.sock.read(33)
            DueData(datahex)

            # Acceleration

            self.acc_x = a[0]
            self.acc_y = a[1]
            self.acc_z = a[2]
            print("acc(g):%.6f %.6f %.6f" % (self.acc_x,self.acc_y,self.acc_z))

            # Angular velocity

            self.angv_x = w[0]
            self.angv_y = w[1]
            self.angv_z = w[2]
            print("angv(g):%.6f %.6f %.6f" % (self.angv_x,self.angv_y,self.angv_z))

            # Angle

            self.ang_x = Angle[0]
            self.ang_y = Angle[1]
            self.ang_z = Angle[2]
            print("ang(g):%.6f %.6f %.6f" % (self.ang_x,self.ang_y,self.ang_z))


def main():
    """Test driver stub.
    """

    try:
        session = MotionTracker()
        session.start_read_data()

        while True:
            print("ang_x:", session.ang_x, "ang_y:", session.ang_y, "ang_z:", session.ang_z)

    except KeyboardInterrupt:
        session.stop_read_data()


if __name__ == "__main__":
    main()
