#!/bin/bash
# My first script
source config.sh

echo $startStmt

a=(foo bar "foo 1" "bar two")  #create an array
b=("${a[@]}")                  #copy the array in another one 

for value in "${b[@]}" ; do    #print the new array 
echo "$value" 
done 

# for file in /home/user/*; do
#   echo ${file##*/}
# done


echo $endStmt


