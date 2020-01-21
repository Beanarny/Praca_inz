create table czujniki (ID_czujnika INT NOT NULL AUTO_INCREMENT PRIMARY KEY, MAC_czujnika VARCHAR(30) NOT NULL UNIQUE, data_pierwszego_podlaczenia TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP);

-- insert into pomiary (sensor_ID, x_axis, y_axis, z_axis) values ('1', '1', '2', '1.5'); do usuniecia, przykladowe inserty

create table kontakty (ID_kontaktu INT NOT NULL AUTO_INCREMENT PRIMARY KEY, telefon VARCHAR(20), email VARCHAR(254), kod_pocztowy VARCHAR(20), miejscowosc VARCHAR(50), ulica VARCHAR(60))

create table plec (ID_plci, nazwa_plci VARCHAR(10))

create table pacjenci (ID_pacjenta INT NOT NULL AUTO_INCREMENT PRIMARY KEY, ID_czujnika INT, FOREIGN KEY (ID_czujnika) REFERENCES czujniki(ID_czujnika),
imie VARCHAR(50), nazwisko VARCHAR(50), pesel VARCHAR(20), ID_plci INT, FOREIGN KEY (ID_plci) REFERENCES plec(ID_plci),
ID_kontaktu INT, FOREIGN KEY (ID_kontaktu) REFERENCES kontakty(ID_kontaktu))

create table rejestr_lacznosci_czujnikow (ID_zdarzenia INT NOT NULL AUTO_INCREMENT PRIMARY KEY, ID_czujnika INT NOT NULL, FOREIGN KEY (ID_czujnika) REFERENCES czujniki(ID_czujnika),
rodzaj_zdarzenia VARCHAR(50), data_i_czas_zdarzenia TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP)

create table alarmy (ID_alarmu INT NOT NULL AUTO_INCREMENT PRIMARY KEY, ID_czujnika INT NOT NULL, FOREIGN KEY (ID_czujnika) REFERENCES czujniki(ID_czujnika), powod_alarmu VARCHAR(50))

create table pomiary (ID_pomiaru INT NOT NULL AUTO_INCREMENT PRIMARY KEY, ID_czujnika INT NOT NULL, FOREIGN KEY (ID_czujnika) REFERENCES czujniki(ID_czujnika),
data_i_czas_pomiaru TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, x_axis VARCHAR(10), y_axis VARCHAR(10), z_axis VARCHAR(10));