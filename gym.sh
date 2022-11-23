#!/bin/sh

time=`date +%Y%m%d%H%M`
/usr/bin/python3 {absolute_path}/gym_order.py > {absolute_path}/log/gym_order_${time}.log