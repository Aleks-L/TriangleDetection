#!/bin/bash
#Target B
racknum=000006
hubid=1.1.2
ports=(0 1 2 3)
shelves=(0 1 2 3)
DEV=$(lsusb -t |grep hub/4p |grep -o 'Dev [0-9]*' |grep -o '[0-9]*')
Y=$(date -d "$ds" -u +"%Y")
M=$(date -d "$ds" -u +"%m")
D=$(date -d "$ds" -u +"%d")
MM=$(date -u +"%M")
H=$(date -u +"%H")
date="$(LC_ALL=C date -u +"%a, %d %b %Y %X %z")"
key_id="AKIAIEIVWAMZYPASVYPA"
key_secret="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"
bucket="my-rack"
content_type="application/octet-stream"
#fsopts="-S 1 -D 1 --font sans:72 --banner-colour 0xFF$racknum --line-colour 0xFF000000 -r 2592x1944 --jpeg 65"
fsopts="-S 25 -D 5 --font sans:72 --no-banner -r 1920x1080 --jpeg 65"

count=0
for i in "${ports[@]}"
do
  #sudo /home/pi/TargetA/hub-ctrl -b 001 -d 7 -P $i -p 0
  #sleep 5
  #sudo /home/pi/TargetA/hub-ctrl -b 001 -d 7 -P $i -p 1
  sleep 5
  #VIDEO=$(ls -l /dev/v4l/by-path/ |grep -o 'video[0-9]')
  fswebcam --device /dev/video${i} $fsopts /tmp/${shelves[$count]}.jpg
  md5="$(openssl md5 -binary < "/tmp/${shelves[$count]}.jpg" | base64)"
  sig="$(printf "PUT\n$md5\n$content_type\n$date\n/$bucket/$racknum/$Y/$M/$D/${shelves[$count]}-$H$MM.jpg" | openssl sha1 -binary -hmac "$key_secret" | base64)"
  #url="http://$bucket.s3.amazonaws.com/$racknum/$Y/$M/$D/${shelves[$count]}-$H$MM.jpg"
  curl --connect-timeout 20 -T /tmp/${shelves[$count]}.jpg http://$bucket.s3.amazonaws.com/$racknum/$Y/$M/$D/${shelves[$count]}-$H$MM.jpg -H "Date: $date" -H "Authorization: AWS $key_id:$sig" -H "Content-Type: $content_type" -H "Content-MD5: $md5" > /tmp/S3
  #sudo /home/pi/TargetA/hub-ctrl -b 001 -d 7 -P $i -p 0
  count=$[count + 1]
  rm -f /tmp/${shelves[$count]}.jpg
done
