import mysql.connector
import serial

# przeniesc haslo do bazy i

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  passwd="123",
  database="users"
)
ser = serial.Serial("COM6", 9600)   # open serial port that Arduino is using

mycursor = mydb.cursor()
mycursor.execute("USE users")   # zmienic na aktualnie uzywana tabele (!!!)

print(ser.readline().decode('utf-8'))
temp = ser.readline().decode('utf-8')
temp_name = temp[0:5]                   # wybranie konkretnych danych z ciągu
temp_phone_number = temp[7:16]          # - || -


sql = "INSERT INTO users (name, phone_number) VALUES (%s, %s)"
val =  (temp_name,temp_phone_number)
mycursor.execute(sql, val)

mydb.commit()

# print(mycursor.rowcount, "record inserted.")  // uzywane do testu