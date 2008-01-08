#!/bin/bash

# Replace these three settings.
PROJDIR="/home/murphy/work/django/HOMEPAGE/murphytalk_django"
PIDFILE="$PROJDIR/mysite.pid"
SOCKET="$PROJDIR/mysite.sock"
MAXSPARE=1

#start 
django_start(){
    exec /usr/bin/env - \
	PYTHONPATH="../python:.." \
        $PROJDIR/manage.py runfcgi socket=$SOCKET pidfile=$PIDFILE maxspare=$MAXSPARE    
	#./manage.py runfcgi host=127.0.0.1 port=3033 pidfile=$PIDFILE maxspare=$MAXSPARE
}

#stop
django_stop(){
    cd $PROJDIR
    if [ -f $PIDFILE ]; then
	kill `cat -- $PIDFILE`
	rm -f -- $PIDFILE
    fi
}

case "$1" in
'start')
  echo "starting ..."
  django_start
  ;;
'stop')
  echo "stopping ..."
  django_stop
  ;;
'restart')
  django_stop
  sleep 1
  django_start
  ;;
*)
  echo "usage $0 start|stop|restart"
esac

