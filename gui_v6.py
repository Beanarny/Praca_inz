import sys
from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSlot, QTime, QDate
from PyQt5.QtWidgets import QApplication, QDialog, QMainWindow, QWidget, QSlider, QTimeEdit, QDateEdit
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


def encrypt_string(hash_string):
    sha_signature = \
        hashlib.sha256(hash_string.encode()).hexdigest()
    return sha_signature

        



################################################# MAIN WINDOW ####################################################################################
class main_window(QMainWindow):
    def __init__(self):
            QMainWindow.__init__(self)
            loadUi('gui_v4.ui', self)
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
#############################################################################################################################
    @pyqtSlot()
###################################################### Odczytywanie czasu z widgetow
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
        
        
###################################################### Odczytywanie czasu z widgetow ^^^^^^^^^^^^^^^
        
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
        print(dateTimeFrom)
        print(dateTimeTo)
        print("SELECT data_i_czas_pomiaru, x_axis FROM pomiary WHERE data_i_czas_pomiaru BETWEEN \'{data_i_czas_od}\' AND \'{data_i_czas_do}\'".format(data_i_czas_od=dateTimeFrom,data_i_czas_do=dateTimeTo))
        try:
            cursor.execute("SELECT data_i_czas_pomiaru, x_axis FROM pomiary WHERE data_i_czas_pomiaru BETWEEN \'{data_i_czas_od}\' AND \'{data_i_czas_do}\'".format(data_i_czas_od=dateTimeFrom,data_i_czas_do=dateTimeTo))
            print("...SELECT query succeeded...")
            
            # OK.... ale teraz jak w matplotlibie okreslic DATĘ jako os X, i x_axis jako os Y (x_axis to wartosci, os pionowa)
            
            myresult = cursor.fetchall()
            # print("The length of \'myresult\' is: ", len(myresult)) # pokazuje ile rekordow ma zostac wykorzystanych na wykresie
            
            list_x = []
            datetime_x = []
            list_y = []
            # datetime_x = []
            # list_y = []
            # print("Zaczynam konwersje")
            for x in myresult:
                # list_x.append(str(x[0]))
                # print("Przed konwesja")
                # print(str(x[0]))
                # print("Zamieniono format daty")
                datetime_x.append(datetime.strptime(str(x[0]), '%Y-%m-%d %H:%M:%S')) # dalem myslnik "-", zamiast "/" w dacie
                # print("Po konwersji")
                list_x.append(str(x[0]))
                list_y.append(str(x[1]))
            print(list_x[0])
            print(list_y[0])
            # teoretycznie datetime_x[] powinno byc lista datetime
            ########################################################## Zmienic wykres zeby ladnie wygladal ......
            fig = plt.figure(figsize=(18, 16), dpi= 80, facecolor='w', edgecolor='k')
            ax = plt.subplot(111)
            box = ax.get_position()
            ax.set_position([box.x0, box.y0 + box.height * 0.1,
                             box.width, box.height * 0.9])
            
            # Put a legend below current axis
            ax.legend(loc='upper right', bbox_to_anchor=(0.4, 1.0),
                      ncol=3, fancybox=True, shadow=True)
            
            ax.tick_params(axis='both', which='major', labelsize=20)
            ax.tick_params(axis='both', which='minor', labelsize=20)
            # plt.title("Wykres oddechu pięciu badanych osób")
            plt.grid()
            
            plt.locator_params(axis='y', nbins=10)
            plt.locator_params(axis='x', nbins=10)
            # ax.yaxis.set_ticks(np.arange(-0.6,1,0.1))

            ##################################################################################
            dates = mdates.date2num(datetime_x) # to powinno stworzyc liczby z listy[] datetime'ow
            ax.plot_date(dates, list_y, label='Historia ruchu wedlug wybranej daty')
            plt.xlabel("Data i czas", fontsize=16)
            plt.ylabel("amplituda [g]",fontsize=16)
            ##################################################################################
            
            plt.show()
            ################################################################### Do tego momentu data, godzina i pomiary poprawnie sie dodaja do list
            # for i in range(len(list_x)):
            #     print(list_x[i])
            # print(list_y[:10])
            
            # fig, ax = plt.subplots(1)
            # fig.autofmt_xdate()
            # ax.xaxis_date()
            # plt.plot(list_x, list_y)
            
            # xfmt = mdates.DateFormatter('%y-%m-%d %H:%M:%S')
            # ax.xaxis.set_major_formatter(xfmt)
            
            # plt.show()
            # fig, ax = plt.subplots(1)
            # fig.autofmt_xdate()
            # ########################################################################################################
            # # NADAC ODPOWIEDNI LABEL ZALEZNIE OD IMIENIA PACJENTA # TODO #
            # line1, = ax.plot(np.arange(0,len(array_x)*0.03,0.03), array_y, label='Label')
            
            # # Shrink current axis's height by 10% on the bottom
            # box = ax.get_position()
            # ax.set_position([box.x0, box.y0 + box.height * 0.1,
            #                   box.width, box.height * 0.9])
            # # Put a legend below current axis
            # plt.plot(array_x, array_y, label='Historia ruchu wedlug wybranej daty')
            # ax.legend(loc='upper right', bbox_to_anchor=(0.4, 1.0),
            #           ncol=3, fancybox=True, shadow=True)
            # plt.xlabel("data i czas")
            # plt.ylabel("amplituda [g]")
            # # plt.title("Wykres oddechu pięciu badanych osób")
            # plt.grid()
            # # ax.yaxis.set_ticks(np.arange(-0.1,0.5,0.05))
            # plt.show()
        except:
            print("SELECT query failed")

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
        try:
            cursor.execute("SELECT ID_pomiaru,x_axis FROM pomiary WHERE ID_pomiaru > ((SELECT MAX(ID_pomiaru) FROM pomiary)-(33*{sekundy}))".format(sekundy=jaki_zakres))
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
            line1, = ax.plot(np.arange(0,len(array_x)*0.03,0.03), array_y, label='Label')
            
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

        cnx.close()
        
        #logs_window.show()
# class logi_zdarzen(QMainWindow):    #
#     def __init__(self):
#         QMainWindow.__init__(self)
#         loadUi('logi_zdarzen.ui', self)
#         self.setWindowTitle("Logi zdarzeń")
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
#####################################   OKNO LOGOWANIA DO APLIKACJI   ######   PO POMYSLNEJ AUTORYZACJI POKAZUJE SIE GLOWNE OKNO PROGRAMU
class auth(QMainWindow):
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
    new_user_window = new_user()
    auth_win = auth()
    auth_win.show()
    # new_user_window = new_user()
    sys.exit(app.exec_())