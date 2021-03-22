#!/bin/bash

rm -f vsopcompiler.tar.xz
mkdir vsopcompiler
cp Makefile vsopcompiler/Makefile
cp -r sly vsopcompiler/sly
for fichier in *.py
do
cp $fichier vsopcompiler/$fichier
done
tar -cJf vsopcompiler.tar.xz vsopcompiler
rm -rf vsopcompiler