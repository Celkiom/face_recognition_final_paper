import serial  # add Serial library for Serial communication


def ArduinoSignal(signal):
    Arduino_Serial = serial.Serial('com21', 9600)  # Create Serial port object called arduinoSerialData
    print(Arduino_Serial.readline())  # read the serial data and print it as line

    print("you entered", signal)  # prints the data for confirmation

    if signal == '1':  # if the entered data is 1
        Arduino_Serial.write(str.encode('1'))  # send 1 to arduino

    # if signal == '0':  # if the entered data is 0
    #     Arduino_Serial.write(str.encode('0'))  # send 0 to arduino
    #     # print("LED ON")


# ArduinoSignal('1')
