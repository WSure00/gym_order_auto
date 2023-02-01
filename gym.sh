function Run() {
    time=`date +%Y%m%d%H%M`
    mkdir -p ./log/
    /usr/bin/python3 ./gym_order.py > ./log/gym_order_${time}.log
}

function Install() {

    localdir=`pwd`
    echo "1. crontab -e"
    echo "2. input \"55 10 * * sun,mon,tue,wed,thu /bin/bash ${localdir}/$0\""
}


if [ "$#" -gt "0" ];then
    if [ "$1" = "-i" ];then
        Install
    else
        echo "parameter error"
    fi
else
    Run
fi

