import sys
from PyQt5 import QtWidgets
# from PyQt5.QtCore import pyqtSlot, QTime, QDate, QTimer
# from PyQt5.QtWidgets import QApplication, QDialog, QMainWindow, QWidget, QSlider, QTimeEdit, QDateEdit
# from PyQt5.QtWidgets import QMessageBox
from PyQt5.uic import loadUi
from time import sleep
import csv
import mysql.connector
import serial
import datetime
import matplotlib.pyplot as plt
import time
import winsound

import queue
import hashlib
import pandas as pd
import numpy as np
import matplotlib.dates as mdates
from datetime import datetime
from PyQt5.QtWidgets import QGridLayout, QSizePolicy
import pyqtgraph as pg
from random import randint

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

import datetime

import time
import traceback, sys

import logging

from pyfirmata import Arduino





########################################################################

result = None ## HASLO ZMIENIONE, NOWA BAZA !!! user / userpass
while result is None:   # wykonuje sie bez konca, jezeli nie uda sie polaczyc, potrzebne do logowania, ale infinite loop
    try:
          # auth = input("Podaj haslo do bazy:\n") # przeniesc to do "maina", wykonanie przed poczatkiem programu
        cnx = mysql.connector.connect(user = 'user', password = 'userpass', host = 'localhost', database = 'main_db')
        result = cnx
        print("...Connection established...")
    except:
        print("Connection failed")
        pass
cursor = cnx.cursor(buffered=True)

#######################################################################

port = "COM3"

ser = serial.Serial(port, 9600)   # open serial port that Arduino is using

ser.timeout=0.1

########################################################################

def encrypt_string(hash_string):
    sha_signature = \
        hashlib.sha256(hash_string.encode()).hexdigest()
    return sha_signature

#################################################################


   
#############################################################

class Worker(QRunnable):

    def __init__(self, *args, **kwargs):
        super(Worker, self).__init__()

        # Store constructor arguments (re-used for processing)
        self.args = args
        self.kwargs = kwargs 
     
    @pyqtSlot()
    def run(self):
        '''
        Initialise the runner function with passed args, kwargs.
        '''

#############################################################

class main_window(QMainWindow): # MAIN WINDOW
    def __init__(self, *args, **kwargs):
            super(main_window, self).__init__(*args, **kwargs)
            loadUi('gui_v4.ui', self)
            self.setWindowTitle("System monitorowania ruchu pacjentow")
            self.pushButtonObserve.clicked.connect(self.pushButtonObserveClicked)    # zmienic hello na cos innego
            # self.pushButtonInsert.clicked.connect(self.pushButtonInsertClicked)
            self.pushButtonBegin.clicked.connect(self.pushButtonBeginClicked)
            self.newPatientButton.clicked.connect(self.newPatientButtonClicked)
            self.newUserButton.clicked.connect(self.newUserButtonClicked)
            self.rangeSlider.setMinimum(10) # 10 sekund
            self.rangeSlider.setMaximum(180) # 3 * 60 sekund
            self.rangeSlider.setValue(60)   # ustalona wartosc poczatkowa
            self.rangeSlider.setTickInterval(18) # liczba "Tickow" nie do konca wydaje sie byc uzywana
            self.rangeSlider.setTickPosition(QSlider.TicksBelow) # ustalenie, ze Ticki (kreski) maja byc ponizej slidera
            self.rangeSlider.valueChanged.connect(self.v_change) # okreslenie akcji nastepujacej po przesunieciu slidera, w programie jest to zmiana wartosci odpowiedniego LineEdita
            self.sliderValueLineEdit.setText("60")    # ta wartosc ma odpowiadac rangeSlider.setValue(_)
            self.showHistoryButton.clicked.connect(self.showHistoryButtonClicked)
            self.pushButtonFilterHistoryPatient.clicked.connect(self.pushButtonFilterHistoryPatientClicked)
            self.pushButtonFilterLivePatient.clicked.connect(self.pushButtonFilterLivePatientClicked)
            self.editPatientButton.clicked.connect(self.editPatientButtonClicked)
            self.editUserButton.clicked.connect(self.editUserButtonClicked)
            self.newSensorButton.clicked.connect(self.newSensorButtonClicked)
            self.editSensorButton.clicked.connect(self.editSensorButtonClicked)
            self.assignSensorPushButton.clicked.connect(self.assignSensorPushButtonClicked)
            self.sendMsgPushButton.clicked.connect(self.sendMsgPushButtonClicked)
            self.pushButtonCleanEvents.clicked.connect(self.pushButtonCleanEventsClicked)
            
            self.threadpool = QThreadPool()
            
            self.current_user = None
    # do Begin dodac rowniez wykrywanie upadku i bezdechu
    def pushButtonCleanEventsClicked(self):
        
        worker = Worker()
        self.threadpool.start(worker)
        
        qm = QMessageBox
        ret = qm.question(self,'', "Czy na pewno chcesz wyczyscić listę zdarzeń?\n\n*zdarzenia można później wczytać z bazy danych", qm.Yes | qm.No)
        
        if ret == qm.Yes:
            self.eventList.clear()
    
    def sendMsgPushButtonClicked(self):
        
        python_to_arduino_msg_win.show()
        
        worker = Worker()
        self.threadpool.start(worker)
        
    def pushButtonBeginClicked(self):
        print("Rozpoczęto wczytywanie danych z monitora szeregowego...")
        notification_win.label.setText("\nRozpoczęto monitoring.\n")
        notification_win.show()
        self.counter = 0
        # -------------------------- dotyczy wykrywania --> UPADKU <-- pacjentow ---------------------------------------------
        self.dict_id_to_alarmvalue = {}
        ###################### #log #rejestr #zdarzenie ########################################################################################
        
        print("login: ",self.current_user)
        cursor.execute("SELECT ID_pracownika FROM personel WHERE login LIKE \"{jaki_login}\"".format(jaki_login=self.current_user))
        ID_pracownika = cursor.fetchall()[0][0]
        # print("Wyswietlanie ID pracownika na podstawie loginu...")
        # print(ID_pracownika)
        
        query = ("INSERT INTO rejestr_zdarzen (ID_pracownika,rodzaj_zdarzenia,opis_zdarzenia) VALUES (%s, %s, %s)")
        taxi = (ID_pracownika, "rozpoczecie pomiaru", "")
        cursor.execute(query, taxi)
        cnx.commit()
        self.eventList.insertItem(0, "rozpoczecie pomiaru, "+str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        ########################################################################################################################################
        # stworzenie Dictionary (slownika) z ID_czujnika przypisanymi do okr. pacjentow i wart. alar. tych pacj.
        cursor.execute("SELECT prz.ID_czujnika, pac.wartosc_alarmowa\
                        FROM przydzial_czujnikow prz\
                        JOIN pacjenci pac\
                        ON prz.ID_pacjenta = pac.ID_pacjenta;")
        print("...SELECT query succeeded...")
        myresult = cursor.fetchall()
        for x in myresult:
            print(x[0],x[1])
            self.dict_id_to_alarmvalue[str(x[0])] = str(x[1])
        # uzycie slownika: dict_id_to_alarmvalue[ID_czujnika] zwraca wartosc alarmowa
        #---------------------------------------------------------------------------------------------------------------------
        # ########################## dotyczy wykrywania --> BEZDECHU <-- pacjentow ###########################################
        arr_5s = np.linspace(100.01,101.50,150) # stworzenie wektora 151 wartosci, 1. wart. to ID czujnika, pozostale 150 to ostatnie wart. pomiarow
        self.df_sekw_bezdechu = 100*[arr_5s] # stworzenie df, gdzie kazdy numer wiersza oznacza ID czujnika, a wartosci w tym wierszu to kolejne pobrane pomiary
        ######################################################################################################################
        def execute_single_import():
            try:
                temp = ser.readline().decode('utf-8')
                temp=str(temp)
                temp = temp.split()
                # print(temp)
                
                query = ("INSERT INTO pomiary (ID_czujnika, modul, x_axis, y_axis, z_axis) VALUES (%s, %s, %s, %s, %s)")
                taxi = (temp[0], temp[1], temp[2], temp[3], temp[4])
                cursor.execute(query, taxi)
                
                id_czujnika = temp[0]
                mod = temp[1]
                x_value = temp[2]
                
                ###################################### dopisanie pomiaru do listy i sprawdzenie czy nie ma bezdechu, czyli czy max-min<0,3 przez 5[s]

                self.df_sekw_bezdechu[int(id_czujnika)] = np.roll(self.df_sekw_bezdechu[int(id_czujnika)],1) # przesuniecie listy pomiarow w prawo
                self.df_sekw_bezdechu[int(id_czujnika)][0] = float(x_value)
                np.set_printoptions(precision=2)
                np.set_printoptions(suppress=True)
                print(self.df_sekw_bezdechu[int(id_czujnika)])
                max_value = np.max(self.df_sekw_bezdechu[int(id_czujnika)])
                min_value = np.min(self.df_sekw_bezdechu[int(id_czujnika)])
                # print("max: {maxv}, min: {minv}, x_value: {x}".format(maxv=str(max_value),minv=str(min_value),x=x_value))
                if (max_value-min_value)<0.03:
                    cursor.execute("SELECT pac.imie, pac.nazwisko\
                                        FROM pacjenci pac\
                                            JOIN przydzial_czujnikow prz ON pac.ID_pacjenta=prz.ID_pacjenta\
                                                JOIN czujniki czu ON prz.ID_czujnika=czu.ID_czujnika\
                                                    WHERE czu.ID_czujnika={jakie_id};".format(jakie_id=temp[0]))
                    myresult = cursor.fetchall()
                    imie = myresult[0][0]
                    nazwisko = myresult[0][1]
                    
                    notification_win.label.setText("\nPacjent {jakie_imie} {jakie_nazwisko} nie wykazuje aktywnosci. Podejrzenie bezdechu.\n".format(jakie_imie=imie,jakie_nazwisko=nazwisko))
                    notification_win.show()
                    self.df_sekw_bezdechu[int(id_czujnika)] = arr_5s # wypelnienie sekwencji nie-bezdechem, aby zapobiec "spamowi" komunikatow o bezdechu
                    ###################### #log #rejestr #zdarzenie ########################################################################################

                    cursor.execute("SELECT ID_pracownika FROM personel WHERE login LIKE \"{jaki_login}\"".format(jaki_login=window.current_user))
                    ID_pracownika = cursor.fetchall()[0][0]
                    # print("Wyswietlanie ID pracownika na podstawie loginu...")
                    # print(ID_pracownika)
                    
                    query = ("INSERT INTO rejestr_zdarzen (ID_pracownika,rodzaj_zdarzenia,opis_zdarzenia) VALUES (%s, %s, %s)")
                    taxi = (ID_pracownika, "Bezdech - {jakie_imie} {jakie_nazwisko}".format(jakie_imie=imie,jakie_nazwisko=nazwisko), "")
                    cursor.execute(query, taxi)
                    cnx.commit()
                    window.eventList.insertItem(0, "Bezdech - {jakie_imie} {jakie_nazwisko}, ".format(jakie_imie=imie,jakie_nazwisko=nazwisko)+str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
                    
                    ########################################################################################################################################

                ###################################### sprawdzenie czy pacjent upadl
                #jesli modul przekroczy wartosc alar. otrzymana po podaniu ID_czujnika do slownika przechowujacego wart. alarmowe
                try:
                    # jezeli zmierzona wartosc modulu, czyli temp[1], jest wieksza niz wartosc alarmowa dla tego ID_czujnika, czyli slownik( temp[0] )
                    if (float(mod)>float(self.dict_id_to_alarmvalue[str(id_czujnika)])):
                        
                        cursor.execute("SELECT pac.imie, pac.nazwisko\
                                       FROM pacjenci pac\
                                           JOIN przydzial_czujnikow prz ON pac.ID_pacjenta=prz.ID_pacjenta\
                                               JOIN czujniki czu ON prz.ID_czujnika=czu.ID_czujnika\
                                                   WHERE czu.ID_czujnika={jakie_id};".format(jakie_id=temp[0]))
                        myresult = cursor.fetchall()
                        imie = myresult[0][0]
                        nazwisko = myresult[0][1]

                        print("Pacjent X Y upadl.")
                        notification_win.label.setText("\nPacjent {jakie_imie} {jakie_nazwisko} upadl.\n".format(jakie_imie=imie,jakie_nazwisko=nazwisko))
                        notification_win.show()

                        print("mod = "+str(float(temp[1]))+", dict_id_to_alarmvalue value = "+self.dict_id_to_alarmvalue [str(x[0])])
                        print("taxi: ",taxi)
                        ###################### #log #rejestr #zdarzenie ########################################################################################

                        cursor.execute("SELECT ID_pracownika FROM personel WHERE login LIKE \"{jaki_login}\"".format(jaki_login=window.current_user))
                        ID_pracownika = cursor.fetchall()[0][0]
                        # print("Wyswietlanie ID pracownika na podstawie loginu...")
                        # print(ID_pracownika)
                        
                        query = ("INSERT INTO rejestr_zdarzen (ID_pracownika,rodzaj_zdarzenia,opis_zdarzenia) VALUES (%s, %s, %s)")
                        taxi = (ID_pracownika, "Upadek - {jakie_imie} {jakie_nazwisko}".format(jakie_imie=imie,jakie_nazwisko=nazwisko), "")
                        cursor.execute(query, taxi)
                        cnx.commit()
                        window.eventList.insertItem(0, "Upadek - {jakie_imie} {jakie_nazwisko}, ".format(jakie_imie=imie,jakie_nazwisko=nazwisko)+str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
                        
                        ########################################################################################################################################
                except:
                    pass
                ######################################
                
                # if temp[1]>wartosc_graniczna_dla_danego_pacjenta
                
                # print("INSERT wykonany poprawnie")
                self.counter = self.counter + 1
                # print("counter zwiekszony, counter = ", self.counter)
                if ((self.counter%100)==0):
                    cnx.commit()
                    self.counter=0
                    print("Zaimportowano 100 rekordow. Wykonano commit w bazie danych.")
            except:
                pass
                #Exception as e: print(e)
                # print("Jeden pomiar nie został zaimportowany. Pomiar moze byc niepoprawny. \n")
                # pass
    
        self.timer = QTimer()
        self.timer.setInterval(10)
        self.timer.timeout.connect(lambda: execute_single_import())
        self.timer.start()
        
    ############################################# funkcja TESTOWA, import pliku .txt z pomiarami do bazy danych
    # def pushButtonInsertClicked(self):

    #     print("Writing .txt to SQL...")
                
    #     #Load text file into list with CSV module
    #     with open(r"C:\Users\matsz\Documents\original_kopia\Refactored_Py_DS_ML_Bootcamp-master\03-Python-for-Data-Analysis-Pandas/kuba - oddech 45 sekund, bezdech 30 sekund.TXT", "rt") as f:
    #         reader = csv.reader(f, delimiter = ' ', skipinitialspace=True)
    #         lineData = list()
    #         cols = next(reader)
        
    #         for line in reader:
    #             if line != []:
    #                 lineData.append(line)
                
    #     # Writing Query to insert data
    #     query = ("INSERT INTO pomiary (ID_czujnika, modul, x_axis, y_axis, z_axis) VALUES (%s, %s, %s, %s, %s)")
        
    #     #Change every item in the sub list into the correct data type and store it in a directory
    #     serie_bezdechu = pd.DataFrame()
    #     # ta petla for z zalozenia CHYBA nie pozwala na "wyjscie z niej do GUI", zeby pozwolic na interakcje
    #     # musi sie skonczyc cala petla zeby program w ogole ruszyl
    #     # for i in range(len(lineData)):
    #     #     try:
                
    #     #         taxi = (1, lineData[i][0], lineData[i][1], lineData[i][2], lineData[i][3]) # zamiast jedynki mozna wrzucic zmienna pobraną z pola EditText (trzeba takie dodać) gdzie uzytkownik wpisze numer czujnika z palca LUB jego ID
    #     def execute_and_pop(lista):
    #         taxi = (1, str(lista[0][0]), str(lista[0][1]), str(lista[0][2]), str(lista[0][3]))
    #         try:
    #             cursor.execute(query, taxi)
    #             lista.pop(0)
    #             cnx.commit()
    #         except:
    #             print("Błędny pomiar")
    #             print(taxi)
    #     self.timer = QTimer()
    #     self.timer.setInterval(1)
    #     self.timer.timeout.connect(lambda: execute_and_pop(lineData))
    #     self.timer.start()
    #     # cursor.execute(query, taxi) #Execute the Query
    #     # print(taxi)
    #     # sleep(0.03)
    #     # self.timer = QTimer()
    #     # self.timer.setInterval(1000)
    #     # self.timer.timeout.connect(self.showHistoryButtonClicked)
    #     # self.timer.start()
    #     # if lineData[i][0]>2.5:
    #     # if (i%1000)==0 and (i>0):
    #     #     print("1000" + " rows inserted, please wait...")
        
    #         # except:
    #         #     print("Błędny pomiar")
    #         #     print(taxi)
    #     print("Import finished.")
    #     #Commit the query
    #     cnx.commit()
###########################################################################################################################
    #         self.graphWidget = pg.PlotWidget()
    #         self.setCentralWidget(self.graphWidget)
    
    #         self.x = list(range(100))  # 100 time points
    #         self.y = [randint(0,100) for _ in range(100)]  # 100 data points
    
    #         self.graphWidget.setBackground('w')
    
    #         pen = pg.mkPen(color=(255, 0, 0))
    #         self.data_line =  self.graphWidget.plot(self.x, self.y, pen=pen)
    #         self.timer = QTimer()
    #         self.timer.setInterval(50)
    #         self.timer.timeout.connect(self.update_plot_data)
    #         self.timer.start()
    #         ##################################################################################################
    # def update_plot_data(self):

    #     self.x = self.x[1:]  # Remove the first y element.
    #     self.x.append(self.x[-1] + 1)  # Add a new value 1 higher than the last.
    
    #     self.y = self.y[1:]  # Remove the first 
    #     self.y.append( randint(0,100))  # Add a new random value.
    
    #     self.data_line.setData(self.x, self.y)  # Update the data.
#############################################################################################################################

###################################################### Wczytywanie pacjentow z bazy do Comboboxa Historii
    def assignSensorPushButtonClicked(self):
        assign_sensor_window.show()
        
        worker = Worker()
        self.threadpool.start(worker) 

    def editSensorButtonClicked(self):
        edit_sensor_window.show()
        
        worker = Worker()
        self.threadpool.start(worker) 

    def newSensorButtonClicked(self):
        new_sensor_window.show()
        
        worker = Worker()
        self.threadpool.start(worker) 

    def editPatientButtonClicked(self):
        edit_patient_window.show()
        
        worker = Worker()
        self.threadpool.start(worker) 

    def editUserButtonClicked(self):
        edit_user_window.show()
        
        worker = Worker()
        self.threadpool.start(worker) 

    def pushButtonFilterHistoryPatientClicked(self):
        self.patientHistoryComboBox.clear()
        
        worker = Worker()
        self.threadpool.start(worker) 
        
        print("Wybor pacjentow... ")

        seekHist = self.filterHistoryLineEdit.text()
        print(seekHist)
        try:
            cursor.execute("SELECT imie, nazwisko FROM pacjenci WHERE imie LIKE BINARY \'%{seek}%\' OR nazwisko LIKE BINARY \'%{seek}%\' OR ID_pacjenta LIKE BINARY \'%{seek}%\'".format(seek=seekHist))
            # usunac przedrostek BINARY, jezeli sie chce case_insensitive
            # cursor.execute("SELECT imie, nazwisko FROM pacjenci")
            print("...SELECT query succeeded...")
            
            # OK.... ale teraz jak w matplotlibie okreslic DATĘ jako os X, i x_axis jako os Y (x_axis to wartosci, os pionowa)
            
            myresult = cursor.fetchall()
            # print("The length of \'myresult\' is: ", len(myresult)) # pokazuje ile rekordow ma zostac wykorzystanych na wykresie
            pacjenci = []
            for x in myresult:
                        pacjenci.append(str(x[0])+" "+str(x[1]))
            self.patientHistoryComboBox.addItems(pacjenci)
            ###################################################################
        except:
            print("SELECT query failed")

        
    
    def pushButtonFilterLivePatientClicked(self):
        self.patientLiveComboBox.clear()
        worker = Worker()
        self.threadpool.start(worker) 
        
        print("Wybor pacjentow... ")
                #Connect with database

        seekLive = self.filterLiveLineEdit.text()
        print(seekLive)
        try:
            cursor.execute("SELECT imie, nazwisko FROM pacjenci WHERE imie LIKE BINARY \'%{seek}%\' OR nazwisko LIKE BINARY \'%{seek}%\' OR ID_pacjenta LIKE BINARY \'%{seek}%\'".format(seek=seekLive))
            # usunac przedrostek BINARY, jezeli sie chce case_insensitive
            # cursor.execute("SELECT imie, nazwisko FROM pacjenci")
            print("...SELECT query succeeded...")
            
            # OK.... ale teraz jak w matplotlibie okreslic DATĘ jako os X, i x_axis jako os Y (x_axis to wartosci, os pionowa)
            
            myresult = cursor.fetchall()
            # print("The length of \'myresult\' is: ", len(myresult)) # pokazuje ile rekordow ma zostac wykorzystanych na wykresie
            pacjenci = []
            for x in myresult:
                        pacjenci.append(str(x[0])+" "+str(x[1]))
            self.patientLiveComboBox.addItems(pacjenci)
            ###################################################################
        except:
            print("SELECT query failed")
    
        
        
    def showHistoryButtonClicked(self):
        print("showHistoryButtonClicked")
        worker = Worker()
        self.threadpool.start(worker) 
        
        timeFrom = QTime()
        timeTo = QTime()
        timeFrom = self.historyFromTimeEdit.time()
        timeTo = self.historyToTimeEdit.time()
        timeFromStr = timeFrom.toString()   # odczytana godzina w formacie HH:MM:DD
        timeToStr = timeTo.toString()   # odczytana godzina w formacie HH:MM:DD
        
        dateFrom = QDate()
        dateTo = QDate()
        dateFrom = self.historyFromDateEdit.date()
        dateTo = self.historyToDateEdit.date()
        dateFromStr = dateFrom.toString("yyyy-MM-dd")   # odczytana data w formacie RRRR-MM-DD
        dateToStr = dateTo.toString("yyyy-MM-dd")   # odczytana data w formacie RRRR-MM-DD
        
        dateTimeFrom = dateFromStr + " " + timeFromStr
        dateTimeTo = dateToStr + " " + timeToStr
        # dateTimeFrom i dateTimeTo sa uzywane w SELECTie historii, do okreslenia zakresu
        # wybraniu zakresu, os X zawiera sekundy, poniewaz w przypadku daty na osi X, bylo wiele pomiarow w jednej sekundzie, wiele kropek w pionie i wykres byl totalnie nieczytalny.
        
###################################################### Odczytywanie czasu z widgetow ^^^^^^^^^^^^^^^
        
        print("Drukowanie wykresu HISTORII wybranego pacjenta...")

        print(dateTimeFrom)
        print(dateTimeTo)
        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! WAZNE
        # teraz odczytac imie i nazwisko (A MOZE COS JESZCZE?...) i na podstawie tego zJOINOWAC ID_czujnika i na podstawie ID czujnika dodać to do WHERE historii i tak samo LIVE'a
        wybrany_pacjent = self.patientHistoryComboBox.currentText()
        try:
            wybrany_pacjent = wybrany_pacjent.split()
            wybrane_imie = wybrany_pacjent[0]
            wybrane_nazwisko = wybrany_pacjent[1]
        except:
            pass
        print("SELECT ID_pomiaru, x_axis FROM pomiary WHERE data_i_czas_pomiaru BETWEEN \'{data_i_czas_od}\' AND \'{data_i_czas_do}\' AND WHERE ID_czujnika==1 SELECT ID_czujnika FROM przydzial_czujnikow WHERE ID_czujnika".format(data_i_czas_od=dateTimeFrom,data_i_czas_do=dateTimeTo))
        try:
            cursor.execute("SELECT ID_pomiaru, x_axis\
                            FROM pomiary pom\
                            INNER JOIN czujniki cz\
                            ON pom.ID_czujnika=cz.ID_czujnika\
                            INNER JOIN przydzial_czujnikow prz\
                            ON prz.ID_czujnika=cz.ID_czujnika\
                            INNER JOIN pacjenci pac\
                            ON prz.ID_pacjenta=pac.ID_pacjenta\
                            WHERE pac.imie LIKE \'{imie}\' AND pac.nazwisko LIKE \'{nazwisko}\';".format(imie=wybrane_imie,nazwisko=wybrane_nazwisko))
            
            print("...SELECT query succeeded...")
            
            # OK.... ale teraz jak w matplotlibie okreslic DATĘ jako os X, i x_axis jako os Y (x_axis to wartosci, os pionowa)
            
            myresult = cursor.fetchall()
            # print("The length of \'myresult\' is: ", len(myresult)) # pokazuje ile rekordow ma zostac wykorzystanych na wykresie
            array_x = []
            array_y = []
            for x in myresult:
                        array_x.append(float(x[0]))
                        array_y.append(float(x[1]))
            ###################################################################
            fig = plt.figure(figsize=(18, 16), dpi= 80, facecolor='w', edgecolor='k')
            ax = plt.subplot(111)
            # NADAC ODPOWIEDNI LABEL ZALEZNIE OD IMIENIA PACJENTA # TODO #
            line1, = ax.plot(np.arange(0,len(array_x)*0.03,0.03), array_y, label='Historia ruchu')
            
            # Shrink current axis's height by 10% on the bottom
            box = ax.get_position()
            ax.set_position([box.x0, box.y0 + box.height * 0.1,
                             box.width, box.height * 0.9])
            # Put a legend below current axis
            ax.legend(loc='upper right', bbox_to_anchor=(0.4, 1.0),
                      ncol=3, fancybox=True, shadow=True)
            plt.xlabel("czas [s]")
            plt.ylabel("amplituda [g]")
            # plt.title("Wykres oddechu pięciu badanych osób")
            plt.grid()
            # ax.yaxis.set_ticks(np.arange(-0.1,0.5,0.05))
            plt.show()
        except:
            print("SELECT query failed")
            notification_win.label.setText("Niepowodzenie wyswietlania wykresu. Nie wybrano pacjenta lub nie udało się połączyć z bazą danych. \n\nUpewnij się, czy kliknięto przycisk Filtruj.")
            notification_win.show()
        
############################################################## Rysowanie wykresu z historii ^^^^^^^^^^^^^^ @ UP
        
    def v_change(self):
        value = str(self.rangeSlider.value())
        self.sliderValueLineEdit.setText(value)
        worker = Worker()
        self.threadpool.start(worker) 
        
    def pushButtonObserveClicked(self):    # funkcja testowa, usunac lub wymienic na inna
        print("Drukowanie wykresu...")
        worker = Worker()
        self.threadpool.start(worker) 

        # dodatkowo uzaleznic wyswietlane rekordy od wybranego pacjenta, imienia, MAC czujnika, ID pacjenta czy cokolwiek # TODO #
        # na podstawie slidera okreslic zakres --> dac zamiast 10000 przeskalowana wartosc
        if int(self.sliderValueLineEdit.text()) < 10 or int(self.sliderValueLineEdit.text()) > 3000:
            self.sliderValueLineEdit.setText("60")
            
        jaki_zakres = self.sliderValueLineEdit.text()
        print("Podany zakres czasu powinien zawierac sie w zakresie od 10 do 3000 sekund.")
        
        wybrany_pacjent = self.patientLiveComboBox.currentText()
        try:
            wybrany_pacjent = wybrany_pacjent.split()
            wybrane_imie = wybrany_pacjent[0]
            wybrane_nazwisko = wybrany_pacjent[1]
        except:
            pass
        try:
            cursor.execute("SELECT ID_pomiaru,x_axis      \
                            FROM pomiary pom              \
                            INNER JOIN czujniki cz        \
                            ON pom.ID_czujnika=cz.ID_czujnika  \
                            INNER JOIN przydzial_czujnikow prz \
                            ON prz.ID_czujnika=cz.ID_czujnika  \
                            INNER JOIN pacjenci pac            \
                            ON prz.ID_pacjenta=pac.ID_pacjenta \
                            WHERE pac.imie LIKE \'{imie}\'          \
                            AND pac.nazwisko LIKE \'{nazwisko}\'   \
                            AND ID_pomiaru > ((SELECT MAX(ID_pomiaru) FROM pomiary)-(33*{sekundy}));".format(imie=wybrane_imie,nazwisko=wybrane_nazwisko,sekundy=jaki_zakres))
            print("...SELECT query succeeded...")
            myresult = cursor.fetchall()
            # print("The length of \'myresult\' is: ", len(myresult)) # pokazuje ile rekordow ma zostac wykorzystanych na wykresie
            array_x = []
            array_y = []
            for x in myresult:
                        array_x.append(float(x[0]))
                        array_y.append(float(x[1]))
            ###################################################################
            fig = plt.figure(figsize=(18, 16), dpi= 80, facecolor='w', edgecolor='k')
            ax = plt.subplot(111)
            # NADAC ODPOWIEDNI LABEL ZALEZNIE OD IMIENIA PACJENTA # TODO #
            line1, = ax.plot(np.arange(0,len(array_x)*0.03,0.03), array_y, label='{imie_i_nazwisko}'.format(imie_i_nazwisko=wybrane_imie+" "+wybrane_nazwisko))
            
            # Shrink current axis's height by 10% on the bottom
            box = ax.get_position()
            ax.set_position([box.x0, box.y0 + box.height * 0.1,
                             box.width, box.height * 0.9])
            # Put a legend below current axis
            ax.legend(loc='upper right', bbox_to_anchor=(0.4, 1.0),
                      ncol=3, fancybox=True, shadow=True)
            plt.xlabel("czas [s]")
            plt.ylabel("amplituda [g]")
            # plt.title("Wykres oddechu pięciu badanych osób")
            plt.grid()
            # ax.yaxis.set_ticks(np.arange(-0.1,0.5,0.05))
            plt.show()
            self.currentPersonLabel.setText(self.patientLiveComboBox.currentText())
        except:
            print("SELECT query failed")
            self.currentPersonLabel.setText("---")
            notification_win.label.setText("Niepowodzenie wyswietlania wykresu. Nie wybrano pacjenta lub nie udało się połączyć z bazą danych. \n\nUpewnij się, czy kliknięto przycisk Filtruj.")
            notification_win.show()
        
        
#######################################################################################################################

        
        
######################################################################################## funkcje otwierajace nowe okna po kliknieciu przycisku w glownym GUI
    def newPatientButtonClicked(self):
        print("Adding new patient...")
        new_patient_window.show()
        
        worker = Worker()
        self.threadpool.start(worker) 
        
    def newUserButtonClicked(self):
        print("Adding new user...")
        new_user_window.show()
        
        worker = Worker()
        self.threadpool.start(worker) 


class new_patient(QMainWindow):    #

    
    def __init__(self):
        QMainWindow.__init__(self)
        loadUi('add_patient_gui.ui', self)
        self.setWindowTitle("Dodawanie nowego pacjenta")
        self.pushButtonAdd.clicked.connect(self.pushButtonAddClicked)
        self.pushButtonAbort.clicked.connect(self.pushButtonAbortClicked)
        self.birthDateLineEdit.setPlaceholderText("RRRR-MM-DD")
        self.emailLineEdit.setPlaceholderText("email@address.com")
        
        self.sexComboBox.addItem("Mężczyzna")
        self.sexComboBox.addItem("Kobieta")
        
        self.threadpool = QThreadPool()
        

    def pushButtonAbortClicked(self):
        new_patient_window.hide()
        
        worker = Worker()
        self.threadpool.start(worker) 
    def pushButtonAddClicked(self):
        
        imie = self.nameLineEdit.text()
        nazwisko = self.surnameLineEdit.text()
        # plec = self.sexLineEdit.text()
        plec = self.sexComboBox.currentText()
        data_urodzenia = self.birthDateLineEdit.text()
        PESEL = self.peselLineEdit.text()        
        telefon = self.phoneLineEdit.text()
        email = self.emailLineEdit.text()
        kod_pocztowy = self.cityCodeLineEdit.text()
        miejscowosc = self.cityLineEdit.text()
        ulica = self.streetLineEdit.text()
        wartosc_alarmowa = self.alarmValueLineEdit.text()
        
        worker = Worker()
        self.threadpool.start(worker) 
        
        #Writing Query to insert data
        query = ("INSERT INTO pacjenci (imie, nazwisko, plec, data_urodzenia, PESEL, telefon, email, kod_pocztowy, miejscowosc, ulica, wartosc_alarmowa) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
        
        taxi = (imie, nazwisko, plec, data_urodzenia, PESEL ,telefon, email, kod_pocztowy, miejscowosc, ulica, wartosc_alarmowa) # zamiast jedynki mozna wrzucic zmienna pobraną z pola EditText (trzeba takie dodać) gdzie uzytkownik wpisze numer czujnika z palca LUB jego ID
        try:
            cursor.execute(query, taxi) #Execute the Query
            cnx.commit()
            print("Dodano nowego pacjenta.")
            # Czyszczenie wprowadzonego tekstu
            self.nameLineEdit.setText("")
            self.surnameLineEdit.setText("")
            # self.sexLineEdit.setText("") # zmienić na combobox?, nie, comboboxa plci NIE TRZEBA czyscic !!!
            self.sexComboBox.clear()
            self.sexComboBox.addItem("Mężczyzna")
            self.sexComboBox.addItem("Kobieta")
            self.birthDateLineEdit.setText("")
            self.peselLineEdit.setText("")        
            self.phoneLineEdit.setText("")
            self.emailLineEdit.setText("")
            self.cityCodeLineEdit.setText("")
            self.cityLineEdit.setText("")
            self.streetLineEdit.setText("")
            self.alarmValueLineEdit.setText("")
            notification_win.label.setText("Dodano nowego pacjenta.")
            notification_win.show()
            # TODO # zarejestrowac ta akcje w logach zdarzen
            ###################### #log #rejestr #zdarzenie ########################################################################################
            
            cursor.execute("SELECT ID_pracownika FROM personel WHERE login LIKE \"{jaki_login}\"".format(jaki_login=window.current_user))
            ID_pracownika = cursor.fetchall()[0][0]
            # print("Wyswietlanie ID pracownika na podstawie loginu...")
            # print(ID_pracownika)
            
            query = ("INSERT INTO rejestr_zdarzen (ID_pracownika,rodzaj_zdarzenia,opis_zdarzenia) VALUES (%s, %s, %s)")
            taxi = (ID_pracownika, "Dodanie pacjenta {jakie_imie} {jakie_nazwisko}".format(jakie_imie=imie,jakie_nazwisko=nazwisko), "")
            cursor.execute(query, taxi)
            cnx.commit()
            window.eventList.insertItem(0, "Dodanie pacjenta {jakie_imie} {jakie_nazwisko}, ".format(jakie_imie=imie,jakie_nazwisko=nazwisko)+str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            
            ########################################################################################################################################
            new_patient_window.hide()
        except:
            notification_win.label.setText("Niepoprawne dane. Zwróć uwagę, czy data urodzenia oraz email mają poprawny format.")
            notification_win.show()
            cnx.rollback()
        

class edit_patient(QMainWindow):    #


    def __init__(self):
        QMainWindow.__init__(self)
        loadUi('edit_patient_gui.ui', self)
        self.setWindowTitle("Edycja danych pacjenta")
        self.pushButtonSaveChanges.clicked.connect(self.pushButtonSaveChangesClicked)
        self.pushButtonAbort.clicked.connect(self.pushButtonAbortClicked)
        self.birthDateLineEdit.setPlaceholderText("RRRR-MM-DD")
        self.emailLineEdit.setPlaceholderText("email@address.com")
        self.pushButtonFilterEditPatient.clicked.connect(self.pushButtonFilterEditPatientClicked)
        self.pushButtonLoadToEditPatient.clicked.connect(self.pushButtonLoadToEditPatientClicked)
        self.pushButtonDeletePatient.clicked.connect(self.pushButtonDeletePatientClicked)
        
        self.threadpool = QThreadPool()

    def pushButtonFilterEditPatientClicked(self):
        # Filtrowanie pacjentow
        self.patientToEditComboBox.clear()
        
        worker = Worker()
        self.threadpool.start(worker) 
        
        print("Wybor pacjentow... ")

        seekToEdit = self.filterToEditLineEdit.text()
        print(seekToEdit)
        try:
            cursor.execute("SELECT imie, nazwisko FROM pacjenci WHERE imie LIKE BINARY \'%{seek}%\' OR nazwisko LIKE BINARY \'%{seek}%\' OR ID_pacjenta LIKE BINARY \'%{seek}%\'".format(seek=seekToEdit))
            # usunac przedrostek BINARY, jezeli sie chce case_insensitive
            # cursor.execute("SELECT imie, nazwisko FROM pacjenci")
            print("...SELECT query succeeded...")
            
            # OK.... ale teraz jak w matplotlibie okreslic DATĘ jako os X, i x_axis jako os Y (x_axis to wartosci, os pionowa)
            
            myresult = cursor.fetchall()
            # print("The length of \'myresult\' is: ", len(myresult)) # pokazuje ile rekordow ma zostac wykorzystanych na wykresie
            pacjenci = []
            for x in myresult:
                        pacjenci.append(str(x[0])+" "+str(x[1]))
            self.patientToEditComboBox.addItems(pacjenci)
            ###################################################################
        except:
            print("SELECT query failed")

        
    
    def pushButtonLoadToEditPatientClicked(self):
        
        print("Ladowanie danych pacjenta... ")
        
        worker = Worker()
        self.threadpool.start(worker) 

        # seekHist = self.filterToEditLineEdit.text()
        # print(seekHist)
        wybrany_pacjent = self.patientToEditComboBox.currentText()
        try:
            wybrany_pacjent = wybrany_pacjent.split()
            wybrane_imie = wybrany_pacjent[0]
            wybrane_nazwisko = wybrany_pacjent[1]
        except:
            pass
        try:
            cursor.execute("SELECT imie, nazwisko, plec, data_urodzenia, PESEL, telefon, email, kod_pocztowy, miejscowosc, ulica, wartosc_alarmowa FROM pacjenci WHERE imie LIKE \'%{imie}%\' AND nazwisko LIKE \'%{nazwisko}%\'".format(imie=wybrane_imie, nazwisko=wybrane_nazwisko))
            # usunac przedrostek BINARY, jezeli sie chce case_insensitive
            # cursor.execute("SELECT imie, nazwisko FROM pacjenci")
            print("...SELECT query succeeded...")
            
            # OK.... ale teraz jak w matplotlibie okreslic DATĘ jako os X, i x_axis jako os Y (x_axis to wartosci, os pionowa)
            
            myresult = cursor.fetchall()
            # print("The length of \'myresult\' is: ", len(myresult)) # pokazuje ile rekordow ma zostac wykorzystanych na wykresie
            # pacjenci = []
            for x in myresult:
                # pacjenci.append(str(x[0])+" "+str(x[1]))
                self.nameLineEdit.setText(str(x[0]))
                self.surnameLineEdit.setText(str(x[1]))
                # self.sexLineEdit.setText(str(x[2]))
                self.sexComboBox.clear()
                self.sexComboBox.addItem(str(x[2]))
                if self.sexComboBox.currentText()[0]=="M":
                    self.sexComboBox.addItem("Kobieta")
                else:
                    self.sexComboBox.addItem("Mezczyzna")
                self.birthDateLineEdit.setText(str(x[3]))
                self.peselLineEdit.setText(str(x[4]))     
                self.phoneLineEdit.setText(str(x[5]))
                self.emailLineEdit.setText(str(x[6]))
                self.cityCodeLineEdit.setText(str(x[7]))
                self.cityLineEdit.setText(str(x[8]))
                self.streetLineEdit.setText(str(x[9]))
                self.alarmValueLineEdit.setText(str(x[10]))
            ###################################################################
        except:
            print("SELECT query failed")

        
    

    def pushButtonAbortClicked(self):
        edit_patient_window.hide()
        
        worker = Worker()
        self.threadpool.start(worker) 
        
    def pushButtonSaveChangesClicked(self):
        
        noweImie = self.nameLineEdit.text()
        noweNazwisko = self.surnameLineEdit.text()
        # nowaPlec = self.sexLineEdit.text()
        nowaPlec = self.sexComboBox.currentText()
        nowaData_urodzenia = self.birthDateLineEdit.text()
        nowyPESEL = self.peselLineEdit.text()        
        nowyTelefon = self.phoneLineEdit.text()
        nowyEmail = self.emailLineEdit.text()
        nowyKod_pocztowy = self.cityCodeLineEdit.text()
        nowaMiejscowosc = self.cityLineEdit.text()
        nowaUlica = self.streetLineEdit.text()
        nowaWartoscAlarmowa = self.alarmValueLineEdit.text()
        
        worker = Worker()
        self.threadpool.start(worker) 
        
        #Writing Query to insert data
        # Przekazanie, ktora osoba ma zostac edytowana do buttona potwierdzajacego i wykonujacego UPDATE
        # Pobranie tych danych z aktualnego ComboBoxa
        wybrany_pacjent = self.patientToEditComboBox.currentText()
        try:
            wybrany_pacjent = wybrany_pacjent.split()
            wybrane_imie = wybrany_pacjent[0]
            wybrane_nazwisko = wybrany_pacjent[1]
        except:
            pass
        
        query = ("UPDATE pacjenci SET imie=\'{imie2}\', nazwisko=\'{nazwisko2}\', plec=\'{plec2}\', data_urodzenia=\'{data_urodzenia2}\', PESEL=\'{PESEL2}\',\
                 telefon=\'{telefon2}\', email=\'{email2}\', kod_pocztowy=\'{kod_pocztowy2}\', miejscowosc=\'{miejscowosc2}\', ulica=\'{ulica2}\', wartosc_alarmowa=\'{wartosc_alarmowa2}\' WHERE imie LIKE\
                     \'{jakie_imie}\' AND nazwisko LIKE '\{jakie_nazwisko}\'".format(imie2=noweImie,nazwisko2=noweNazwisko,plec2=nowaPlec,\
                         data_urodzenia2=nowaData_urodzenia,PESEL2=nowyPESEL,telefon2=nowyTelefon,email2=nowyEmail,kod_pocztowy2=nowyKod_pocztowy,\
                             miejscowosc2=nowaMiejscowosc,ulica2=nowaUlica,wartosc_alarmowa2=nowaWartoscAlarmowa,jakie_imie=wybrane_imie,jakie_nazwisko=wybrane_nazwisko))
        
        # taxi = (imie, nazwisko, plec, data_urodzenia, PESEL ,telefon, email, kod_pocztowy, miejscowosc, ulica) # zamiast jedynki mozna wrzucic zmienna pobraną z pola EditText (trzeba takie dodać) gdzie uzytkownik wpisze numer czujnika z palca LUB jego ID
        try:
            cursor.execute(query) #Execute the Query
            cnx.commit()
            print("Zmieniono dane pacjenta.")
            # Czyszczenie wprowadzonego tekstu
            self.nameLineEdit.setText("")
            self.surnameLineEdit.setText("")
            # self.sexLineEdit.setText("")
            self.sexComboBox.clear()
            self.birthDateLineEdit.setText("")
            self.peselLineEdit.setText("")        
            self.phoneLineEdit.setText("")
            self.emailLineEdit.setText("")
            self.cityCodeLineEdit.setText("")
            self.cityLineEdit.setText("")
            self.streetLineEdit.setText("")
            self.alarmValueLineEdit.setText("")
            
            notification_win.label.setText("Zmieniono dane pacjenta.")
            notification_win.show()
            # TODO # zarejestrowac ta akcje w logach zdarzen
            ###################### #log #rejestr #zdarzenie ########################################################################################
            
            cursor.execute("SELECT ID_pracownika FROM personel WHERE login LIKE \"{jaki_login}\"".format(jaki_login=window.current_user))
            ID_pracownika = cursor.fetchall()[0][0]
            # print("Wyswietlanie ID pracownika na podstawie loginu...")
            # print(ID_pracownika)
            
            query = ("INSERT INTO rejestr_zdarzen (ID_pracownika,rodzaj_zdarzenia,opis_zdarzenia) VALUES (%s, %s, %s)")
            taxi = (ID_pracownika, "Zmiana danych pacjenta {jakie_imie} {jakie_nazwisko}".format(jakie_imie=wybrane_imie,jakie_nazwisko=wybrane_nazwisko), "")
            cursor.execute(query, taxi)
            cnx.commit()
            window.eventList.insertItem(0, "Zmiana danych pacjenta {jakie_imie} {jakie_nazwisko}, ".format(jakie_imie=wybrane_imie,jakie_nazwisko=wybrane_nazwisko)+str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            
            ########################################################################################################################################

        except:
            notification_win.label.setText("Niepoprawne dane. Zwróć uwagę, czy data urodzenia oraz email mają poprawny format.")
            notification_win.show()
            cnx.rollback()
        

    def pushButtonDeletePatientClicked(self):
        
        worker = Worker()
        self.threadpool.start(worker) 
        
        #Writing Query to insert data
        # Przekazanie, ktora osoba ma zostac edytowana do buttona potwierdzajacego i wykonujacego UPDATE
        # Pobranie tych danych z aktualnego ComboBoxa
        
        ### Czekanie na potwierdzenie ...
        # TODO pytanie o potwierdzenie skasowania pacjenta
        # w zamysle po potwierdzeniu usuniecia w oknie delete_confirm_window powinno sie zamknac to okno i kontynuowac operacje ponizej czyli usuniecie pacjenta
        confirmed = 1
        # delete_confirm_window.show()
          
        qm = QMessageBox
        ret = qm.question(self,'', "Czy na pewno chcesz usunąć tego pacjenta?", qm.Yes | qm.No)
        
        if ret == qm.Yes:
            try:
                wybrany_pacjent = self.patientToEditComboBox.currentText()
                
                wybrany_pacjent = wybrany_pacjent.split()
                wybrane_imie = wybrany_pacjent[0]
                wybrane_nazwisko = wybrany_pacjent[1]
                
                
                query = ("DELETE FROM pacjenci WHERE imie LIKE \'{jakie_imie}\' AND nazwisko LIKE '\{jakie_nazwisko}\'".\
                         format(jakie_imie=wybrane_imie,jakie_nazwisko=wybrane_nazwisko))
                
                # taxi = (imie, nazwisko, plec, data_urodzenia, PESEL ,telefon, email, kod_pocztowy, miejscowosc, ulica) # zamiast jedynki mozna wrzucic zmienna pobraną z pola EditText (trzeba takie dodać) gdzie uzytkownik wpisze numer czujnika z palca LUB jego ID
    
            
                cursor.execute(query) #Execute the Query
                cnx.commit()
                print("Usunieto pacjenta {jakie_imie} {jakie_nazwisko}.".format(jakie_imie=wybrane_imie,jakie_nazwisko=wybrane_nazwisko))
                # Czyszczenie wprowadzonego tekstu
                self.nameLineEdit.setText("")
                self.surnameLineEdit.setText("")
                # self.sexLineEdit.setText("")
                self.sexComboBox.clear()
                self.birthDateLineEdit.setText("")
                self.peselLineEdit.setText("")        
                self.phoneLineEdit.setText("")
                self.emailLineEdit.setText("")
                self.cityCodeLineEdit.setText("")
                self.cityLineEdit.setText("")
                self.streetLineEdit.setText("")
                
                ###################### #log #rejestr #zdarzenie ########################################################################################
                
                cursor.execute("SELECT ID_pracownika FROM personel WHERE login LIKE \"{jaki_login}\"".format(jaki_login=window.current_user))
                ID_pracownika = cursor.fetchall()[0][0]
                # print("Wyswietlanie ID pracownika na podstawie loginu...")
                # print(ID_pracownika)
                
                query = ("INSERT INTO rejestr_zdarzen (ID_pracownika,rodzaj_zdarzenia,opis_zdarzenia) VALUES (%s, %s, %s)")
                taxi = (ID_pracownika, "Usuniecie pacjenta {jakie_imie} {jakie_nazwisko}".format(jakie_imie=wybrane_imie,jakie_nazwisko=wybrane_nazwisko), "")
                cursor.execute(query, taxi)
                cnx.commit()
                window.eventList.insertItem(0, "Usuniecie pacjenta {jakie_imie} {jakie_nazwisko}, ".format(jakie_imie=wybrane_imie,jakie_nazwisko=wybrane_nazwisko)+str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
                
                ########################################################################################################################################

                
                notification_win.label.setText("Usunieto pacjenta {jakie_imie} {jakie_nazwisko}.".format(jakie_imie=wybrane_imie,jakie_nazwisko=wybrane_nazwisko))
                notification_win.show()
                # TODO # zarejestrowac ta akcje w logach zdarzen
            except Exception as e:
                print(e)
                notification_win.label.setText("Wystapil problem podczas usuwania pacjenta. Sprawdz czy pacjent zostal wybrany.")
                notification_win.show()
                cnx.rollback()
            
        else:

            print("")

class new_sensor(QMainWindow):    #
   
    def __init__(self):
        QMainWindow.__init__(self)
        loadUi('add_sensor_gui.ui', self)
        self.setWindowTitle("Dodawanie nowego czujnika")
        self.pushButtonAdd.clicked.connect(self.pushButtonAddClicked)
        self.pushButtonAddDefaultID.clicked.connect(self.pushButtonAddDefaultIDClicked)
        self.pushButtonAbort.clicked.connect(self.pushButtonAbortClicked)
        self.macLineEdit.setPlaceholderText("AABBCCDDEEFF")
        
        self.threadpool = QThreadPool()
        

    def pushButtonAbortClicked(self):
        new_patient_window.hide()
        
        worker = Worker()
        self.threadpool.start(worker) 
        
    def pushButtonAddDefaultIDClicked(self):
        
        worker = Worker()
        self.threadpool.start(worker) 
        
        mac_address = self.macLineEdit.text()
        
        #Writing Query to insert data
        query = ("INSERT INTO czujniki (MAC_czujnika) VALUES (\'{jaki_mac}\')".format(jaki_mac=mac_address))
        
        # taxi = (mac_address) # zamiast jedynki mozna wrzucic zmienna pobraną z pola EditText (trzeba takie dodać) gdzie uzytkownik wpisze numer czujnika z palca LUB jego ID
        try:
            cursor.execute(query) #Execute the Query
            cnx.commit()
            print("Dodano nowy czujnik.")
            # Czyszczenie wprowadzonego tekstu
            self.macLineEdit.setText("")
            self.sensorIDLineEdit.setText("")

            notification_win.label.setText("Dodano nowy czujnik.")
            notification_win.show()
            # TODO # zarejestrowac ta akcje w logach zdarzen
            ###################### #log #rejestr #zdarzenie ########################################################################################
            
            cursor.execute("SELECT ID_pracownika FROM personel WHERE login LIKE \"{jaki_login}\"".format(jaki_login=window.current_user))
            ID_pracownika = cursor.fetchall()[0][0]
            # print("Wyswietlanie ID pracownika na podstawie loginu...")
            # print(ID_pracownika)
            
            query = ("INSERT INTO rejestr_zdarzen (ID_pracownika,rodzaj_zdarzenia,opis_zdarzenia) VALUES (%s, %s, %s)")
            taxi = (ID_pracownika, "Dodano czujnik, MAC: {jaki_mac}".format(jaki_mac=mac_address), "")
            cursor.execute(query, taxi)
            cnx.commit()
            window.eventList.insertItem(0, "Dodano czujnik, MAC: {jaki_mac}, ".format(jaki_mac=mac_address)+str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            
            ########################################################################################################################################

            
            new_sensor_window.hide()
        except:
            notification_win.label.setText("Niepoprawne dane. Zwróć uwagę, czy data urodzenia oraz email mają poprawny format.")
            notification_win.show()
            # TODO zmienic komunikat, optymalnie wymusic znaki 0-9, A-F
            cnx.rollback()
        
    def pushButtonAddClicked(self):
        
        worker = Worker()
        self.threadpool.start(worker) 
        
        mac_address = self.macLineEdit.text()
        sensor_id = self.sensorIDLineEdit.text()
        
        #Writing Query to insert data
        query = ("INSERT INTO czujniki (ID_czujnika, MAC_czujnika) VALUES (\'{jakie_id}\', \'{jaki_mac}\')".format(jakie_id = sensor_id,jaki_mac=mac_address))
        
        # taxi = (mac_address) # zamiast jedynki mozna wrzucic zmienna pobraną z pola EditText (trzeba takie dodać) gdzie uzytkownik wpisze numer czujnika z palca LUB jego ID
        try:
            cursor.execute(query) #Execute the Query
            cnx.commit()
            print("Dodano nowy czujnik.")
            # Czyszczenie wprowadzonego tekstu
            self.macLineEdit.setText("")
            self.sensorIDLineEdit.setText("")

            notification_win.label.setText("Dodano nowy czujnik.")
            notification_win.show()
            
            # TODO # zarejestrowac ta akcje w logach zdarzen
            ###################### #log #rejestr #zdarzenie ########################################################################################
            
            cursor.execute("SELECT ID_pracownika FROM personel WHERE login LIKE \"{jaki_login}\"".format(jaki_login=window.current_user))
            ID_pracownika = cursor.fetchall()[0][0]
            # print("Wyswietlanie ID pracownika na podstawie loginu...")
            # print(ID_pracownika)
            
            query = ("INSERT INTO rejestr_zdarzen (ID_pracownika,rodzaj_zdarzenia,opis_zdarzenia) VALUES (%s, %s, %s)")
            taxi = (ID_pracownika, "Dodano czujnik, MAC: {jaki_mac}".format(jaki_mac=mac_address), "")
            cursor.execute(query, taxi)
            cnx.commit()
            window.eventList.insertItem(0, "Dodano czujnik, MAC: {jaki_mac}, ".format(jaki_mac=mac_address)+str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            
            ########################################################################################################################################
            new_sensor_window.hide()
        except:
            notification_win.label.setText("Nie udało się dodać czujnika.\nPodane ID czujnika może już istnieć w bazie danych.")
            notification_win.show()
            # TODO zmienic komunikat, optymalnie wymusic znaki 0-9, A-F
            cnx.rollback()
        

class edit_sensor(QMainWindow):    #

    def __init__(self):
        
        QMainWindow.__init__(self)
        loadUi('edit_sensor_gui.ui', self)
        self.setWindowTitle("Edytowanie danych czujnika")
        self.pushButtonSaveChanges.clicked.connect(self.pushButtonSaveChangesClicked)
        self.pushButtonAbort.clicked.connect(self.pushButtonAbortClicked)
        self.macLineEdit.setPlaceholderText("AABBCCDDEEFF")
        self.pushButtonFilter.clicked.connect(self.pushButtonFilterClicked)
        self.pushButtonLoad.clicked.connect(self.pushButtonLoadClicked)
        self.pushButtonDelete.clicked.connect(self.pushButtonDeleteClicked)
        
        sizePolicy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.pushButtonDelete.setSizePolicy(sizePolicy)
        
        self.threadpool = QThreadPool()
        
        self.previous_mac = "Default mac string"
    
    def pushButtonFilterClicked(self):
        
        worker = Worker()
        self.threadpool.start(worker) 
        
        # Filtrowanie pacjentow
        self.chooseToEditComboBox.clear()
        
        print("Wybor czujnika... ")

        seekToEdit = self.filterToEditLineEdit.text()
        print(seekToEdit)
        try:

            cursor.execute("SELECT cz.ID_czujnika, cz.MAC_czujnika, IFNULL(pac.imie,'-'), IFNULL(pac.nazwisko,'-')\
                           FROM czujniki cz\
                           LEFT JOIN przydzial_czujnikow prz\
                           ON cz.ID_czujnika=prz.ID_czujnika\
                           LEFT JOIN pacjenci pac\
                           ON prz.ID_pacjenta=pac.ID_pacjenta\
                               WHERE cz.ID_czujnika LIKE \'%{seek}%\' OR cz.MAC_czujnika LIKE \'%{seek}%\'\
                                   OR pac.imie LIKE \'%{seek}%\' OR pac.nazwisko LIKE \'%{seek}%\'".format(seek=seekToEdit))
            # LEFT JOIN ma na celu pokazanie rowniez czujnikow nie przypisanych do zadnego pacjenta
            # wyswietlanie imienia i nazwiska obok ID oraz MAC ma na celu podpowiedzenie uzytkownikowi, kogo dotyczy wybrany czujnik, czy jest "wolny"
            # usunac przedrostek BINARY, jezeli sie chce case_insensitive
            # cursor.execute("SELECT imie, nazwisko FROM pacjenci")
            print("...SELECT query succeeded...")
            
            # OK.... ale teraz jak w matplotlibie okreslic DATĘ jako os X, i x_axis jako os Y (x_axis to wartosci, os pionowa)
            
            myresult = cursor.fetchall()
            # print("The length of \'myresult\' is: ", len(myresult)) # pokazuje ile rekordow ma zostac wykorzystanych na wykresie
            czujniki = []
            for x in myresult:
                        czujniki.append(str(x[0])+" "+str(x[1])+" "+str(x[2])+" "+str(x[3]))
            self.chooseToEditComboBox.addItems(czujniki)
            
        except:
            print("SELECT query failed")

        
    
    def pushButtonLoadClicked(self):
        
        worker = Worker()
        self.threadpool.start(worker) 
        
        print("Ladowanie danych czujnika... ")

        # seekHist = self.filterToEditLineEdit.text()
        # print(seekHist)
        wybrany_czujnik = self.chooseToEditComboBox.currentText()
        try:
            wybrany_czujnik = wybrany_czujnik.split()
            wybrane_id = wybrany_czujnik[0]
        except:
            pass
        try:
            cursor.execute("SELECT ID_czujnika, MAC_czujnika FROM czujniki WHERE ID_czujnika={jakie_id}".format(jakie_id=wybrane_id))
            # usunac przedrostek BINARY, jezeli sie chce case_insensitive
            # cursor.execute("SELECT imie, nazwisko FROM pacjenci")
            print("...SELECT query succeeded...")
            
            # OK.... ale teraz jak w matplotlibie okreslic DATĘ jako os X, i x_axis jako os Y (x_axis to wartosci, os pionowa)
            
            myresult = cursor.fetchall()
            # print("The length of \'myresult\' is: ", len(myresult)) # pokazuje ile rekordow ma zostac wykorzystanych na wykresie
            # pacjenci = []
            for x in myresult:
                # pacjenci.append(str(x[0])+" "+str(x[1]))
                self.idLineEdit.setText(str(x[0]))
                self.macLineEdit.setText(str(x[1]))
            ###################################################################
        except:
            print("SELECT query failed")
        self.previous_mac = self.macLineEdit.text()

        
    

    def pushButtonAbortClicked(self):
        edit_patient_window.hide()
        
        worker = Worker()
        self.threadpool.start(worker) 
        
    def pushButtonSaveChangesClicked(self):
        
        worker = Worker()
        self.threadpool.start(worker) 
        
        noweID = self.idLineEdit.text()
        nowyMAC = self.macLineEdit.text()

        #Writing Query to insert data
        # Przekazanie, ktora osoba ma zostac edytowana do buttona potwierdzajacego i wykonujacego UPDATE
        # Pobranie tych danych z aktualnego ComboBoxa
        wybrany_czujnik = self.chooseToEditComboBox.currentText()
        try:
            wybrany_czujnik = wybrany_czujnik.split()
            wybrane_id = wybrany_czujnik[0]
        except:
            pass
        
        query = ("UPDATE czujniki SET ID_czujnika={ID_czujnika2}, MAC_czujnika=\'{MAC_czujnika2}\' WHERE ID_czujnika={jakie_id}"\
                 .format(ID_czujnika2=noweID,MAC_czujnika2=nowyMAC,jakie_id=wybrane_id))
        
        # taxi = (imie, nazwisko, plec, data_urodzenia, PESEL ,telefon, email, kod_pocztowy, miejscowosc, ulica) # zamiast jedynki mozna wrzucic zmienna pobraną z pola EditText (trzeba takie dodać) gdzie uzytkownik wpisze numer czujnika z palca LUB jego ID
        try:
            cursor.execute(query) #Execute the Query
            cnx.commit()
            print("Zmieniono dane czujnika.")
            # Czyszczenie wprowadzonego tekstu
            self.idLineEdit.setText("")
            self.macLineEdit.setText("")
            
            self.pushButtonFilterClicked()

            notification_win.label.setText("Zmieniono dane czujnika.")
            notification_win.show()
            # TODO # zarejestrowac ta akcje w logach zdarzen
            ###################### #log #rejestr #zdarzenie ########################################################################################
            
            cursor.execute("SELECT ID_pracownika FROM personel WHERE login LIKE \"{jaki_login}\"".format(jaki_login=window.current_user))
            ID_pracownika = cursor.fetchall()[0][0]
            # print("Wyswietlanie ID pracownika na podstawie loginu...")
            # print(ID_pracownika)
            
            query = ("INSERT INTO rejestr_zdarzen (ID_pracownika,rodzaj_zdarzenia,opis_zdarzenia) VALUES (%s, %s, %s)")
            taxi = (ID_pracownika, "Zmiana MAC czujnika z {stary_mac} na {jaki_mac}".format(stary_mac=self.previous_mac, jaki_mac=nowyMAC), "")
            cursor.execute(query, taxi)
            cnx.commit()
            window.eventList.insertItem(0, "Zmiana MAC czujnika z {stary_mac} na {jaki_mac}, ".format(stary_mac=self.previous_mac, jaki_mac=nowyMAC)+str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            
            ########################################################################################################################################

        except:
            notification_win.label.setText("Niepoprawne dane. Zwróć uwagę, czy data urodzenia oraz email mają poprawny format.")
            notification_win.show()
            cnx.rollback()
        

    def pushButtonDeleteClicked(self):
        
        worker = Worker()
        self.threadpool.start(worker) 
        
        #Writing Query to insert data
        # Przekazanie, ktora osoba ma zostac edytowana do buttona potwierdzajacego i wykonujacego UPDATE
        # Pobranie tych danych z aktualnego ComboBoxa
        
        ### Czekanie na potwierdzenie ...
        # TODO pytanie o potwierdzenie skasowania pacjenta
        # w zamysle po potwierdzeniu usuniecia w oknie delete_confirm_window powinno sie zamknac to okno i kontynuowac operacje ponizej czyli usuniecie pacjenta
        confirmed = 1
        # delete_confirm_window.show()
          
        qm = QMessageBox
        ret = qm.question(self,'', "Czy na pewno chcesz usunąć ten czujnik?", qm.Yes | qm.No)
        
        if ret == qm.Yes:
            try:
                wybrany_czujnik = self.chooseToEditComboBox.currentText()
                
                
                wybrany_czujnik = wybrany_czujnik.split()
                wybrane_id = wybrany_czujnik[0]
                mac_usuwanego_czujnika = wybrany_czujnik[1]
                
                
                query = ("DELETE FROM czujniki WHERE ID_czujnika={jakie_id}".\
                         format(jakie_id=int(wybrane_id)))
                
                # taxi = (imie, nazwisko, plec, data_urodzenia, PESEL ,telefon, email, kod_pocztowy, miejscowosc, ulica) # zamiast jedynki mozna wrzucic zmienna pobraną z pola EditText (trzeba takie dodać) gdzie uzytkownik wpisze numer czujnika z palca LUB jego ID
    
            
                cursor.execute(query) #Execute the Query
                cnx.commit()
                print("Usunieto czujnik z bazy, MAC: {jaki_mac}.".format(jaki_mac=mac_usuwanego_czujnika))
                # Czyszczenie wprowadzonego tekstu
                self.idLineEdit.setText("")
                self.macLineEdit.setText("")
                
                self.pushButtonFilterClicked()

                notification_win.label.setText("Usunieto czujnik z bazy danych. MAC: {jaki_mac}.".format(jaki_mac=mac_usuwanego_czujnika))
                notification_win.show()
                # TODO # zarejestrowac ta akcje w logach zdarzen
                ###################### #log #rejestr #zdarzenie ########################################################################################
            
                cursor.execute("SELECT ID_pracownika FROM personel WHERE login LIKE \"{jaki_login}\"".format(jaki_login=window.current_user))
                ID_pracownika = cursor.fetchall()[0][0]
                # print("Wyswietlanie ID pracownika na podstawie loginu...")
                # print(ID_pracownika)
                
                query = ("INSERT INTO rejestr_zdarzen (ID_pracownika,rodzaj_zdarzenia,opis_zdarzenia) VALUES (%s, %s, %s)")
                taxi = (ID_pracownika, "Usunieto czujnik, MAC: {jaki_mac}".format(jaki_mac=mac_usuwanego_czujnika), "")
                cursor.execute(query, taxi)
                cnx.commit()
                window.eventList.insertItem(0, "Usunieto czujnik, MAC: {jaki_mac}, ".format(jaki_mac=mac_usuwanego_czujnika)+str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
                
                ########################################################################################################################################

            except:
                notification_win.label.setText("Wystapil problem podczas usuwania czujnika. Sprawdz czy pacjent zostal wybrany.")
                notification_win.show()
                cnx.rollback()
            
        else:

            print("")

class assign_sensor(QMainWindow):    #

    def __init__(self):
        QMainWindow.__init__(self)
        loadUi('assign_sensor_gui.ui', self)
        self.setWindowTitle("Zmiana przypisania czujnikow")
        self.pushButtonAbort.clicked.connect(self.pushButtonAbortClicked)
        self.pushButtonFilter.clicked.connect(self.pushButtonFilterClicked)
        self.pushButtonAssign.clicked.connect(self.pushButtonAssignClicked)
        self.pushButtonFilterEditPatient.clicked.connect(self.pushButtonFilterEditPatientClicked)
        self.pushButtonDelete.clicked.connect(self.pushButtonDeleteClicked)
        #-------------------------------------------------------------------------- nie dokonczone skalowanie okna
        sizePolicy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.pushButtonDelete.setSizePolicy(sizePolicy)
        
        self.threadpool = QThreadPool()
        
        self.MAC_assigned = "Replace with ID..."
        self.assigned_to_name = "Replace with name"
        self.assigned_to_surname = "Replace with surname"
        
    def pushButtonFilterClicked(self):
        # Filtrowanie pacjentow
        self.chooseToEditComboBox.clear()
        
        print("Wybor czujnika... ")
        
        worker = Worker()
        self.threadpool.start(worker) 

        seekToEdit = self.filterToEditLineEdit.text()
        print(seekToEdit)
        try:

            cursor.execute("SELECT cz.ID_czujnika, cz.MAC_czujnika, IFNULL(pac.imie,'-'), IFNULL(pac.nazwisko,'-')\
                           FROM czujniki cz\
                           LEFT JOIN przydzial_czujnikow prz\
                           ON cz.ID_czujnika=prz.ID_czujnika\
                           LEFT JOIN pacjenci pac\
                           ON prz.ID_pacjenta=pac.ID_pacjenta\
                               WHERE cz.ID_czujnika LIKE BINARY \'%{seek}%\' OR cz.MAC_czujnika LIKE BINARY \'%{seek}%\'\
                                   OR pac.imie LIKE BINARY \'%{seek}%\' OR pac.nazwisko LIKE BINARY \'%{seek}%\'".format(seek=seekToEdit))
            # LEFT JOIN ma na celu pokazanie rowniez czujnikow nie przypisanych do zadnego pacjenta
            # wyswietlanie imienia i nazwiska obok ID oraz MAC ma na celu podpowiedzenie uzytkownikowi, kogo dotyczy wybrany czujnik, czy jest "wolny"
            # usunac przedrostek BINARY, jezeli sie chce case_insensitive
            # cursor.execute("SELECT imie, nazwisko FROM pacjenci")
            print("...SELECT query succeeded...")
            
            # OK.... ale teraz jak w matplotlibie okreslic DATĘ jako os X, i x_axis jako os Y (x_axis to wartosci, os pionowa)
            
            myresult = cursor.fetchall()
            # print("The length of \'myresult\' is: ", len(myresult)) # pokazuje ile rekordow ma zostac wykorzystanych na wykresie
            czujniki = []
            for x in myresult:
                        czujniki.append(str(x[0])+" "+str(x[1])+" "+str(x[2])+" "+str(x[3]))
            self.chooseToEditComboBox.addItems(czujniki)

        except:
            print("SELECT query failed")

        
    
    def pushButtonFilterEditPatientClicked(self):
        # Filtrowanie pacjentow
        self.patientToEditComboBox.clear()
        
        worker = Worker()
        self.threadpool.start(worker) 
        
        print("Wybor pacjentow... ")

        seekToEdit = self.filterPatientLineEdit.text()
        print(seekToEdit)
        try:
            cursor.execute("SELECT ID_pacjenta, imie, nazwisko FROM pacjenci WHERE imie LIKE BINARY \'%{seek}%\' OR nazwisko LIKE BINARY \'%{seek}%\' OR ID_pacjenta LIKE BINARY \'%{seek}%\'".format(seek=seekToEdit))
            # usunac przedrostek BINARY, jezeli sie chce case_insensitive
            # cursor.execute("SELECT imie, nazwisko FROM pacjenci")
            print("...SELECT query succeeded...")
            
            # OK.... ale teraz jak w matplotlibie okreslic DATĘ jako os X, i x_axis jako os Y (x_axis to wartosci, os pionowa)
            
            myresult = cursor.fetchall()
            # print("The length of \'myresult\' is: ", len(myresult)) # pokazuje ile rekordow ma zostac wykorzystanych na wykresie
            pacjenci = []
            for x in myresult:
                        pacjenci.append(str(x[0])+" "+str(x[1])+" "+str(x[2]))
            self.patientToEditComboBox.addItems(pacjenci)
            ###################################################################
        except:
            print("SELECT query failed")

        
    
    def pushButtonAbortClicked(self):
        edit_patient_window.hide()
        
        worker = Worker()
        self.threadpool.start(worker) 
        
    def pushButtonAssignClicked(self):
        
        worker = Worker()
        self.threadpool.start(worker) 
        
        #Writing Query to insert data
        # Przekazanie, ktora osoba ma zostac edytowana do buttona potwierdzajacego i wykonujacego UPDATE
        # Pobranie tych danych z aktualnego ComboBoxa
        
        wybrany_czujnik = self.chooseToEditComboBox.currentText()
        wybrany_pacjent = self.patientToEditComboBox.currentText()
        # do ustawienia comboboxow na okreslonych elementach, po wykonaniu zmian
        id_of_assigned = self.chooseToEditComboBox.currentIndex()
        id_of_chosen_patient = self.patientToEditComboBox.currentIndex()
        
        try:
            wybrany_czujnik = wybrany_czujnik.split()
            wybrane_id = wybrany_czujnik[0]
            
            MAC_assigned = wybrany_czujnik[1]
            
            wybrany_pacjent = wybrany_pacjent.split()
            wybrane_id_pacjenta = wybrany_pacjent[0]
            wybrane_imie = wybrany_pacjent[1]
            wybrane_nazwisko = wybrany_pacjent[2]
                        
            print("Udalo sie odczytac dane z ComboBoxow")
        except:
            pass
        
        query = ("INSERT INTO przydzial_czujnikow (ID_pacjenta,ID_czujnika,status) VALUES ({ID_pacjenta_2},{ID_czujnika_2},'default')"\
                     .format(ID_pacjenta_2=wybrane_id_pacjenta,ID_czujnika_2=wybrane_id))
        print("query: "+query)
        # taxi = (imie, nazwisko, plec, data_urodzenia, PESEL ,telefon, email, kod_pocztowy, miejscowosc, ulica) # zamiast jedynki mozna wrzucic zmienna pobraną z pola EditText (trzeba takie dodać) gdzie uzytkownik wpisze numer czujnika z palca LUB jego ID
        try:
            cursor.execute(query) #Execute the Query
            cnx.commit()
            print("Dodano nowe przypisanie.")
            # Czyszczenie wprowadzonego tekstu
            self.filterToEditLineEdit.setText("")
            self.filterPatientLineEdit.setText("")
            
            self.pushButtonFilterClicked()
            self.chooseToEditComboBox.setCurrentIndex(id_of_assigned)
            
            self.pushButtonFilterEditPatientClicked()
            self.patientToEditComboBox.setCurrentIndex(id_of_chosen_patient)

            notification_win.label.setText("Dodano nowe przypisanie.")
            notification_win.show()
            # TODO # zarejestrowac ta akcje w logach zdarzen
            ###################### #log #rejestr #zdarzenie ########################################################################################
            
            cursor.execute("SELECT ID_pracownika FROM personel WHERE login LIKE \"{jaki_login}\"".format(jaki_login=window.current_user))
            ID_pracownika = cursor.fetchall()[0][0]
            # print("Wyswietlanie ID pracownika na podstawie loginu...")
            # print(ID_pracownika)
            
            query = ("INSERT INTO rejestr_zdarzen (ID_pracownika,rodzaj_zdarzenia,opis_zdarzenia) VALUES (%s, %s, %s)")
            taxi = (ID_pracownika, "Przypisano czujnik, MAC: {jaki_mac} pacjentowi {jakie_imie} {jakie_nazwisko}, ".format(jaki_mac=MAC_assigned,jakie_imie=wybrane_imie,jakie_nazwisko=wybrane_nazwisko), "")
            cursor.execute(query, taxi)
            cnx.commit()
            window.eventList.insertItem(0, "Przypisano czujnik, MAC: {jaki_mac} pacjentowi {jakie_imie} {jakie_nazwisko}, ".format(jaki_mac=MAC_assigned,jakie_imie=wybrane_imie,jakie_nazwisko=wybrane_nazwisko)+str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            
            ########################################################################################################################################

        except Exception as e:
            print(e)
            notification_win.label.setText("Nie udalo się dodać przypisania.\nWybrany czujnik może już być przypisany do innego pacjenta.\n\nUsuń przypisanie i spróbuj ponownie.")
            notification_win.show()
            cnx.rollback()
        

    def pushButtonDeleteClicked(self):
        
        worker = Worker()
        self.threadpool.start(worker)
        #Writing Query to insert data
        # Przekazanie, ktora osoba ma zostac edytowana do buttona potwierdzajacego i wykonujacego UPDATE
        # Pobranie tych danych z aktualnego ComboBoxa
        
        ### Czekanie na potwierdzenie ...
        # TODO pytanie o potwierdzenie skasowania pacjenta
        # w zamysle po potwierdzeniu usuniecia w oknie delete_confirm_window powinno sie zamknac to okno i kontynuowac operacje ponizej czyli usuniecie pacjenta
        confirmed = 1
        # delete_confirm_window.show()
          
        qm = QMessageBox
        ret = qm.question(self,'', "Czy na pewno chcesz usunąć to przypisanie?", qm.Yes | qm.No)
        
        if ret == qm.Yes:
            try:
                wybrany_czujnik = self.chooseToEditComboBox.currentText()
                
                wybrany_czujnik = wybrany_czujnik.split()
                wybrane_id = wybrany_czujnik[0]
                
                id_of_deleted = self.chooseToEditComboBox.currentIndex()
                id_of_chosen_patient = self.patientToEditComboBox.currentIndex()
                
                query = ("DELETE FROM przydzial_czujnikow WHERE ID_czujnika={jakie_id}".\
                          format(jakie_id=int(wybrane_id)))
                
                # taxi = (imie, nazwisko, plec, data_urodzenia, PESEL ,telefon, email, kod_pocztowy, miejscowosc, ulica) # zamiast jedynki mozna wrzucic zmienna pobraną z pola EditText (trzeba takie dodać) gdzie uzytkownik wpisze numer czujnika z palca LUB jego ID
    
            
                cursor.execute(query) #Execute the Query
                cnx.commit()
                print("Usunieto czujnik z bazy.")
                ######################################### potrzebne do rejestru zdarzen
                
                wybrany_czujnik = self.chooseToEditComboBox.currentText()
                wybrany_pacjent = self.patientToEditComboBox.currentText()
                try:
                    wybrany_czujnik = wybrany_czujnik.split()
                    wybrane_id = wybrany_czujnik[0]
                    
                    MAC_assigned = wybrany_czujnik[1]
                    
                    wybrany_pacjent = wybrany_pacjent.split()
                    wybrane_id_pacjenta = wybrany_pacjent[0]
                    wybrane_imie = wybrany_pacjent[1]
                    wybrane_nazwisko = wybrany_pacjent[2]
                except:
                    pass
                
                #########################################
                # Czyszczenie wprowadzonego tekstu
                self.filterToEditLineEdit.setText("")
                self.filterPatientLineEdit.setText("")
                
                self.pushButtonFilterClicked()
                self.chooseToEditComboBox.setCurrentIndex(id_of_deleted)
                self.pushButtonFilterEditPatientClicked()
                self.patientToEditComboBox.setCurrentIndex(id_of_chosen_patient)

                notification_win.label.setText("Usunieto przypisanie z bazy.")
                notification_win.show()
                # TODO # zarejestrowac ta akcje w logach zdarzen
                ###################### #log #rejestr #zdarzenie ########################################################################################

                cursor.execute("SELECT ID_pracownika FROM personel WHERE login LIKE \"{jaki_login}\"".format(jaki_login=window.current_user))
                ID_pracownika = cursor.fetchall()[0][0]
                # print("Wyswietlanie ID pracownika na podstawie loginu...")
                # print(ID_pracownika)
                
                query = ("INSERT INTO rejestr_zdarzen (ID_pracownika,rodzaj_zdarzenia,opis_zdarzenia) VALUES (%s, %s, %s)")
                taxi = (ID_pracownika, "Usunieto przypisanie czujnika, MAC: {jaki_mac} , pacjent: {jakie_imie} {jakie_nazwisko}, ".format(jaki_mac=MAC_assigned,jakie_imie=wybrane_imie,jakie_nazwisko=wybrane_nazwisko), "")
                cursor.execute(query, taxi)
                cnx.commit()
                window.eventList.insertItem(0, "Usunieto przypisanie czujnika, MAC: {jaki_mac} , pacjent: {jakie_imie} {jakie_nazwisko}, ".format(jaki_mac=MAC_assigned,jakie_imie=wybrane_imie,jakie_nazwisko=wybrane_nazwisko)+str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
                
                ########################################################################################################################################

            except:
                notification_win.label.setText("Wystapil problem podczas usuwania przypisania. Sprawdz czy pacjent zostal wybrany.")
                notification_win.show()
                cnx.rollback()
            
        else:

            print("")

# delete_patient_confirm NIE JEST UZYWANY, zamiast tego uzyto QMessageBox, nieoptymalny bo nie ma polskich napisow, tylko Yes, No, ale dziala
# class delete_patient_confirm(QMainWindow):
#     def __init__(self):
#         QMainWindow.__init__(self)
#         loadUi('delete_patient_confirm.ui', self)
        
#         self.pushButtonDelete.clicked.connect(self.pushButtonDeleteClicked)
#         self.pushButtonAbort.clicked.connect(self.pushButtonAbortClicked)
#     def pushButtonDeleteClicked(self):
#         edit_patient.confirmed = 1
#     def pushButtonAbortClicked(self):
#         delete_confirm_window.hide() # edit_patient_window
    
class new_user(QMainWindow):    #
    
    def __init__(self):
        QMainWindow.__init__(self)
        loadUi('add_user_gui.ui', self)
        self.setWindowTitle("Dodawanie nowego pacjenta")
        self.pushButtonAdd.clicked.connect(self.pushButtonAddClicked)
        self.pushButtonAbort.clicked.connect(self.pushButtonAbortClicked)
        self.birthDateLineEdit.setPlaceholderText("RRRR-MM-DD")
        self.hireDateLineEdit.setPlaceholderText("RRRR-MM-DD")
        self.emailLineEdit.setPlaceholderText("email@address.com")
        self.passwordLineEdit.setEchoMode(QtWidgets.QLineEdit.Password)
        
        self.sexComboBox.addItem("Mężczyzna")
        self.sexComboBox.addItem("Kobieta")
        # TODO # wymagac od loginu minimum 5 znakow, od hasla optymalnie 8+ znakow i A-Z, a-z, 0-9
        
        self.threadpool = QThreadPool()
        

    def pushButtonAbortClicked(self):
        new_patient_window.hide()
        
        worker = Worker()
        self.threadpool.start(worker) 
        
    def pushButtonAddClicked(self):
        
        imie = self.nameLineEdit.text()
        nazwisko = self.surnameLineEdit.text()
        # plec = self.sexLineEdit.text()
        plec = self.sexComboBox.currentText()
        data_urodzenia = self.birthDateLineEdit.text()
        PESEL = self.peselLineEdit.text()
        data_zatrudnienia = self.hireDateLineEdit.text()
        login = self.loginLineEdit.text()
        zaszyfrowane_haslo = encrypt_string(self.passwordLineEdit.text()) # zamiana hasla jawnego na hash
        print(zaszyfrowane_haslo) # TODO # mozna skasowac, wyswietlenie kontrolne
        telefon = self.nameLineEdit.text()
        email = self.emailLineEdit.text()
        kod_pocztowy = self.cityCodeLineEdit.text()
        miejscowosc = self.cityLineEdit.text()
        ulica = self.streetLineEdit.text()
        
        worker = Worker()
        self.threadpool.start(worker) 
        
        #Writing Query to insert data
        query = ("INSERT INTO personel (imie, nazwisko, plec, data_urodzenia, PESEL, data_zatrudnienia, login, zaszyfrowane_haslo, telefon, email, kod_pocztowy, miejscowosc, ulica) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
        
        taxi = (imie, nazwisko, plec, data_urodzenia, PESEL , data_zatrudnienia, login, zaszyfrowane_haslo, telefon, email, kod_pocztowy, miejscowosc, ulica) # zamiast jedynki mozna wrzucic zmienna pobraną z pola EditText (trzeba takie dodać) gdzie uzytkownik wpisze numer czujnika z palca LUB jego ID
        try:
            cursor.execute(query, taxi) #Execute the Query
            cnx.commit()
            print("Dodano nowego pracownika.")
            self.nameLineEdit.setText("")
            self.surnameLineEdit.setText("")
            # self.sexLineEdit.setText("")
            self.sexComboBox.clear()
            self.sexComboBox.addItem("Mężczyzna")
            self.sexComboBox.addItem("Kobieta")
            self.birthDateLineEdit.setText("")
            self.peselLineEdit.setText("")
            self.hireDateLineEdit.setText("")
            self.loginLineEdit.setText("")
            self.passwordLineEdit.setText("")
            self.phoneLineEdit.setText("")
            self.emailLineEdit.setText("")
            self.cityCodeLineEdit.setText("")
            self.cityLineEdit.setText("")
            self.streetLineEdit.setText("")
            
            notification_win.label.setText("Dodano nowego pracownika.")
            notification_win.show()
            # TODO # zarejestrowac ta akcje w logach zdarzen
            ###################### #log #rejestr #zdarzenie ########################################################################################
            
            cursor.execute("SELECT ID_pracownika FROM personel WHERE login LIKE \"{jaki_login}\"".format(jaki_login=window.current_user))
            ID_pracownika = cursor.fetchall()[0][0]
            # print("Wyswietlanie ID pracownika na podstawie loginu...")
            # print(ID_pracownika)
            
            query = ("INSERT INTO rejestr_zdarzen (ID_pracownika,rodzaj_zdarzenia,opis_zdarzenia) VALUES (%s, %s, %s)")
            taxi = (ID_pracownika, "Dodano pracownika {jakie_imie} {jakie_nazwisko}, ".format(jakie_imie=imie,jakie_nazwisko=nazwisko), "")
            cursor.execute(query, taxi)
            cnx.commit()
            window.eventList.insertItem(0, "Dodano pracownika {jakie_imie} {jakie_nazwisko}, ".format(jakie_imie=imie,jakie_nazwisko=nazwisko)+str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            
            ########################################################################################################################################
            new_user_window.hide()
        except:
            print("Niepoprawne dane. Zwróć uwagę, czy data urodzenia oraz email mają poprawny format.")
            cnx.rollback()
        

class edit_user(QMainWindow):    #


    def __init__(self):
        QMainWindow.__init__(self)
        loadUi('edit_user_gui.ui', self)
        self.setWindowTitle("Edycja danych pracownika")
        self.pushButtonSaveChanges.clicked.connect(self.pushButtonSaveChangesClicked)
        self.pushButtonAbort.clicked.connect(self.pushButtonAbortClicked)
        self.birthDateLineEdit.setPlaceholderText("RRRR-MM-DD")
        self.hireDateLineEdit.setPlaceholderText("RRRR-MM-DD")
        self.emailLineEdit.setPlaceholderText("email@address.com")
        self.pushButtonFilterEditUser.clicked.connect(self.pushButtonFilterEditUserClicked)
        self.pushButtonLoadToEditUser.clicked.connect(self.pushButtonLoadToEditUserClicked)
        self.pushButtonDeleteUser.clicked.connect(self.pushButtonDeleteUserClicked)
        
        self.sexComboBox.addItem("Mężczyzna")
        self.sexComboBox.addItem("Kobieta")
        
        self.threadpool = QThreadPool()
        
    def pushButtonFilterEditUserClicked(self):
        # Filtrowanie pacjentow
        self.userToEditComboBox.clear()
        
        worker = Worker()
        self.threadpool.start(worker) 
        
        print("Wybor pracownikow... ")

        seekToEdit = self.filterToEditLineEdit.text()
        print(seekToEdit)
        try:
            cursor.execute("SELECT imie, nazwisko FROM personel WHERE imie LIKE BINARY \'%{seek}%\' OR nazwisko LIKE BINARY \'%{seek}%\' OR ID_pracownika LIKE BINARY \'%{seek}%\'".format(seek=seekToEdit))
            # usunac przedrostek BINARY, jezeli sie chce case_insensitive
            # cursor.execute("SELECT imie, nazwisko FROM pacjenci")
            print("...SELECT query succeeded...")
            
            # OK.... ale teraz jak w matplotlibie okreslic DATĘ jako os X, i x_axis jako os Y (x_axis to wartosci, os pionowa)
            
            myresult = cursor.fetchall()
            # print("The length of \'myresult\' is: ", len(myresult)) # pokazuje ile rekordow ma zostac wykorzystanych na wykresie
            pracownicy = []
            for x in myresult:
                        pracownicy.append(str(x[0])+" "+str(x[1]))
            self.userToEditComboBox.addItems(pracownicy)
            ###################################################################
        except:
            print("SELECT query failed")

        
    
    def pushButtonLoadToEditUserClicked(self):
        
        worker = Worker()
        self.threadpool.start(worker) 
        
        print("Ladowanie danych pracownika... ")

        # seekHist = self.filterToEditLineEdit.text()
        # print(seekHist)
        wybrany_pracownik = self.userToEditComboBox.currentText()
        try:
            wybrany_pracownik = wybrany_pracownik.split()
            wybrane_imie = wybrany_pracownik[0]
            wybrane_nazwisko = wybrany_pracownik[1]
        except:
            pass
        try:
            cursor.execute("SELECT imie, nazwisko, plec, data_urodzenia, PESEL, data_zatrudnienia, telefon, email, kod_pocztowy, miejscowosc, ulica FROM personel WHERE imie LIKE \'%{imie}%\' AND nazwisko LIKE \'%{nazwisko}%\'".format(imie=wybrane_imie, nazwisko=wybrane_nazwisko))
            # usunac przedrostek BINARY, jezeli sie chce case_insensitive
            # cursor.execute("SELECT imie, nazwisko FROM pacjenci")
            print("...SELECT query succeeded...")
            
            # OK.... ale teraz jak w matplotlibie okreslic DATĘ jako os X, i x_axis jako os Y (x_axis to wartosci, os pionowa)
            
            myresult = cursor.fetchall()
            # print("The length of \'myresult\' is: ", len(myresult)) # pokazuje ile rekordow ma zostac wykorzystanych na wykresie
            # pacjenci = []
            for x in myresult:
                # pacjenci.append(str(x[0])+" "+str(x[1]))
                self.nameLineEdit.setText(str(x[0]))
                self.surnameLineEdit.setText(str(x[1]))
                # self.sexLineEdit.setText(str(x[2]))
                self.sexComboBox.clear()
                self.sexComboBox.addItem(str(x[2]))
                if self.sexComboBox.currentText()[0]=="M":
                    self.sexComboBox.addItem("Kobieta")
                else:
                    self.sexComboBox.addItem("Mezczyzna")
                self.birthDateLineEdit.setText(str(x[3]))
                self.peselLineEdit.setText(str(x[4]))
                self.hireDateLineEdit.setText(str(x[5]))
                self.phoneLineEdit.setText(str(x[6]))
                self.emailLineEdit.setText(str(x[7]))
                self.cityCodeLineEdit.setText(str(x[8]))
                self.cityLineEdit.setText(str(x[9]))
                self.streetLineEdit.setText(str(x[10]))
            ###################################################################
        except:
            print("SELECT query failed")

    def pushButtonAbortClicked(self):
        edit_patient_window.hide()
        
        worker = Worker()
        self.threadpool.start(worker) 
        
    def pushButtonSaveChangesClicked(self):
        
        noweImie = self.nameLineEdit.text()
        noweNazwisko = self.surnameLineEdit.text()
        nowaPlec = self.sexComboBox.currentText()
        nowaData_urodzenia = self.birthDateLineEdit.text()
        nowyPESEL = self.peselLineEdit.text()
        nowaData_zatrudnienia = self.hireDateLineEdit.text()
        nowyTelefon = self.phoneLineEdit.text()
        nowyEmail = self.emailLineEdit.text()
        nowyKod_pocztowy = self.cityCodeLineEdit.text()
        nowaMiejscowosc = self.cityLineEdit.text()
        nowaUlica = self.streetLineEdit.text()
        
        worker = Worker()
        self.threadpool.start(worker) 
        
        #Writing Query to insert data
        # Przekazanie, ktora osoba ma zostac edytowana do buttona potwierdzajacego i wykonujacego UPDATE
        # Pobranie tych danych z aktualnego ComboBoxa
        wybrany_pacjent = self.userToEditComboBox.currentText()
        try:
            wybrany_pacjent = wybrany_pacjent.split()
            wybrane_imie = wybrany_pacjent[0]
            wybrane_nazwisko = wybrany_pacjent[1]
        except:
            pass
        
        query = ("UPDATE personel SET imie=\'{imie2}\', nazwisko=\'{nazwisko2}\', plec=\'{plec2}\', data_urodzenia=\'{data_urodzenia2}\', PESEL=\'{PESEL2}\',\
                 data_zatrudnienia=\'{data_zatrudnienia2}\', telefon=\'{telefon2}\', email=\'{email2}\', kod_pocztowy=\'{kod_pocztowy2}\', miejscowosc=\'{miejscowosc2}\', ulica=\'{ulica2}\' WHERE imie LIKE\
                     \'{jakie_imie}\' AND nazwisko LIKE '\{jakie_nazwisko}\'".format(imie2=noweImie,nazwisko2=noweNazwisko,plec2=nowaPlec,\
                         data_urodzenia2=nowaData_urodzenia,PESEL2=nowyPESEL,data_zatrudnienia2=nowaData_zatrudnienia,telefon2=nowyTelefon,email2=nowyEmail,kod_pocztowy2=nowyKod_pocztowy,\
                             miejscowosc2=nowaMiejscowosc,ulica2=nowaUlica,jakie_imie=wybrane_imie,jakie_nazwisko=wybrane_nazwisko))
        
        # taxi = (imie, nazwisko, plec, data_urodzenia, PESEL ,telefon, email, kod_pocztowy, miejscowosc, ulica) # zamiast jedynki mozna wrzucic zmienna pobraną z pola EditText (trzeba takie dodać) gdzie uzytkownik wpisze numer czujnika z palca LUB jego ID
        try:
            cursor.execute(query) #Execute the Query
            cnx.commit()
            print("Zmieniono dane pracownika.")
            # Czyszczenie wprowadzonego tekstu
            self.nameLineEdit.setText("")
            self.surnameLineEdit.setText("")
            # self.sexLineEdit.setText("")
            self.sexComboBox.clear()
            self.sexComboBox.addItem("Mężczyzna")
            self.sexComboBox.addItem("Kobieta")
            self.birthDateLineEdit.setText("")
            self.peselLineEdit.setText("")
            self.hireDateLineEdit.setText("")
            self.phoneLineEdit.setText("")
            self.emailLineEdit.setText("")
            self.cityCodeLineEdit.setText("")
            self.cityLineEdit.setText("")
            self.streetLineEdit.setText("")
            
            notification_win.label.setText("Zmieniono dane pracownika.")
            notification_win.show()
            # TODO # zarejestrowac ta akcje w logach zdarzen
            ###################### #log #rejestr #zdarzenie ########################################################################################
            
            cursor.execute("SELECT ID_pracownika FROM personel WHERE login LIKE \"{jaki_login}\"".format(jaki_login=window.current_user))
            ID_pracownika = cursor.fetchall()[0][0]
            # print("Wyswietlanie ID pracownika na podstawie loginu...")
            # print(ID_pracownika)
            
            query = ("INSERT INTO rejestr_zdarzen (ID_pracownika,rodzaj_zdarzenia,opis_zdarzenia) VALUES (%s, %s, %s)")
            taxi = (ID_pracownika, "Zmieniono dane pracownika {jakie_imie} {jakie_nazwisko}".format(jakie_imie=wybrane_imie,jakie_nazwisko=wybrane_nazwisko), "")
            cursor.execute(query, taxi)
            cnx.commit()
            window.eventList.insertItem(0, "Zmieniono dane pracownika {jakie_imie} {jakie_nazwisko}, ".format(jakie_imie=wybrane_imie,jakie_nazwisko=wybrane_nazwisko)+str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            
            ########################################################################################################################################

        except:
            notification_win.label.setText("Niepoprawne dane. Zwróć uwagę, czy data urodzenia, data zatrudnienia oraz email mają poprawny format.")
            notification_win.show()
            cnx.rollback()
        

    def pushButtonDeleteUserClicked(self):
        
        worker = Worker()
        self.threadpool.start(worker) 
        
        result = None
        while result is None:
            try:
                # auth = input("Podaj haslo do bazy:\n")
                cnx = mysql.connector.connect(user = 'user', password = 'userpass',
                                                                          host = 'localhost',
                                                                          database = 'main_db')
                result = cnx
            except:
                pass
        cursor = cnx.cursor(buffered=True)
        #Writing Query to insert data
        # Przekazanie, ktora osoba ma zostac edytowana do buttona potwierdzajacego i wykonujacego UPDATE
        # Pobranie tych danych z aktualnego ComboBoxa
        
        ### Czekanie na potwierdzenie ...
        # TODO pytanie o potwierdzenie skasowania pacjenta
        # w zamysle po potwierdzeniu usuniecia w oknie delete_confirm_window powinno sie zamknac to okno i kontynuowac operacje ponizej czyli usuniecie pacjenta
        confirmed = 1
        # delete_confirm_window.show()
        print("Polaczono z baza danych...")
        qm = QMessageBox
        ret = qm.question(self,'', "Czy na pewno chcesz usunąć tego pracownika?", qm.Yes | qm.No)
        
        if ret == qm.Yes:
            try:
                wybrany_pracownik = self.userToEditComboBox.currentText()
                
                wybrany_pracownik = wybrany_pracownik.split()
                wybrane_imie = wybrany_pracownik[0]
                wybrane_nazwisko = wybrany_pracownik[1]
                
                
                query = ("DELETE FROM personel WHERE imie LIKE \'{jakie_imie}\' AND nazwisko LIKE '\{jakie_nazwisko}\'".\
                         format(jakie_imie=wybrane_imie,jakie_nazwisko=wybrane_nazwisko))
                
                # taxi = (imie, nazwisko, plec, data_urodzenia, PESEL ,telefon, email, kod_pocztowy, miejscowosc, ulica) # zamiast jedynki mozna wrzucic zmienna pobraną z pola EditText (trzeba takie dodać) gdzie uzytkownik wpisze numer czujnika z palca LUB jego ID
    
            
                cursor.execute(query) #Execute the Query
                cnx.commit()
                print("Usunieto pracownika.")
                # Czyszczenie wprowadzonego tekstu
                self.nameLineEdit.setText("")
                self.surnameLineEdit.setText("")
                # self.sexLineEdit.setText("")
                self.sexComboBox.clear()
                self.sexComboBox.addItem("Mężczyzna")
                self.sexComboBox.addItem("Kobieta")
                self.birthDateLineEdit.setText("")
                self.peselLineEdit.setText("")
                self.hireDateLineEdit.setText("")
                self.phoneLineEdit.setText("")
                self.emailLineEdit.setText("")
                self.cityCodeLineEdit.setText("")
                self.cityLineEdit.setText("")
                self.streetLineEdit.setText("")
                
                notification_win.label.setText("Usunieto pracownika {jakie_imie} {jakie_nazwisko}, ".format(jakie_imie=wybrane_imie,jakie_nazwisko=wybrane_nazwisko))
                notification_win.show()
                # TODO # zarejestrowac ta akcje w logach zdarzen
                ###################### #log #rejestr #zdarzenie ########################################################################################
            
                cursor.execute("SELECT ID_pracownika FROM personel WHERE login LIKE \"{jaki_login}\"".format(jaki_login=window.current_user))
                ID_pracownika = cursor.fetchall()[0][0]
                # print("Wyswietlanie ID pracownika na podstawie loginu...")
                # print(ID_pracownika)
                
                query = ("INSERT INTO rejestr_zdarzen (ID_pracownika,rodzaj_zdarzenia,opis_zdarzenia) VALUES (%s, %s, %s)")
                taxi = (ID_pracownika, "Usunieto pracownika {jakie_imie} {jakie_nazwisko}".format(jakie_imie=wybrane_imie,jakie_nazwisko=wybrane_nazwisko), "")
                cursor.execute(query, taxi)
                cnx.commit()
                window.eventList.insertItem(0, "Usunieto pracownika {jakie_imie} {jakie_nazwisko}, ".format(jakie_imie=wybrane_imie,jakie_nazwisko=wybrane_nazwisko)+str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
                
                ########################################################################################################################################

            except:
                notification_win.label.setText("Wystapil problem podczas usuwania pracownika. Sprawdz czy pracownik zostal wybrany.")
                notification_win.show()
                cnx.rollback()
            
        else:

            print("")

class auth(QMainWindow): #   OKNO LOGOWANIA DO APLIKACJI   ######   PO POMYSLNEJ AUTORYZACJI POKAZUJE SIE GLOWNE OKNO PROGRAMU
    def __init__(self):
        QMainWindow.__init__(self)
        loadUi('auth_gui.ui', self)
        self.loginButton.clicked.connect(self.loginButtonClicked)
        self.abortButton.clicked.connect(self.abortButtonClicked)
        self.passwordLineEdit.setEchoMode(QtWidgets.QLineEdit.Password)
        ################################################################## DO TESTOW ##### POZNIEJ SKASOWAC TE LINIE # TODO
        self.loginLineEdit.setText("admin")
        self.passwordLineEdit.setText("admin")
        
        self.threadpool = QThreadPool()
        
    def loginButtonClicked(self):
        
        worker = Worker()
        self.threadpool.start(worker) 
        
        login = self.loginLineEdit.text()
        password = self.passwordLineEdit.text()  
        ################################################# LOGOWANIE DO APLIKACJI - login i hasło z bazy danych, tabela personel
        result0 = None
        while result0 is None:   # wykonuje sie bez konca, jezeli nie uda sie polaczyc, potrzebne do logowania, ale infinite loop
            try:
                 # auth = input("Podaj haslo do bazy:\n") # przeniesc to do "maina", wykonanie przed poczatkiem programu
                cnx = mysql.connector.connect(user = 'user', password = 'userpass', host = 'localhost', database = 'main_db')
                result0 = cnx
                cursor = cnx.cursor()
                print("...Connection established...")
            except:
                notification_win.label.setText("Blad polaczenia. Sprawdz czy serwer bazy danych jest uruchomiony.")
                notification_win.show()
                pass
        try:
            cursor.execute("SELECT zaszyfrowane_haslo FROM personel WHERE login LIKE \"{jaki_login}\"".format(jaki_login=login)) #Execute the Query
            myresult = cursor.fetchall()    # przeczytany hasz wlasciwego hasla # zakomentowac oba wiersze
            myresult = myresult[0][0]
            # print(myresult) # kontrolnie, pokazanie HASZU hasla z bazy
            # print(encrypt_string(password))
            
            if myresult==encrypt_string(password):
                window.show()
                auth_win.hide()
                print("Logowanie pomyslne.")
                window.current_user = login
                
                ###################### #log #rejestr #zdarzenie ########################################################################################

                cursor.execute("SELECT ID_pracownika FROM personel WHERE login LIKE \"{jaki_login}\"".format(jaki_login=window.current_user))
                ID_pracownika = cursor.fetchall()[0][0]
                # print("Wyswietlanie ID pracownika na podstawie loginu...")
                # print(ID_pracownika)
                
                query = ("INSERT INTO rejestr_zdarzen (ID_pracownika,rodzaj_zdarzenia,opis_zdarzenia) VALUES (%s, %s, %s)")
                taxi = (ID_pracownika, "pomyslne logowanie", "")
                cursor.execute(query, taxi)
                cnx.commit()
                window.eventList.insertItem(0, "pomyslne logowanie, "+str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
                
                ########################################################################################################################################
        except:
            print("Login attempt failed.")
            notification_win.label.setText("Niepoprawny login lub hasło.")
            notification_win.show()
            
            ###################### #log #rejestr #zdarzenie ########################################################################################

            query = ("INSERT INTO rejestr_zdarzen (rodzaj_zdarzenia,opis_zdarzenia) VALUES (%s, %s)")
            taxi = ("nieudana proba logowania", "")
            cursor.execute(query, taxi)
            cnx.commit()
            window.eventList.insertItem(0, "nieudana proba logowania, "+str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            
            ########################################################################################################################################

    def abortButtonClicked(self):
        
        worker = Worker()
        self.threadpool.start(worker)
        
        auth_win.close()
        
            
class notification(QMainWindow):    #

    def __init__(self):
        QMainWindow.__init__(self)
        loadUi('notification.ui', self)
        self.setWindowTitle("Informacja")
        self.pushButtonOK.clicked.connect(self.pushButtonOKClicked)
        
        self.threadpool = QThreadPool()
        
    def pushButtonOKClicked(self):
        
        worker = Worker()
        self.threadpool.start(worker)
        
        self.hide()
        
class python_to_arduino_msg(QMainWindow):    #
    
    def __init__(self):
        QMainWindow.__init__(self)
        loadUi('komunikat_zwrotny.ui', self)
        self.setWindowTitle("Informacja zwrotna do układu pomiarowego")
        
        self.pushButtonFilterEditPatient.clicked.connect(self.pushButtonFilterEditPatientClicked)
        self.pushButtonSend.clicked.connect(self.pushButtonSendClicked)
        
        self.msgComboBox.clear()
        self.msgComboBox.addItem("1 - Zmień tryb transmisji na ciągły")
        self.msgComboBox.addItem("2 - Zmień tryb transmisji na zdarzeniowy")
        self.msgComboBox.addItem("3 - Przerwij wysyłanie pomiarów")
        self.msgComboBox.addItem("4 - Wznów wysyłanie pomiarów")
        
        self.threadpool = QThreadPool()
        

    def pushButtonFilterEditPatientClicked(self):
        # Filtrowanie pacjentow
        self.patientToEditComboBox.clear()
        
        worker = Worker()
        self.threadpool.start(worker) 
        
        print("Wybor pacjentow... ")

        seekToEdit = self.filterToEditLineEdit.text()
        print(seekToEdit)
        try:
            cursor.execute("SELECT pac.imie, pac.nazwisko, prz.ID_czujnika FROM pacjenci pac JOIN przydzial_czujnikow prz ON pac.ID_pacjenta=prz.ID_pacjenta WHERE pac.imie LIKE BINARY \'%{seek}%\' OR pac.nazwisko LIKE BINARY \'%{seek}%\' OR pac.ID_pacjenta LIKE BINARY \'%{seek}%\'".format(seek=seekToEdit))
            # usunac przedrostek BINARY, jezeli sie chce case_insensitive
            # cursor.execute("SELECT imie, nazwisko FROM pacjenci")
            print("...SELECT query succeeded...")
            
            # OK.... ale teraz jak w matplotlibie okreslic DATĘ jako os X, i x_axis jako os Y (x_axis to wartosci, os pionowa)
            
            myresult = cursor.fetchall()
            # print("The length of \'myresult\' is: ", len(myresult)) # pokazuje ile rekordow ma zostac wykorzystanych na wykresie
            pacjenci = []
            for x in myresult:
                        pacjenci.append(str(x[0])+" "+str(x[1])+" czujnik: "+str(x[2]))
            self.patientToEditComboBox.addItems(pacjenci)
            ###################################################################
        except:
            print("SELECT query failed")

    
    def pushButtonSendClicked(self):
        
        print("Wysylanie wiadomosci... ")
        
        worker = Worker()
        self.threadpool.start(worker) 

        # seekHist = self.filterToEditLineEdit.text()
        # print(seekHist)
        wybrany_komunikat = self.msgComboBox.currentText()
        try:
            wybrany_komunikat = wybrany_komunikat.split()
            wybrane_id_komunikatu = wybrany_komunikat[0]
        except Exception as e: print(e)
            # pass
        print("Wybrane ID komunikatu: "+wybrane_id_komunikatu)
        
        ser.close()
        board = Arduino(port)
        ####################################### zakodowanie rodzaju komunikatu na pinach arduino
        if wybrane_id_komunikatu==1:
            board.digital[6].write(1) # najmlodszy bit z 4 przydzielonych do zakodowania wiadomosci
            
        elif wybrane_id_komunikatu==2:
            board.digital[5].write(1)
            
        elif wybrane_id_komunikatu==3:
            board.digital[6].write(1)
            board.digital[5].write(1)
            
        elif wybrane_id_komunikatu==3:
            board.digital[4].write(1)
        ######################################## zakodowanie ID czujnika
        wybrany_pacjent = self.patientToEditComboBox.currentText()
        try:
            wybrany_pacjent = wybrany_pacjent.split()
            wybrane_id_czujnika_pacjenta = wybrany_pacjent[3]
        except Exception as e: print(e)
            # pass
        if wybrane_id_czujnika_pacjenta==1:
            board.digital[13].write(1)
        elif wybrane_id_czujnika_pacjenta==2:
            board.digital[12].write(1)
        elif wybrane_id_czujnika_pacjenta==3:
            board.digital[13].write(1)
            board.digital[12].write(1)
        elif wybrane_id_czujnika_pacjenta==4:
            board.digital[11].write(1)
        elif wybrane_id_czujnika_pacjenta==5:
            board.digital[11].write(1)
            board.digital[13].write(1)
        elif wybrane_id_czujnika_pacjenta==6:
            board.digital[11].write(1)
            board.digital[12].write(1)
        elif wybrane_id_czujnika_pacjenta==7:
            board.digital[11].write(1)
            board.digital[12].write(1)
            board.digital[13].write(1)
        elif wybrane_id_czujnika_pacjenta==8:
            board.digital[10].write(1)
        elif wybrane_id_czujnika_pacjenta==9:
            board.digital[10].write(1)
            board.digital[13].write(1)
        elif wybrane_id_czujnika_pacjenta==10:
            board.digital[10].write(1)
            board.digital[12].write(1)
        
            
        
        board.exit()
        ser.open()
        
        
if __name__ == '__main__':
        
    app=QApplication(sys.argv)
    app.setStyle('Breeze')
    
    window = main_window()
    # window.show() # ten wiersz jest ukryty, bo okno ma się pokazać dopiero po zalogowaniu, mozna odkomentowac do obejscia hasla
    new_patient_window = new_patient()    # stworzenie okna dodawania nowego pacjenta
    edit_patient_window = edit_patient()
    
    new_user_window = new_user()    
    edit_user_window = edit_user()
    
    new_sensor_window = new_sensor()
    edit_sensor_window = edit_sensor()
    # delete_confirm_window = delete_patient_confirm() nie jest uzywane, tymczasowo(lub na stałe zastapione poprzez QMessageBox)
    auth_win = auth()
    auth_win.show()
    
    notification_win = notification()
    
    assign_sensor_window = assign_sensor()
    
    python_to_arduino_msg_win = python_to_arduino_msg()
        
    
    # new_user_window = new_user()
    sys.exit(app.exec_())