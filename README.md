## Docker
Virtualizačná technológia pre beh aplikácií, ktorá na rozdiel od VM zdieľa aj kernel/OS. Je o úroveň vyššie čo sa týka abstrakcie:
- **VM** - abstrakcia nad HW
- **Docker** - abstrakcia nad OS

![alt text](https://image.slidesharecdn.com/headfirstdocker-160529162342/95/head-first-docker-5-638.jpg?cb=1464539065)

Typické docker workflow sa skladá z vytvorenia `docker image` a konfigurácie a spustenia `docker container`.

### Image
Jedná sa o spustiteľný balík, ktorý obsahuje všetky závislosti nutné pre beh aplikácie - runtime, kód, knižnice, environment variables, konfiguračné súbory. Spúšta sa pomocou príkazu docker build, ktorý vytvára image podľa manifestu definovanáho v Dockerfile.

#### Docker Hub
Nie všetky image si musíme vytvárať sami prostredíctvom Dockerfile. Existuje verejný repozitár, tzv. [Docker Hub](https://hub.docker.com/) kde sa nachádza množstvo pripravených imagov vhodných pre beh určitých komponet, napríklad databázu mongoDB, ktorú budeme používať v ďalšej časti tutoriálu. Prípadne je možné využiť niektorý z týchto imagov ako základ pre ďalšie úpravy prostredníctvom Dockerfile.

#### Príprava Dockerfile
Vyčerpávajúca dokumentácia je k dispozícií priamo na docker stránkach - [dockerfile best practice](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)

Dockerfile je manifest v ktorom sa definujú jednotlivé kroky/príkazy ktoré umožňujú opakovane vytvárať prostredie resp. image nutný pre beh aplikácie. V podstate je možné spustiť si čistý kontajner, prepnúť sa do neho, manuálne v ňom urobiť potrebné zmeny a prípravy a potom výsledok uložiť ako image, ale tým sa stratia všetky výhody jednoduchej a efektívnej úpravy.

Všetky príkazy v rámci Dockerfile sú zdokumentované na docker stránach:
- [Prehĺad príkazov](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/#dockerfile-instructions)
- [Detailenejšie súvislosti](https://docs.docker.com/engine/reference/builder/#from)

V následujúcej časti nebudem prechádzať všetky príkazy, ale ukážeme si príklad Dockerfile pre jednoduchú Flask aplikáciu a vyberiem niektoré detaily a súvislosti medzi príkazmi.

Príklad Dockerfile ktorý vytvára image pre základnu "Hello world" Flask aplikáciu:

```Dockerfile
# specifikuje vychodzi image
FROM ubuntu:18.04

# aktualizuje repozitare a nainstaluje pip pre python 3
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

# prikaz ktory sa spusti po starte kontajnera - spusti aplikaciu
CMD ["python3", "app.py"]
```

**ADD vs. COPY**

Funčne sú oba príkazy podobné, avšak ADD podporuje rozšírenú funkcionalitu ako napríklad automatickú extraciu tar balíčkov pri kopírovaní. COPY umožňuje len základné kopírovanie súborov a adresárov, preto je odporúčané používať COPY namiesto ADD.
Taktiež je odporúčané kopírovať súbory pre jednotlivé build steps oddelene, aby bolo maximalizové využitie cache, napr. v príklade hore kopírujeme zvlášť requirements.txt a aplikačné súbory.

**CMD vs. ENTRYPOINT**

ENTRYPOINT umožňuje nastaviť kontajner ako executable - t.j. špecifikuje aký príkaz sa spustí pri spustení kontajneru. CMD špecifikuje doplňujúce argumenty pre ENTRYPOINT v prípade, že nie sú žiadne definované ako súčasť docker run príkazu pri spustení kontajneru, t.j. CMD slúži ako default pre ENTRYPOINT. Ako entrypoint je možné použiť napr. aj bash script.

#### Docker build
Vytvorenie image z daného Dockerfile spustíme príkazom `docker build -t docker-tutorial:latest .`. Prepínač`-t, --tag` nastavuje aké meno a tag priraďujeme k image.
Bodka na konci špecifikuje kontext z ktorého sa bude image vytvárať - t.j aktuálny adresár z ktorého invokujeme docker build príkaz.  Dockerfile nemusíme špecifikovať, pretože sa defaultne používa ten, ktorý je nazvaný "Dockerfile" v danom adresári od kiaľ spúšťame `docker build`. V prípade, že chceme špecifikovať iný Dockerfile, môžeme tak urobiť prepínačom `-f, --file`.

Do kontextu sa rekurzívne predáva celý obsah špecifikovaného adresára a jeho podadresárov. V Dockerfile sa potom môžeme odkazovať na ktorýkoľvek súbor predaný v kontexte. Je vhodné do adresára ktorý používame ako kontext umiestňovať len súbory nutné pre build proces, prípadne využiť `.dockerignore` súbor - [viz. docker dokumentácia](https://docs.docker.com/engine/reference/builder/#dockerignore-file).

#### Vrstvy v image
[Detailný blog venovaný vrstvám v docker images.](https://mydeveloperplanet.com/2019/03/13/docker-layers-explained/)

Každý príkaz vytvára novú vrstvu, ale len príkazy `RUN`, `COPY` a `ADD` pridávajú dáta do image a zväčšujú tým jeho veľkosť.
To si vieme overiť cez príkaz docker history pre dané image id:
```
IMAGE               CREATED             CREATED BY                                      SIZE                COMMENT
3bb5d76ecde5        8 hours ago         /bin/sh -c #(nop)  CMD ["python3" "app.py"]     0B                  
1af1e7dc2d94        8 hours ago         /bin/sh -c #(nop)  EXPOSE 5000                  0B                  
45ba81a72a0d        8 hours ago         /bin/sh -c #(nop) COPY file:363490ef15fa4f53…   170B                
3f1328252569        8 hours ago         /bin/sh -c pip3 install -r requirements.txt     4.52MB              
c64ceaaae85d        8 hours ago         /bin/sh -c #(nop) COPY file:17b2b8de81d160bf…   6B                  
20739db67a83        8 hours ago         /bin/sh -c #(nop) WORKDIR /app/                 0B                  
f99a421029d6        8 hours ago         /bin/sh -c apt-get update && apt-get install…   424MB               
6a98a89dad74        3 days ago          /bin/sh -c #(nop)  CMD ["/bin/bash"]            0B                  
<missing>           3 days ago          /bin/sh -c #(nop)  ENV LANG=en_US.UTF-8 LANG…   0B                  
<missing>           3 days ago          /bin/sh -c #(nop) ADD file:2f1b81b76ea79cca3…   
```
Tento prístup šetrí miesto na disku a taktiež čas potrebný pre vytváranie imageov, kedže pri opätovnom vytváraní image sa vytvárajú len tie vrstvy v ktorých nastala zmena oproti minulému stavu a nezmenené vrstvy sa načítavajú z cache. Preto je dôležité dbať na usporiadanie jednolivých príkazov, a pokiaľ je to možné , tie u ktorých je predpoklad najčastejších zmien umiestňovať na koniec Dockerfile.

V prípade, že spustíme docker build znova, môžeme z výpisu pozorovať, ktoré vrstvy sa načítavajú z cache a ktoré sa vytvárajú odznova.
```
Sending build context to Docker daemon  46.08kB
Step 1/8 : FROM docker.dev.dszn.cz/debian:buster
 ---> 6a98a89dad74
Step 2/8 : RUN apt-get update && apt-get install -y python3-pip
 ---> Using cache
 ---> f99a421029d6
Step 3/8 : WORKDIR /app/
 ---> Using cache
 ---> 20739db67a83
Step 4/8 : COPY requirements.txt .
 ---> Using cache
 ---> c64ceaaae85d
Step 5/8 : RUN pip3 install -r requirements.txt
 ---> Using cache
 ---> 3f1328252569
Step 6/8 : COPY app.py .
 ---> Using cache
 ---> 45ba81a72a0d
Step 7/8 : EXPOSE 5000
 ---> Using cache
 ---> 1af1e7dc2d94
Step 8/8 : CMD ["python3", "app.py"]
 ---> Using cache
 ---> 3bb5d76ecde5
Successfully built 3bb5d76ecde5
Successfully tagged docker-tutorial:latest
```
Príkaz `docker images`/`docker image ls` vylistuje všetky image ktoré sú v lokálnom repozitári, mohli byť vytvorené lokálne, prípadne stiahnuté z repozitárov.

V prípade, že vytvoríme pozmenený image pod rovnakým menom a tagom, tak predchádzajúci image sa stane tzv. "dangling" a stratí svoje referencie.
```
docker-tutorial                                   latest                        48a4d341b1d2        2 minutes ago       626MB
<none>                                            <none>                        3bb5d76ecde5        26 hours ago        626MB

```
Tieto images je možné odstrániť pomocou príkazu `docker system prune`. Prepínač `-a, --all`odstráni aj všetky "unused" image, t.j. tie ktoré momentálne nie sú pripojené k žiadnemu kontajneru, čo spôsobí, že sa budú musieť celé opätovne vytvoriť. Tento príkaz odstráni aj všetky zastavené kontajnery a nepoužívané siete.

### Container
Container je bežiaca inštancia založená na docker image. Spúšta sa príkazom `docker run`
Príklad pre základné spustenie vyššie spomínaného hello world príkladu:
`docker run -p 5000:5000 docker-tutorial:latest`

Prepínač `-p, --publish` špecifikuje aký port z kontajneru sa má namapovať na host port aby bol umožnený prístup do kontajneru z vonkajšieho prostredia. Port 5000 bol už definovaný v Dockerfile cez príkaz EXPOSE, avšak až definovaním cez -p pri spustení kontajneru sa skutočne namapuje. Samotný EXPOSE v Dockerfile nezabezpečuje vystavenie portu, ale má dokumentačné účely. Časť príkazu`docker-tutorial:latest` špecifikuje meno a tag image ktorý sa použije pre spustenie kontajnera.

### Docker príkazy

Na docker dokumentačnej stránke je dostupný [kompletný zoznam docker príkazov](https://docs.docker.com/engine/reference/commandline/docker/).

`docker ps`
- vylistuje kontajnery, defaultne len tie ktoré práve bežia (vrátane pauznutých)
```
CONTAINER ID        IMAGE                    COMMAND             CREATED             STATUS              PORTS                    NAMES
7ee7666500b2        docker-tutorial:latest   "python3 app.py"    40 minutes ago      Up 4 minutes        0.0.0.0:5000->5000/tcp   nervous_booth
```
- prepínač `-a, --all` vylistuje aj zastavené kontajnery
```
CONTAINER ID        IMAGE                    COMMAND                  CREATED             STATUS                         PORTS                    NAMES
7ee7666500b2        docker-tutorial:latest   "python3 app.py"         About an hour ago   Up 40 minutes                  0.0.0.0:5000->5000/tcp   nervous_booth
54694d25f1c3        docker-tutorial:latest   "python3 app.py"         About an hour ago   Exited (0) About an hour ago                            nostalgic_lewin
6a6ddea77d44        48a4d341b1d2             "python3 app.py"         About an hour ago   Exited (0) About an hour ago                            heuristic_saha
41353e62057e        48a4d341b1d2             "python3 app.py"         2 hours ago         Exited (0) About an hour ago                            relaxed_bose
```
`docker stop`
- zastaví bežiaci kontajner - napr. `docker stop 7ee7666500b2`,
-vo všetkých ďalších príkazoch je možné využiť id kontajneru, prípadne aj meno

`docker start`
- naštartuje zastavený kontajner, neobnoví ale presmerovanie výstupu na terminál

`docker attach`
- pripojí výstup z kontajnera na terminál

`docker pause`
- pauzne procesy v kontajneri, ale kontajner naďalej beží - vhodné na emuláciu timeout errorov

`docker unpause`
- znova spustí procesy v pauznutom kontajneri

`docker exec`
- vykoná príkaz v bežiacom kontajneri
- napr. `docker exec -it 7ee7666500b2 bash` sa pripojí na terminál v kontajneri, kde je potom možné spúšťať ďalšie príkazy vo vnútri kontajneru

## Docker compose

Docker compose je nadstavba nad docker, ktorá umožňuje orchestráciu prostredia pozostávajúceho z viacerých kontajnerov.

Pomocou yaml súboru môžeme nakonfigurovať naraz viacero kontajnerov, nieje nutné pripájať konfiguračné prepínače k docker build a docker run príkazom.

V príklade máme nakonfigurovanú aplikáciu pozostávajúcu z dvoch kontajnerov:
- Flask aplikácia umožňujúca vytárať a listovať cez web knihy v knižnici
- Mongodb databáza ktorá zabezpečuje ukladanie dát

```yaml
version: "3.2"
services:
  flask:
    build:
      context: .
    image: flask_game:latest
    ports:
      - "5000:5000"
    depends_on:
      - mongo
    environment:
      - DEBUG=True
  mongo:
    image: mongo
    volumes:
      - /home/mongo_data:/data/db
```
`docker-compose build` zabezpečí vytvorenie definovaných image - v tomto prípade sa vytvára len image pre Flask appku, keďže mongodb používa už vytvorený oficálny image.

`docker-compose up --force-recreate` naštartuje oba kontajnery a vytvorí sieť ktorá ich prepojí.

`docker-compose stop` zastaví kontajnery.
`docker-compose down` ich aj odstráni spolu so sieťou.

Pre dosiahnutie rovnakého efektu bez docker-compose by bolo potrebné:
- nakonfigurovať sieť
- spustiť Flask app kontajner s danou konfiguráciou
- spustiť mongo kontajner s danou konfiguráciou
