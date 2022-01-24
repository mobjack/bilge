#!/bin/sh

trap 'kill -TERM $PID ; wait $PID' TERM INT

if [ "$1" = "smbd" ] ; then
  shift
  if [ "$1" == "--" ] ; then
    shift
  fi

  # Kill old processes if any
  smb_count=`/bin/ps | grep smb.conf | grep -v grep | wc -l`
  if [ $smb_count -gt 0 ] ; then
      for PID in `ps -ef | grep -v grep | grep smb.conf | awk '{print $2}'`
      do
          kill -9 $PID
      done
  fi

  smbd --foreground --log-stdout --debuglevel=1 --configfile /smb.conf "$@" &

  PID=$!
  wait $PID
  wait $PID
  exit $?
fi

exec "$@"
