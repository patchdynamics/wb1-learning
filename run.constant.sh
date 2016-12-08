YEAR=$1

cd wb1
set +e
\rm *.opt
\rm *.rso
set -e
sed s/%%%%/$YEAR/ inputs/control/constant.npt > w2_con.npt
cp inputs/TIN.CONSTANT.npt tin.npt
cp inputs/QIN$YEAR.npt qin.npt
cp inputs/QOUT$YEAR.npt qot_br1.npt
cp inputs/met$YEAR.npt met.npt
#../../bin/cequalw2.v371.mac.fast .
wine ../../bin/w2_ivf32_v372.exe
