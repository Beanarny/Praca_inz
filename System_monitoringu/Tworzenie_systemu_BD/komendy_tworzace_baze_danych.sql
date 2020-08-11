create table personel(
ID_pracownika INT NOT NULL AUTO_INCREMENT PRIMARY KEY, 
imie VARCHAR(50), 
nazwisko VARCHAR(50), 
plec VARCHAR(10),
data_urodzenia DATE,
PESEL VARCHAR(20),
data_zatrudnienia DATE,
login VARCHAR(20), 
zaszyfrowane_haslo VARCHAR(30),
telefon VARCHAR(20),
email VARCHAR(254),
kod_pocztowy VARCHAR(20),
miejscowosc VARCHAR(50),
ulica VARCHAR(60));

create table pacjenci (
ID_pacjenta INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
imie VARCHAR(50), 
nazwisko VARCHAR(50),
plec VARCHAR(10),
data_urodzenia DATE,
PESEL VARCHAR(20), 
telefon VARCHAR(20),
email VARCHAR(254),
kod_pocztowy VARCHAR(20),
miejscowosc VARCHAR(50),
ulica VARCHAR(60));

create table czujniki (
ID_czujnika INT NOT NULL AUTO_INCREMENT PRIMARY KEY, 
MAC_czujnika VARCHAR(30) NOT NULL UNIQUE, 
data_pierwszego_podlaczenia TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP);

create table przydzial_czujnikow (
ID_przydzialu INT NOT NULL PRIMARY KEY,
ID_pacjenta INT NULL, FOREIGN KEY (ID_pacjenta) REFERENCES pacjenci(ID_pacjenta),
ID_czujnika INT NULL, FOREIGN KEY (ID_czujnika) REFERENCES czujniki(ID_czujnika),
status VARCHAR(10),
data_rozpoczecia TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
data_zakonczenia TIMESTAMP);

create table pomiary (
ID_pomiaru INT NOT NULL AUTO_INCREMENT PRIMARY KEY, 
ID_czujnika INT NOT NULL, FOREIGN KEY (ID_czujnika) REFERENCES czujniki(ID_czujnika),
data_i_czas_pomiaru TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
modul VARCHAR(10),
x_axis VARCHAR(10), 
y_axis VARCHAR(10),
z_axis VARCHAR(10));

create table rejestr_zdarzen (
ID_zdarzenia INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
ID_pomiaru INT NULL, FOREIGN KEY (ID_pomiaru) REFERENCES pomiary(ID_pomiaru),
ID_pracownika INT NULL, FOREIGN KEY (ID_pracownika) REFERENCES personel(ID_pracownika),
rodzaj_zdarzenia VARCHAR(30),
opis_zdarzenia VARCHAR(60),
data_i_czas_zdarzenia TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP);





















