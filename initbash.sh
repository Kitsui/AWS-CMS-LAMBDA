#!/bin/bash
# My first script
source config.sh

echo $startStmt

a=()  #create an array
                  #copy the array in another one 



for file in /home/user/*; do
  echo "files in directory :" ${file##*/} ,
  b=("${a[@]}" ${file##*/})
done

echo completed
echo 

for value in "${b[@]}" ; do    #print the new array 
echo "$value" 
done 


echo $endStmt


