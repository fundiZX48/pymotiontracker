# pymotiontracker
Want to track head or hand movement in your Python application or game?

**pymotiontracker** is a simple Python 3 library to continuously read values from an MPU6050 Bluetooth device on a 
non-blocking I/O thread.
These values include:
- Acceleration in X,Y,Z
- Angular velocity in X,Y,Z
- Angle in X,Y,Z
- Temperature (yup, these things do record temperature!)

Numerous solutions available on the web provide motion tracking solutions using an MPU6050 module connected to Bluetooth 
module via an Arduino or Raspberry Pi.
I thought this was a bit overkill having a "computer" as the go between the MPU6050 and Bluetooth modules.

There are numerous MPU6050 with integrated Bluetooth modules available to buy and most of them are rather inexpensive.
(Far cheaper than buying an Arduino + Bluetooth module + MPU6050 module.)
However the documentation of these integrated modules are hard to find and rather poor.

The following will attempt to address these shortcoming in a series of tutorials and will cover:
1. Getting your MPU6050 Bluetooth module
2. Powering it up
3. Installing Python libraries
4. Displaying tracked values to console

Watch this space!









