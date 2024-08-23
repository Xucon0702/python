#!/bin/sh

HERE="$(realpath "$(dirname "$0")")"
rm -rf ${HERE}/cpu
mkdir -p ${HERE}/cpu

date=$(date "+%Y%m%d-%H%M%S")
file=${HERE}/cpu/top_${date}.txt

for i in $(seq 1 $1)
do
    echo "$i"
    echo "topDate:"`date +"%H:%M:%S"` >> $file
    sleep 1
    top -b  -n 1 | head -n 200 >> $file
done

tar cvf cpu_${date}.tar ./cpu

echo "Fininshed  ! ! ! "
