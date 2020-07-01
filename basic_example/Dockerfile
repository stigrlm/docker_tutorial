# specifikuje vychodzi image
FROM ubuntu:18.04

# aktuaklizuje repozitare a nainstaluje pip pre python 3
RUN apt-get update && apt-get install -y python3-pip

# specifikuje pracovny adresar, ktory sa aplikuje na vsetky dalsie prikazy
WORKDIR /app/

# skopiruje requirements.txt do adresara /app/
COPY requirements.txt .

# nainstaluje python zavislosti specifikovane v requirements.txt
RUN pip3 install -r requirements.txt

# skopiruje aplikaciu app.py do pracovneho adresara
COPY app.py .

# signaziluje ze aplikacia bude dostupna na porte 5000 a ten je potrebne vystavit pri spustatni kontajnera
EXPOSE 5000

# prikaz pre spusteni aplikace
CMD ["python3", "app.py"]
