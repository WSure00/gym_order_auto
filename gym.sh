function Run() {
    time=`date +%Y%m%d%H%M`
    cd $localdir
    mkdir -p ./log/
    /usr/bin/python3 ./gym_order.py > ./log/gym_order_${time}.log
}

function Install() {
    cd $localdir && localdir=`pwd`
    echo "1. crontab -e"
    echo "2. input \"55 10 * * sun,mon,tue,wed,thu /bin/bash ${localdir}/`basename $0`\""
}

localdir=`dirname $0`
if [ "$#" -gt "0" ];then
    if [ "$1" = "-i" ];then
        Install
    else
        echo "parameter error"
    fi
else
    Run
fi

