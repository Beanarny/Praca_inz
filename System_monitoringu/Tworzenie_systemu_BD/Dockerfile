FROM mysql:latest
ENV MYSQL_ROOT_PASSWORD rootpass
ENV MYSQL_DATABASE main_db
ENV MYSQL_USER user
ENV MYSQL_PASSWORD userpass
ADD komendy_tworzace_baze_danych.sql /docker-entrypoint-initdb.d
EXPOSE 3306