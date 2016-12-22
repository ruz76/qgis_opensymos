wget -O irz.html "http://portal.cenia.cz/irz/unikyPrenosy.jsp?Rok=2015&UnikOvzdusi=1&Typ=bezny&Mnozstvi=*&MetodaC=1&MetodaM=1&MetodaE=1&LatkaNazev=*&Ohlasovatel=&OhlasovatelTyp=subjektNazev&EPRTR=*&NACE=*&Lokalita=cr&Adresa=&Kraj=*&CZNUTS=*&SeskupitDle=subjektu&Razeni=vzestupne&OKEC=*"
tidy irz.html > irz2.html
xsltproc --html irz_to_wget.xsl irz2.html > irz.html.sh
bash irz.html.sh
xsltproc --html irz_to_csv.xsl irz.html > irz.csv
tail -n +2 irz.csv > pom
cat pom | tr -d '"' | tr -d "'" > irz.csv
rm pom
echo "NAME;ID;X;Y;POLLUTANT;POLLUTANTID;AMOUNT;TYPEOFDETERMINATION";
while read line           
do           
    NAME=`echo $line | cut -d";" -f1`;
    ID=`echo $line | cut -d";" -f2`;
    XY=`xsltproc --html id_to_xy.xsl $ID | tr -d '\r\n'`
    X=`echo $XY | cut -d";" -f2 | xargs`;
    Y=`echo $XY | cut -d";" -f1 | xargs`;
    ct=`echo $line | grep -o ";" | wc -l`
    for (( a=3; a<=$ct; a+=2 ))
    do  
        let "b = $a + 1"
        POLLUTANT=`echo $line | cut -d";" -f$a`;
        POLLUTANT1=`echo $POLLUTANT | cut -d"(" -f1 | xargs`;
        POLLUTANT2=`echo $POLLUTANT | cut -d"(" -f2 | cut -d")" -f1`;
        AMOUNT=`echo $line | cut -d";" -f$b`;
        AMOUNT1=`echo $AMOUNT | cut -d"[" -f1 | xargs`;
        AMOUNT2=`echo $AMOUNT | cut -d"[" -f2 | cut -d"]" -f1`;
        echo "\""$NAME"\";"$ID";-"$X";-"$Y";"$POLLUTANT1";"$POLLUTANT2";"$AMOUNT1";"$AMOUNT2;           
    done
done <irz.csv 
