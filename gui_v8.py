import sys
from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSlot, QTime, QDate
from PyQt5.QtWidgets import QApplication, QDialog, QMainWindow, QWidget, QSlider, QTimeEdit, QDateEdit
from PyQt5.QtWidgets import QMessageBox
from PyQt5.uic import loadUi
from time import sleep
import csv
import mysql.connector
import datetime
import matplotlib.pyplot as plt
import numpy as np
import time
import winsound
import ctypes
import queue
import hashlib
import pandas as pd
import matplotlib.dates as mdates
from datetime import datetime
from PyQt5.QtWidgets import QGridLayout, QSizePolicy

def encrypt_string(hash_string):
    sha_signature = \
        hashlib.sha256(hash_string.encode()).hexdigest()
    return sha_signature

#############################################################

class main_window(QMainWindow): # MAIN WINDOW
    def __init__(self):
            QMainWindow.__init__(self)
            loadUi('gui_v4.ui', self)
            self.setWindowTitle("System monitorowania ruchu pacjentow")
            self.pushButtonBegin.clicked.connect(self.pushButtonBeginClicked)    # zmienic hello na cos innego
            self.pushButtonInsert.clicked.connect(self.pushButtonInsertClicked)
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
#############################################################################################################################
    @pyqtSlot()
###################################################### Wczytywanie pacjentow z bazy do Comboboxa Historii
    def assignSensorPushButtonClicked(self):
        assign_sensor_window.show()

    def editSensorButtonClicked(self):
        edit_sensor_window.show()

    def newSensorButtonClicked(self):
        new_sensor_window.show()

    def editPatientButtonClicked(self):
        edit_patient_window.show()

    def editUserButtonClicked(self):
        edit_user_window.show()

    def pushButtonFilterHistoryPatientClicked(self):
        self.patientHistoryComboBox.clear()
        
        print("Wybor pacjentow... ")
                #Connect with database
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
        cursor = cnx.cursor()
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

        cnx.close()
    
    def pushButtonFilterLivePatientClicked(self):
        self.patientLiveComboBox.clear()
        
        print("Wybor pacjentow... ")
                #Connect with database
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
        cursor = cnx.cursor()
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
    
        cnx.close()
        
    def showHistoryButtonClicked(self):
        print("showHistoryButtonClicked")
        
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
        #Connect with database
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
        cursor = cnx.cursor()
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
            ctypes.windll.user32.MessageBoxW(0, "Niepowodzenie wyswietlania wykresu. Nie wybrano pacjenta lub nie udało się połączyć z bazą danych.", "Informacja", 0)

        cnx.close()
############################################################## Rysowanie wykresu z historii ^^^^^^^^^^^^^^ @ UP
        
    def v_change(self):
        value = str(self.rangeSlider.value())
        self.sliderValueLineEdit.setText(value)
        
    def pushButtonBeginClicked(self):    # funkcja testowa, usunac lub wymienic na inna
        print("Drukowanie wykresu...")
        #Connect with database
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
        cursor = cnx.cursor()
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
            ctypes.windll.user32.MessageBoxW(0, "Niepowodzenie wyswietlania wykresu. Nie wybrano pacjenta lub nie udało się połączyć z bazą danych.", "Informacja", 0)

        cnx.close()
        
#######################################################################################################################
    def pushButtonInsertClicked(self):
            #ctypes.windll.user32.MessageBoxW(0, "Trwa wczytywanie danych prosze czekac", "Informacja", 1)
        print("Writing .txt to SQL...")
        #Load text file into list with CSV module
        with open(r"C:\Users\matsz\Documents\original_kopia\Refactored_Py_DS_ML_Bootcamp-master\03-Python-for-Data-Analysis-Pandas/kuba - oddech 45 sekund, bezdech 30 sekund.TXT", "rt") as f:
            reader = csv.reader(f, delimiter = ' ', skipinitialspace=True)
            lineData = list()
            cols = next(reader)
        
            for line in reader:
                if line != []:
                    lineData.append(line)
        
        #Connect with database
        
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
        query = ("INSERT INTO pomiary (ID_czujnika, modul, x_axis, y_axis, z_axis) VALUES (%s, %s, %s, %s, %s)")
        
        #Change every item in the sub list into the correct data type and store it in a directory
        serie_bezdechu = pd.DataFrame()
        for i in range(len(lineData)):
            try:
                taxi = (1, lineData[i][0], lineData[i][1], lineData[i][2], lineData[i][3]) # zamiast jedynki mozna wrzucic zmienna pobraną z pola EditText (trzeba takie dodać) gdzie uzytkownik wpisze numer czujnika z palca LUB jego ID
                cursor.execute(query, taxi) #Execute the Query
                sleep(0.03)
                # if lineData[i][0]>2.5:
                    # ctypes.windll.user32.MessageBoxW(0, "PACJENT UPADL, WYMAGANA INTERWENCJA !", "Informacja", 1)
                if (i%1000)==0 and (i>0):
                    print("1000" + " rows inserted, please wait...")
        
            except:
                print("Błędny pomiar")
                print(taxi)
        print("Import finished.")
        #Commit the query
        cnx.commit()
        
        cnx.close()
######################################################################################## funkcje otwierajace nowe okna po kliknieciu przycisku w glownym GUI
    def newPatientButtonClicked(self):
        print("Adding new patient...")
        new_patient_window.show()
        
    def newUserButtonClicked(self):
        print("Adding new user...")
        new_user_window.show()

class new_patient(QMainWindow):    #

    
    def __init__(self):
        QMainWindow.__init__(self)
        loadUi('add_patient_gui.ui', self)
        self.setWindowTitle("Dodawanie nowego pacjenta")
        self.pushButtonAdd.clicked.connect(self.pushButtonAddClicked)
        self.pushButtonAbort.clicked.connect(self.pushButtonAbortClicked)
        self.birthDateLineEdit.setPlaceholderText("RRRR-MM-DD")
        self.emailLineEdit.setPlaceholderText("email@address.com")
    @pyqtSlot()
    def pushButtonAbortClicked(self):
        new_patient_window.hide()
    def pushButtonAddClicked(self):
        
        imie = self.nameLineEdit.text()
        nazwisko = self.surnameLineEdit.text()
        plec = self.sexLineEdit.text()
        data_urodzenia = self.birthDateLineEdit.text()
        PESEL = self.peselLineEdit.text()        
        telefon = self.phoneLineEdit.text()
        email = self.emailLineEdit.text()
        kod_pocztowy = self.cityCodeLineEdit.text()
        miejscowosc = self.cityLineEdit.text()
        ulica = self.streetLineEdit.text()
        
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
        query = ("INSERT INTO pacjenci (imie, nazwisko, plec, data_urodzenia, PESEL, telefon, email, kod_pocztowy, miejscowosc, ulica) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
        
        taxi = (imie, nazwisko, plec, data_urodzenia, PESEL ,telefon, email, kod_pocztowy, miejscowosc, ulica) # zamiast jedynki mozna wrzucic zmienna pobraną z pola EditText (trzeba takie dodać) gdzie uzytkownik wpisze numer czujnika z palca LUB jego ID
        try:
            cursor.execute(query, taxi) #Execute the Query
            cnx.commit()
            print("Dodano nowego pacjenta.")
            # Czyszczenie wprowadzonego tekstu
            imie = self.nameLineEdit.setText("")
            nazwisko = self.surnameLineEdit.setText("")
            plec = self.sexLineEdit.setText("")
            data_urodzenia = self.birthDateLineEdit.setText("")
            PESEL = self.peselLineEdit.setText("")        
            telefon = self.phoneLineEdit.setText("")
            email = self.emailLineEdit.setText("")
            kod_pocztowy = self.cityCodeLineEdit.setText("")
            miejscowosc = self.cityLineEdit.setText("")
            ulica = self.streetLineEdit.setText("")
            ctypes.windll.user32.MessageBoxW(0, "Dodano nowego pacjenta.", "Informacja", 0)
            # TODO # zarejestrowac ta akcje w logach zdarzen
        except:
            ctypes.windll.user32.MessageBoxW(0, "Niepoprawne dane. Zwróć uwagę, czy data urodzenia oraz email mają poprawny format.", "Informacja", 0)
            cnx.rollback()
        cnx.close()

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
    
    def pushButtonFilterEditPatientClicked(self):
        # Filtrowanie pacjentow
        self.patientToEditComboBox.clear()
        
        print("Wybor pacjentow... ")
                #Connect with database
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
        cursor = cnx.cursor()
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

        cnx.close()
    
    def pushButtonLoadToEditPatientClicked(self):
        
        print("Ladowanie danych pacjenta... ")
        #Connect with database
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
        cursor = cnx.cursor()
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
            cursor.execute("SELECT imie, nazwisko, plec, data_urodzenia, PESEL, telefon, email, kod_pocztowy, miejscowosc, ulica FROM pacjenci WHERE imie LIKE \'%{imie}%\' AND nazwisko LIKE \'%{nazwisko}%\'".format(imie=wybrane_imie, nazwisko=wybrane_nazwisko))
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
                self.sexLineEdit.setText(str(x[2]))
                self.birthDateLineEdit.setText(str(x[3]))
                self.peselLineEdit.setText(str(x[4]))     
                self.phoneLineEdit.setText(str(x[5]))
                self.emailLineEdit.setText(str(x[6]))
                self.cityCodeLineEdit.setText(str(x[7]))
                self.cityLineEdit.setText(str(x[8]))
                self.streetLineEdit.setText(str(x[9]))
            ###################################################################
        except:
            print("SELECT query failed")

        cnx.close()
    
    @pyqtSlot()
    def pushButtonAbortClicked(self):
        edit_patient_window.hide()
    def pushButtonSaveChangesClicked(self):
        
        noweImie = self.nameLineEdit.text()
        noweNazwisko = self.surnameLineEdit.text()
        nowaPlec = self.sexLineEdit.text()
        nowaData_urodzenia = self.birthDateLineEdit.text()
        nowyPESEL = self.peselLineEdit.text()        
        nowyTelefon = self.phoneLineEdit.text()
        nowyEmail = self.emailLineEdit.text()
        nowyKod_pocztowy = self.cityCodeLineEdit.text()
        nowaMiejscowosc = self.cityLineEdit.text()
        nowaUlica = self.streetLineEdit.text()
        
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
        wybrany_pacjent = self.patientToEditComboBox.currentText()
        try:
            wybrany_pacjent = wybrany_pacjent.split()
            wybrane_imie = wybrany_pacjent[0]
            wybrane_nazwisko = wybrany_pacjent[1]
        except:
            pass
        
        query = ("UPDATE pacjenci SET imie=\'{imie2}\', nazwisko=\'{nazwisko2}\', plec=\'{plec2}\', data_urodzenia=\'{data_urodzenia2}\', PESEL=\'{PESEL2}\',\
                 telefon=\'{telefon2}\', email=\'{email2}\', kod_pocztowy=\'{kod_pocztowy2}\', miejscowosc=\'{miejscowosc2}\', ulica=\'{ulica2}\' WHERE imie LIKE\
                     \'{jakie_imie}\' AND nazwisko LIKE '\{jakie_nazwisko}\'".format(imie2=noweImie,nazwisko2=noweNazwisko,plec2=nowaPlec,\
                         data_urodzenia2=nowaData_urodzenia,PESEL2=nowyPESEL,telefon2=nowyTelefon,email2=nowyEmail,kod_pocztowy2=nowyKod_pocztowy,\
                             miejscowosc2=nowaMiejscowosc,ulica2=nowaUlica,jakie_imie=wybrane_imie,jakie_nazwisko=wybrane_nazwisko))
        
        # taxi = (imie, nazwisko, plec, data_urodzenia, PESEL ,telefon, email, kod_pocztowy, miejscowosc, ulica) # zamiast jedynki mozna wrzucic zmienna pobraną z pola EditText (trzeba takie dodać) gdzie uzytkownik wpisze numer czujnika z palca LUB jego ID
        try:
            cursor.execute(query) #Execute the Query
            cnx.commit()
            print("Dodano nowego pacjenta.")
            # Czyszczenie wprowadzonego tekstu
            self.nameLineEdit.setText("")
            self.surnameLineEdit.setText("")
            self.sexLineEdit.setText("")
            self.birthDateLineEdit.setText("")
            self.peselLineEdit.setText("")        
            self.phoneLineEdit.setText("")
            self.emailLineEdit.setText("")
            self.cityCodeLineEdit.setText("")
            self.cityLineEdit.setText("")
            self.streetLineEdit.setText("")
            ctypes.windll.user32.MessageBoxW(0, "Zmieniono dane pacjenta.", "Informacja", 0)
            # TODO # zarejestrowac ta akcje w logach zdarzen
        except:
            ctypes.windll.user32.MessageBoxW(0, "Niepoprawne dane. Zwróć uwagę, czy data urodzenia oraz email mają poprawny format.", "Informacja", 0)
            cnx.rollback()
        cnx.close()

    def pushButtonDeletePatientClicked(self):
        
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
                print("Usunieto pacjenta.")
                # Czyszczenie wprowadzonego tekstu
                self.nameLineEdit.setText("")
                self.surnameLineEdit.setText("")
                self.sexLineEdit.setText("")
                self.birthDateLineEdit.setText("")
                self.peselLineEdit.setText("")        
                self.phoneLineEdit.setText("")
                self.emailLineEdit.setText("")
                self.cityCodeLineEdit.setText("")
                self.cityLineEdit.setText("")
                self.streetLineEdit.setText("")
                ctypes.windll.user32.MessageBoxW(0, "Usunieto pacjenta.", "Informacja", 0)
                # TODO # zarejestrowac ta akcje w logach zdarzen
            except:
                ctypes.windll.user32.MessageBoxW(0, "Wystapil problem podczas usuwania pacjenta. Sprawdz czy pacjent zostal wybrany.", "Informacja", 0)
                cnx.rollback()
            cnx.close()
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
    @pyqtSlot()
    def pushButtonAbortClicked(self):
        new_patient_window.hide()
    def pushButtonAddDefaultIDClicked(self):
        
        mac_address = self.macLineEdit.text()
        
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
        query = ("INSERT INTO czujniki (MAC_czujnika) VALUES (\'{jaki_mac}\')".format(jaki_mac=mac_address))
        
        # taxi = (mac_address) # zamiast jedynki mozna wrzucic zmienna pobraną z pola EditText (trzeba takie dodać) gdzie uzytkownik wpisze numer czujnika z palca LUB jego ID
        try:
            cursor.execute(query) #Execute the Query
            cnx.commit()
            print("Dodano nowy czujnik.")
            # Czyszczenie wprowadzonego tekstu
            self.macLineEdit.setText("")
            self.sensorIDLineEdit.setText("")

            ctypes.windll.user32.MessageBoxW(0, "Dodano nowy czujnik.", "Informacja", 0)
            # TODO # zarejestrowac ta akcje w logach zdarzen
        except:
            ctypes.windll.user32.MessageBoxW(0, "Niepoprawne dane. Zwróć uwagę, czy data urodzenia oraz email mają poprawny format.", "Informacja", 0)
            # TODO zmienic komunikat, optymalnie wymusic znaki 0-9, A-F
            cnx.rollback()
        cnx.close()
    def pushButtonAddClicked(self):
        
        mac_address = self.macLineEdit.text()
        sensor_id = self.sensorIDLineEdit.text()
        
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
        query = ("INSERT INTO czujniki (ID_czujnika, MAC_czujnika) VALUES (\'{jakie_id}\', \'{jaki_mac}\')".format(jakie_id = sensor_id,jaki_mac=mac_address))
        
        # taxi = (mac_address) # zamiast jedynki mozna wrzucic zmienna pobraną z pola EditText (trzeba takie dodać) gdzie uzytkownik wpisze numer czujnika z palca LUB jego ID
        try:
            cursor.execute(query) #Execute the Query
            cnx.commit()
            print("Dodano nowy czujnik.")
            # Czyszczenie wprowadzonego tekstu
            self.macLineEdit.setText("")
            self.sensorIDLineEdit.setText("")

            ctypes.windll.user32.MessageBoxW(0, "Dodano nowy czujnik.", "Informacja", 0)
            # TODO # zarejestrowac ta akcje w logach zdarzen
        except:
            ctypes.windll.user32.MessageBoxW(0, "Niepoprawne dane. Zwróć uwagę, czy data urodzenia oraz email mają poprawny format.", "Informacja", 0)
            # TODO zmienic komunikat, optymalnie wymusic znaki 0-9, A-F
            cnx.rollback()
        cnx.close()

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
        
    
    def pushButtonFilterClicked(self):
        # Filtrowanie pacjentow
        self.chooseToEditComboBox.clear()
        
        print("Wybor czujnika... ")
                #Connect with database
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
        cursor = cnx.cursor()
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

        cnx.close()
    
    def pushButtonLoadClicked(self):
        
        print("Ladowanie danych czujnika... ")
        #Connect with database
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
        cursor = cnx.cursor()
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

        cnx.close()
    
    @pyqtSlot()
    def pushButtonAbortClicked(self):
        edit_patient_window.hide()
    def pushButtonSaveChangesClicked(self):
        
        noweID = self.idLineEdit.text()
        nowyMAC = self.macLineEdit.text()

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

            ctypes.windll.user32.MessageBoxW(0, "Zmieniono dane czujnika.", "Informacja", 0)
            # TODO # zarejestrowac ta akcje w logach zdarzen
        except:
            ctypes.windll.user32.MessageBoxW(0, "Niepoprawne dane. Zwróć uwagę, czy data urodzenia oraz email mają poprawny format.", "Informacja", 0)
            cnx.rollback()
        cnx.close()

    def pushButtonDeleteClicked(self):
        
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
          
        qm = QMessageBox
        ret = qm.question(self,'', "Czy na pewno chcesz usunąć ten czujnik?", qm.Yes | qm.No)
        
        if ret == qm.Yes:
            try:
                wybrany_czujnik = self.chooseToEditComboBox.currentText()
                
                wybrany_czujnik = wybrany_czujnik.split()
                wybrane_id = wybrany_czujnik[0]
                
                
                query = ("DELETE FROM czujniki WHERE ID_czujnika={jakie_id}".\
                         format(jakie_id=int(wybrane_id)))
                
                # taxi = (imie, nazwisko, plec, data_urodzenia, PESEL ,telefon, email, kod_pocztowy, miejscowosc, ulica) # zamiast jedynki mozna wrzucic zmienna pobraną z pola EditText (trzeba takie dodać) gdzie uzytkownik wpisze numer czujnika z palca LUB jego ID
    
            
                cursor.execute(query) #Execute the Query
                cnx.commit()
                print("Usunieto czujnik z bazy.")
                # Czyszczenie wprowadzonego tekstu
                self.idLineEdit.setText("")
                self.macLineEdit.setText("")

                ctypes.windll.user32.MessageBoxW(0, "Usunieto czujnik z bazy.", "Informacja", 0)
                # TODO # zarejestrowac ta akcje w logach zdarzen
            except:
                ctypes.windll.user32.MessageBoxW(0, "Wystapil problem podczas usuwania czujnika. Sprawdz czy pacjent zostal wybrany.", "Informacja", 0)
                cnx.rollback()
            cnx.close()
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
        
    def pushButtonFilterClicked(self):
        # Filtrowanie pacjentow
        self.chooseToEditComboBox.clear()
        
        print("Wybor czujnika... ")
                #Connect with database
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
        cursor = cnx.cursor()
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

        cnx.close()
    
    def pushButtonFilterEditPatientClicked(self):
        # Filtrowanie pacjentow
        self.patientToEditComboBox.clear()
        
        print("Wybor pacjentow... ")
                #Connect with database
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
        cursor = cnx.cursor()
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

        cnx.close()
    
    def pushButtonAbortClicked(self):
        edit_patient_window.hide()
    def pushButtonAssignClicked(self):
        
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
        
        wybrany_czujnik = self.chooseToEditComboBox.currentText()
        wybrany_pacjent = self.patientToEditComboBox.currentText()
        try:
            wybrany_czujnik = wybrany_czujnik.split()
            wybrane_id = wybrany_czujnik[0]
            
            wybrany_pacjent = wybrany_pacjent.split()
            wybrane_id_pacjenta = wybrany_pacjent[0]
            wybrane_imie = wybrany_pacjent[1]
            wybrane_nazwisko = wybrany_pacjent[2]
            
            print("Udalo sie odczytac dane z ComboBoxow")
        except:
            pass
        
        query = ("INSERT INTO przydzial_czujnikow (ID_pacjenta,ID_czujnika,status)\
                 VALUES ({ID_pacjenta_2},{ID_czujnika_2},'default')"\
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

            ctypes.windll.user32.MessageBoxW(0, "Dodano nowe przypisanie.", "Informacja", 0)
            # TODO # zarejestrowac ta akcje w logach zdarzen
        except:
            ctypes.windll.user32.MessageBoxW(0, "Nie udalo się dodać przypisania. Wybrany czujnik może już być przypisany do innego pacjenta. Usuń przypisanie i spróbuj ponownie.", "Informacja", 0)
            cnx.rollback()
        cnx.close()

    def pushButtonDeleteClicked(self):
        
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
          
        qm = QMessageBox
        ret = qm.question(self,'', "Czy na pewno chcesz usunąć to przypisanie?", qm.Yes | qm.No)
        
        if ret == qm.Yes:
            try:
                wybrany_czujnik = self.chooseToEditComboBox.currentText()
                
                wybrany_czujnik = wybrany_czujnik.split()
                wybrane_id = wybrany_czujnik[0]
                
                
                query = ("DELETE FROM przydzial_czujnikow WHERE ID_czujnika={jakie_id}".\
                          format(jakie_id=int(wybrane_id)))
                
                # taxi = (imie, nazwisko, plec, data_urodzenia, PESEL ,telefon, email, kod_pocztowy, miejscowosc, ulica) # zamiast jedynki mozna wrzucic zmienna pobraną z pola EditText (trzeba takie dodać) gdzie uzytkownik wpisze numer czujnika z palca LUB jego ID
    
            
                cursor.execute(query) #Execute the Query
                cnx.commit()
                print("Usunieto czujnik z bazy.")
                # Czyszczenie wprowadzonego tekstu
                self.filterToEditLineEdit.setText("")
                self.filterPatientLineEdit.setText("")

                ctypes.windll.user32.MessageBoxW(0, "Usunieto przypisanie z bazy.", "Informacja", 0)
                # TODO # zarejestrowac ta akcje w logach zdarzen
            except:
                ctypes.windll.user32.MessageBoxW(0, "Wystapil problem podczas usuwania przypisania. Sprawdz czy pacjent zostal wybrany.", "Informacja", 0)
                cnx.rollback()
            cnx.close()
        else:

            print("")

# delete_patient_confirm NIE JEST UZYWANY, zamiast tego uzyto QMessageBox, nieoptymalny bo nie ma polskich napisow, tylko Yes, No, ale dziala
class delete_patient_confirm(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        loadUi('delete_patient_confirm.ui', self)
        
        self.pushButtonDelete.clicked.connect(self.pushButtonDeleteClicked)
        self.pushButtonAbort.clicked.connect(self.pushButtonAbortClicked)
    def pushButtonDeleteClicked(self):
        edit_patient.confirmed = 1
    def pushButtonAbortClicked(self):
        delete_confirm_window.hide()
    
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
        # TODO # wymagac od loginu minimum 5 znakow, od hasla optymalnie 8+ znakow i A-Z, a-z, 0-9
    @pyqtSlot()
    def pushButtonAbortClicked(self):
        new_patient_window.hide()
    def pushButtonAddClicked(self):
        
        imie = self.nameLineEdit.text()
        nazwisko = self.surnameLineEdit.text()
        plec = self.sexLineEdit.text()
        data_urodzenia = self.birthDateLineEdit.text()
        PESEL = self.peselLineEdit.text()
        data_zatrudnienia = self.hireDateLineEdit.text()
        login = self.loginLineEdit.text()
        haslo = self.passwordLineEdit.text() # TODO # trzeba dodac zaslanianie hasla i pewnie nie bedzie tak latwo
        zaszyfrowane_haslo = encrypt_string(haslo)
        print(zaszyfrowane_haslo)
        telefon = self.nameLineEdit.text()
        email = self.emailLineEdit.text()
        kod_pocztowy = self.cityCodeLineEdit.text()
        miejscowosc = self.cityLineEdit.text()
        ulica = self.streetLineEdit.text()
        
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
        query = ("INSERT INTO personel (imie, nazwisko, plec, data_urodzenia, PESEL, data_zatrudnienia, login, zaszyfrowane_haslo, telefon, email, kod_pocztowy, miejscowosc, ulica) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
        
        taxi = (imie, nazwisko, plec, data_urodzenia, PESEL , data_zatrudnienia, login, zaszyfrowane_haslo, telefon, email, kod_pocztowy, miejscowosc, ulica) # zamiast jedynki mozna wrzucic zmienna pobraną z pola EditText (trzeba takie dodać) gdzie uzytkownik wpisze numer czujnika z palca LUB jego ID
        try:
            cursor.execute(query, taxi) #Execute the Query
            cnx.commit()
            print("Dodano nowego pracownika.")
            self.nameLineEdit.setText("")
            self.surnameLineEdit.setText("")
            self.sexLineEdit.setText("")
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
            ctypes.windll.user32.MessageBoxW(0, "Dodano nowego pracownika.", "Informacja", 0)
            # TODO # zarejestrowac ta akcje w logach zdarzen
        except:
            print("Niepoprawne dane. Zwróć uwagę, czy data urodzenia oraz email mają poprawny format.")
            cnx.rollback()
        cnx.close()

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
    
    def pushButtonFilterEditUserClicked(self):
        # Filtrowanie pacjentow
        self.userToEditComboBox.clear()
        
        print("Wybor pracownikow... ")
                #Connect with database
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
        cursor = cnx.cursor()
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

        cnx.close()
    
    def pushButtonLoadToEditUserClicked(self):
        
        print("Ladowanie danych pracownika... ")
        #Connect with database
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
        cursor = cnx.cursor()
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
                self.sexLineEdit.setText(str(x[2]))
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

        cnx.close()
    
    @pyqtSlot()
    def pushButtonAbortClicked(self):
        edit_patient_window.hide()
    def pushButtonSaveChangesClicked(self):
        
        noweImie = self.nameLineEdit.text()
        noweNazwisko = self.surnameLineEdit.text()
        nowaPlec = self.sexLineEdit.text()
        nowaData_urodzenia = self.birthDateLineEdit.text()
        nowyPESEL = self.peselLineEdit.text()
        nowaData_zatrudnienia = self.hireDateLineEdit.text()
        nowyTelefon = self.phoneLineEdit.text()
        nowyEmail = self.emailLineEdit.text()
        nowyKod_pocztowy = self.cityCodeLineEdit.text()
        nowaMiejscowosc = self.cityLineEdit.text()
        nowaUlica = self.streetLineEdit.text()
        
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
            self.sexLineEdit.setText("")
            self.birthDateLineEdit.setText("")
            self.peselLineEdit.setText("")
            self.hireDateLineEdit.setText("")
            self.phoneLineEdit.setText("")
            self.emailLineEdit.setText("")
            self.cityCodeLineEdit.setText("")
            self.cityLineEdit.setText("")
            self.streetLineEdit.setText("")
            ctypes.windll.user32.MessageBoxW(0, "Zmieniono dane pracownika.", "Informacja", 0)
            # TODO # zarejestrowac ta akcje w logach zdarzen
        except:
            ctypes.windll.user32.MessageBoxW(0, "Niepoprawne dane. Zwróć uwagę, czy data urodzenia, data zatrudnienia oraz email mają poprawny format.", "Informacja", 0)
            cnx.rollback()
        cnx.close()

    def pushButtonDeleteUserClicked(self):
        
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
                self.sexLineEdit.setText("")
                self.birthDateLineEdit.setText("")
                self.peselLineEdit.setText("")
                self.hireDateLineEdit.setText("")
                self.phoneLineEdit.setText("")
                self.emailLineEdit.setText("")
                self.cityCodeLineEdit.setText("")
                self.cityLineEdit.setText("")
                self.streetLineEdit.setText("")
                ctypes.windll.user32.MessageBoxW(0, "Usunieto pracownika.", "Informacja", 0)
                # TODO # zarejestrowac ta akcje w logach zdarzen
            except:
                ctypes.windll.user32.MessageBoxW(0, "Wystapil problem podczas usuwania pracownika. Sprawdz czy pracownik zostal wybrany.", "Informacja", 0)
                cnx.rollback()
            cnx.close()
        else:

            print("")

class auth(QMainWindow): #   OKNO LOGOWANIA DO APLIKACJI   ######   PO POMYSLNEJ AUTORYZACJI POKAZUJE SIE GLOWNE OKNO PROGRAMU
    def __init__(self):
        QMainWindow.__init__(self)
        loadUi('auth_gui.ui', self)
        self.loginButton.clicked.connect(self.loginButtonClicked)
        self.passwordLineEdit.setEchoMode(QtWidgets.QLineEdit.Password)
        ################################################################## DO TESTOW ##### POZNIEJ SKASOWAC TE LINIE
        self.loginLineEdit.setText("admin")
        self.passwordLineEdit.setText("admin")
    def loginButtonClicked(self):
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
                ctypes.windll.user32.MessageBoxW(0, "Connection failed. Check if Database is running.", "Informacja", 0)
                pass
        try:
            cursor.execute("SELECT zaszyfrowane_haslo FROM personel WHERE login LIKE \"{jaki_login}\"".format(jaki_login=login)) #Execute the Query
            print("Access granted.")
            myresult = cursor.fetchall()    # przeczytany hasz wlasciwego hasla # zakomentowac oba wiersze
            print(myresult) # kontrolnie, pokazanie HASZU hasla z bazy
            print(encrypt_string(password))
            myresult==password
            cnx.close()
            window.show()
            auth_win.hide()
        except:
            print("Login attempt failed.")
            ctypes.windll.user32.MessageBoxW(0, "Niepoprawny login lub hasło.", "Informacja", 0)


if __name__ == '__main__':
        
    app=QApplication(sys.argv)
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
    
    assign_sensor_window = assign_sensor()
    
    
    # new_user_window = new_user()
    sys.exit(app.exec_())