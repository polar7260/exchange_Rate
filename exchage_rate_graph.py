# -*- coding: utf-8 -*-
"""
Created on Wed Mar 27 14:43:32 2019

@author: likel
"""

import json
import requests
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import scipy.spatial as spatial
import matplotlib.dates as mdates
from pandas import DataFrame as df
import pandas as pd


def fmt(x, y):
    return '{x}\n rate:{y}'.format(x=x, y=y)

class FollowDotCursor(object):
    """Display the x,y location of the nearest data point.
    https://stackoverflow.com/a/4674445/190597 (Joe Kington)
    https://stackoverflow.com/a/20637433/190597 (unutbu)
    """
    def __init__(self, ax, x, y, formatter=fmt, offsets=(-20, 20)):
        try:
            x = np.asarray(x, dtype='float')
        except (TypeError, ValueError):
            x = np.asarray(mdates.date2num(x), dtype='float')
        y = np.asarray(y, dtype='float')
        mask = ~(np.isnan(x) | np.isnan(y))
        x = x[mask]
        y = y[mask]
        self._points = np.column_stack((x, y))
        self.offsets = offsets
        y = y[np.abs(y - y.mean()) <= 3 * y.std()]
        self.scale = x.ptp()
        self.scale = y.ptp() / self.scale if self.scale else 1
        self.tree = spatial.cKDTree(self.scaled(self._points))
        self.formatter = formatter
        self.ax = ax
        self.fig = ax.figure
        self.ax.xaxis.set_label_position('top')
        self.dot = ax.scatter(
            [x.min()], [y.min()], s=30, color='yellow', alpha=0.5)
        self.annotation = self.setup_annotation()
        plt.connect('motion_notify_event', self)

    def scaled(self, points):
        points = np.asarray(points)
        return points * (self.scale, 1)

    def __call__(self, event):
        ax = self.ax
        # event.inaxes is always the current axis. If you use twinx, ax could be
        # a different axis.
        if event.inaxes == ax:
            x, y = event.xdata, event.ydata
        elif event.inaxes is None:
            return
        else:
            inv = ax.transData.inverted()
            x, y = inv.transform([(event.x, event.y)]).ravel()
        annotation = self.annotation
        x, y = self.snap(x, y)
        annotation.xy = x, y
        annotation.set_text(self.formatter(mdates.num2date(x).date(), y))
        self.dot.set_offsets((x, y))
        event.canvas.draw()

    def setup_annotation(self):
        """Draw and hide the annotation box."""
        annotation = self.ax.annotate(
            '', xy=(0, 0), ha = 'right',
            xytext = self.offsets, textcoords = 'offset points', va = 'top',
            bbox = dict(
                boxstyle='round,pad=0.5', fc='yellow', alpha=0.5),
            arrowprops = dict(
                arrowstyle='->', connectionstyle='arc3,rad=0'))
        return annotation

    def snap(self, x, y):
        """Return the value in self.tree closest to x, y."""
        dist, idx = self.tree.query(self.scaled((x, y)), k=1, p=1)
        try:
            return self._points[idx]
        except IndexError:
            # IndexError: index out of bounds
            return self._points[0]


date_list=[]
usd_list=[]
jpy_list=[]
usd_dictionary={}
jpy_dictionary={}

term_year = relativedelta(years=1)
term_3month = relativedelta(months=3)
term_6month = relativedelta(months=6)
term_1month = relativedelta(months=1)

def choose_one(x):
    return  {'1': term_year, '2': term_3month, '3' : term_6month, '4' : term_1month}[x]

date_iterator = (datetime.today() - choose_one(input("Choose one \n 1. 1년 2. 3개월 3.6개월 4.1개월\n"))).date()

while date_iterator != datetime.today().date():
    date_list.append(date_iterator)
    date_iterator += timedelta(days=1)
    
for date in date_list:
    url='https://www.koreaexim.go.kr/site/program/financial/exchangeJSON?authkey=y3yL7pP10tUmqA7YW8vCr0AXhbqemgKa'+'&searchdate='+date.strftime("%Y%m%d")+'&data=AP01'
    res = requests.get(url)
    data = json.loads(res.text)
    
    if (str(data) == "[]"):
        usd_list.append("No data")
        jpy_list.append("No data")
        
    else:     
        for item in data:
            if(item['cur_unit'] == "USD"):
                usd_list.append(float(item['ttb'].replace(',','')))
            if(item['cur_unit'] == "JPY(100)"):
                jpy_list.append(float(item['ttb'].replace(',','')))


for i in range(0,len(usd_list)):
    usd_dictionary[date_list[i]] = usd_list[i]

for key in list(usd_dictionary.keys()):
    if usd_dictionary[key] == "No data":
        usd_dictionary.pop(key)
        
for i in range(0,len(jpy_list)):
    jpy_dictionary[date_list[i]] = jpy_list[i]

for key in list(jpy_dictionary.keys()):
    if jpy_dictionary[key] == "No data":
        jpy_dictionary.pop(key)
       


x_usd = list(usd_dictionary.keys())
y_usd = list(usd_dictionary.values())

x_jpy = list(jpy_dictionary.keys())
y_jpy = list(jpy_dictionary.values())

fig, ax1 = plt.subplots()


ax1.plot(x_usd, y_usd, 'r-', label='usd')
ax1.plot(x_jpy, y_jpy, 'g-', label='jpy')

cursor1 = FollowDotCursor(ax1,x_usd, y_usd)
cursor2 = FollowDotCursor(ax1,x_jpy, y_jpy)

ax1.grid()
ax1.legend()
plt.show()


df1 = df(usd_dictionary.values(), columns=["USD"], index = usd_dictionary.keys())
display(df1)
