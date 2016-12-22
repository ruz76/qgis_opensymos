#wget -O irz.html "http://portal.cenia.cz/irz/unikyPrenosy.jsp?Rok=2015&UnikOvzdusi=1&Typ=bezny&Mnozstvi=*&MetodaC=1&MetodaM=1&MetodaE=1&LatkaNazev=*&Ohlasovatel=&OhlasovatelTyp=subjektNazev&EPRTR=*&NACE=*&Lokalita=cr&Adresa=&Kraj=*&CZNUTS=*&SeskupitDle=subjektu&Razeni=vzestupne&OKEC=*"
#tidy irz.html > irz2.html
#xsltproc --html irz_to_wget.xsl irz2.html > irz.html.sh
#bash irz.html.sh
xsltproc --html irz_to_csv.xsl irz.html > irz.csv
tail -n +2 irz.csv > pom
cat pom | tr -d '"' | tr -d "'" > irz.csv
rm pom
echo "NAME;ID;X;Y;LATKA;LATKAID;MNOZSTVI;TYPURCENI";
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
        LATKA=`echo $line | cut -d";" -f$a`;
        LATKA1=`echo $LATKA | cut -d"(" -f1 | xargs`;
        LATKA2=`echo $LATKA | cut -d"(" -f2 | cut -d")" -f1`;
        MNOZSTVI=`echo $line | cut -d";" -f$b`;
        MNOZSTVI1=`echo $MNOZSTVI | cut -d"[" -f1 | xargs`;
        MNOZSTVI2=`echo $MNOZSTVI | cut -d"[" -f2 | cut -d"]" -f1`;
        #echo $a;
        #echo $b;
        echo "\""$NAME"\";"$ID";-"$X";-"$Y";"$LATKA1";"$LATKA2";"$MNOZSTVI1";"$MNOZSTVI2;           
    done
done <irz.csv 