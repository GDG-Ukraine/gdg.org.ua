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

. "$APP_PATH/.exports-dev"
. "$APP_PATH/.exports"


set -e

case "$1" in
    start)
        PROC_PID=`cat $PID`
        test -f $PID && log_daemon_msg "PID exists: $PROC_PID." && exit 1
        log_daemon_msg "Starting web server" "blueberrypy"
        blueberrypy serve -b $IF:$PORT -P $PID -d && sleep 2 && \
        log_daemon_msg "New blueberrypy with PID `cat $PID` has been started."
        exit $?
        ;;
    restart)
        PROC_PID=`cat $PID`
        kill -SIGHUP $PROC_PID
        exit $?
        ;;
    reload)
        PROC_PID=`cat $PID`
        kill -SIGUSR1 $PROC_PID
        exit $?
        ;;
    stop)
        PROC_PID=`cat $PID`
        kill -SIGTERM $PROC_PID && \
        log_daemon_msg "Killed blueberrypy with PID $PROC_PID."
        exit $?
        ;;
    *)
        log_daemon_msg "Usage: $0 start|stop|restart|reload" >&2
        exit 3
        ;;
esac
