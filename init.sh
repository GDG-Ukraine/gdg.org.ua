#! /bin/sh
### BEGIN INIT INFO
# Provides:          blueberrypy
# Required-Start:    $remote_fs $all
# Required-Stop:
# Default-Start:     2 3 4 5
# Default-Stop:
# Short-Description: Set the CPU Frequency Scaling governor to "ondemand"
### END INIT INFO


PATH=/sbin:/usr/sbin:/bin:/usr/bin
APP_PATH=/home/gtug2/gdg.org.ua
IF=0.0.0.0
PORT=11010
cd $APP_PATH

. /lib/init/vars.sh
. /lib/lsb/init-functions
. $APP_PATH/env/bin/activate

case "$1" in
    start)
        blueberrypy serve -b $IF:$PORT -d
    	#start-stop-daemon --start --background --exec /etc/init.d/ondemand -- background
        ;;
    restart|reload|force-reload)
        echo "Error: argument '$1' not supported" >&2
        exit 3
        ;;
    stop)
        ;;
    *)
        echo "Usage: $0 start|stop" >&2
        exit 3
        ;;
esac
