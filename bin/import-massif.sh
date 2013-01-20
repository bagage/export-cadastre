#!/bin/bash
# ©Cléo 2010
# GPL v3 or higher — http://www.gnu.org/licenses/gpl-3.0.html

cd /data/project/cadastre.openstreetmap.fr/data

for i in 007 029 035 041 045 052 053 056 068 070 072 088 089 090 002 014 027 050 051 054 055 057 060 061 067 075 077 078 091 092 093 094 095 008 059 062 076 080 02A 02B 009 011 017 034 064 065 066 083 004 006 012 013 030 032 040 047 048 081 082 084 005 007 015 019 024 026 033 038 043 046 073 001 003 016 017 023 042 063 069 074 087  018 021 025 036 037 039 044 049 058 071 031 070 090 091 034 079 085 086 010 022 028 
do
	[ -d $i ] || mkdir $i
	cd $i
	/data/project/cadastre.openstreetmap.fr//bin/Qadastre2OSM --list $i > $i-liste.txt
#	sed -i "s/\([^ ]*\) - \(.*\) (.*)/\1 \2/" $i-liste.txt
	while read l 
		do
			code=`echo $l|cut -d' ' -f2`
			ville=`echo $l|sed 's/[^"]*"\([^"]*\)"//'`
			echo /data/project/cadastre.openstreetmap.fr//bin/Qadastre2OSM --download $i $code "$ville"
			/data/project/cadastre.openstreetmap.fr//bin/Qadastre2OSM --download $i $code "$ville"
			echo /data/project/cadastre.openstreetmap.fr//bin/Qadastre2OSM --convert $code "$ville"
			/data/project/cadastre.openstreetmap.fr//bin/Qadastre2OSM --convert $code "$ville"
			rm -f "$code-$ville.tar.bz2"
			tar cvf "$code-$ville.tar" --exclude="*.pdf" $code-$ville*
			bzip2 -f "$code-$ville.tar"
		done < $i-liste.txt
	cd ..
done
