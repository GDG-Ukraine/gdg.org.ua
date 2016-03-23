#! /bin/sh -e
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
PID_PATH=/var/tmp/run
PID=$PID_PATH/gdg.org.ua.development.pid
IF=0.0.0.0
IF=127.0.0.1
PORT=11010
cd $APP_PATH
mkdir -p $PID_PATH

. /lib/init/vars.sh
. /lib/lsb/init-functions

export PATH="$HOME/.pyenv/bin:$PATH"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"

. "$APP_PATH/.exports"


set -e

case "$1" in
    start)
        test -f $PID && log_daemon_msg "PID exists: `cat $PID`." && exit 1
        log_daemon_msg "Starting web server" "blueberrypy"
        blueberrypy serve -b $IF:$PORT -P $PID -d && sleep 2 && \
        log_daemon_msg "New blueberrypy with PID `cat $PID` has been started."
        exit $?
        ;;
    restart|reload|force-reload)
        $0 stop
        $0 start
        exit $?
        ;;
    stop)
        PROC_PID=`cat $PID`
        kill $PROC_PID && \
        log_daemon_msg "Killed blueberrypy with PID $PROC_PID."
        exit $?
        ;;
    *)
        log_daemon_msg "Usage: $0 start|stop" >&2
        exit 3
        ;;
esac
