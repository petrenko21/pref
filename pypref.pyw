#!/usr/bin/python
# -*- coding: cp1251 -*-
#
# PyPref - Preference game for Windows, *NIX and Pocket PC
# This source code is based on kpref by Azarniy I.V.
# and OpenPref (http://openpref.narod.ru)
#
# Author (version 2.0): Alexander aka amigo <amigo12@newmail.ru> - Aug 2007
# Versions 2.1-2.34: Vadim Zapletin <preference.gixx@mail.ru> - Feb-Mar 2018
# License: GNU GPL
#

import os
import time
import random

import sys
sys.path = sys.path + ['.']

from game.prfconst import *
from game.desktop import *
import game.cardlist as cardlist

# for PC version use lighton opton for orientation option
landscape = lighton

EKeyRightArrow = 'Right'
EKeyUpArrow = 'Up'
EKeyLeftArrow = 'Left'
EKeyDownArrow = 'Down'
EKeySelect = 'Return'
EKey5 = '5'

VERSION = ' 2.34'
FONT = 'Tahoma'
#FONT = 'Helvetica'
PATH = '.'

########### WinCE backlight and fullscreen support
try:
	if os.name == 'ce':
		from ctypes import windll, Structure, c_byte, c_ulong, byref
		keybd_event = windll.coredll.keybd_event
		GetActiveWindow = windll.coredll.GetActiveWindow
		SystemIdleTimerReset = windll.coredll.SystemIdleTimerReset
		GetSystemPowerStatusEx = windll.coredll.GetSystemPowerStatusEx
		SHFullScreen = windll.aygshell.SHFullScreen
		try:
			SHIdleTimerReset = windll.aygshell.SHIdleTimerReset
		except:
			SHIdleTimerReset = None

		class SYSTEM_POWER_STATUS_EX(Structure):
			_fields_ = [
				('ACLineStatus', c_byte),
				('BatteryFlag', c_byte),
				('BatteryLifePercent', c_byte),
				('Reserved1', c_byte),
				('BatteryLifeTime', c_ulong),
				('BatteryFullLifeTime', c_ulong),
				('Reserved2', c_byte),
				('BackupBatteryFlag', c_byte),
				('BackupBatteryLifePercent', c_byte),
				('Reserved3', c_byte),
				('BackupBatteryLifeTime', c_ulong),
				('BackupBatteryFullLifeTime', c_ulong)
			]
		pstat = SYSTEM_POWER_STATUS_EX()
		scnt = 0

		def FullScreenOn(e=None):
			gui.c.pack()
			gui.c.focus_set()
			desk.geometry('%dx%d+0+0'%gui.screen_size)
			ret = SHFullScreen(hwnd, 2|8)
			#print 'on', hwnd, ret

		def FullScreenOff(e=None):
			if gui.c == cwin:
				return
			gui.c.pack_forget()
			desk.geometry('0x0+0+0')
			ret = SHFullScreen(hwnd, 1|4)
			#print 'off', hwnd, ret
			save = gui.c
			gui.c = cwin
			list = ('Continue','Exit')
			while True:
				i = gui.PopUp(list, 'Python Pref')
				if i == 0:
					gui.c = save
					FullScreenOn()
					return
				break
			save.destroy()
			gui.c.destroy()
			tk.quit()

		def KeepBacklight():
			keybd_event(0x87,0,2,0)

		def DoNotSleep():
			global scnt
			scnt += 1
			if gui.c != cwin:
				SystemIdleTimerReset()
				if SHIdleTimerReset:
					SHIdleTimerReset()
				if gui.opt[lighton]:
					KeepBacklight()
				if scnt == 12 and (app.mode == demo or app.mode == run):
					try:
						gui.c.itemconfig('batt',text=BattStatus())
						gui.c.itemconfig('time',text=CurrTime())
					except:
						pass
			if scnt == 12:
				scnt = 0
			tk.after(5000, DoNotSleep)

		def BattStatus():
			if not GetSystemPowerStatusEx(byref(pstat),1):
				return 'n/a'
			if pstat.ACLineStatus:
				return 'AC'
			return str(pstat.BatteryLifePercent)+'%'

		def CurrTime():
			h,m = time.localtime()[3:5]
			return "%02d:%02d"%(h,m)
except:
	pass
########### WinCE try to guess pyPref directory path
if os.name == 'ce':
	try:
		from _winreg import *
		key = OpenKey(HKEY_CURRENT_USER,'Software\\Microsoft\\File Explorer',0,KEY_READ)
		(val,typ) = QueryValueEx(key,'StorageCardPath')
		card = '/' + val.split('\\')[1]
		for i in ('','/Program Files',card,card+'/Program Files'):
			PATH = i +'/Pypref'
			if os.path.isdir(PATH):
				break
			else:
				PATH = '.'
		CloseKey(key)
		# Fixup TclTk library location
		key = CreateKey(HKEY_LOCAL_MACHINE,'Environment')
		try:
			# test if exists
			(val,typ) = QueryValueEx(key,'TCL_LIBRARY')
			if not os.path.isdir(val):
				raise
		except:
			# create if not exists
			for i in ('/Program Files',card+'/Program Files'):
				path = i + '/Lib/tcl8.4'
				if os.path.isdir(path):
					SetValue(key,'TCL_LIBRARY',REG_SZ,path)
					SetValue(key,'TK_LIBRARY',REG_SZ,i+'/Lib/tk8.4')
					FlushKey(key)
					break
		CloseKey(key)
	except:
		PATH = '/Program Files/Pypref'
####################################################### WinCE end

from Tkinter import *
from tkFont import *

CONFIG_FILE = PATH + "/game/pypref.cfg"
SAVE_FILE = PATH + "/game/pypref%s.sav"

def MakePaper(size):
	(sw,sh) = size
	sw2,sw4 = sw/2,sw/4
	(h,k,o) = sw < 300 and (17,3,13) or (25,5,25)
	paper = (
		(
			(sw2,0, sw2,sh-sw2, 0,sh, sw,sh, sw2,sh-sw2),
			(sw4+k,0, sw4+k,sh-sw2+sw4-k, sw-sw4-k,sh-sw2+sw4-k, sw-sw4-k,0),
			(sw4-h,0, sw4-h,sh-sw2+sw4+h, sw-sw4+h,sh-sw2+sw4+h, sw-sw4+h,0),
			(0,sw2, sw4-h,sw2),
			(sw-sw4+h,sw2, sw,sw2),
			(sw2,sh-sw2+sw4+h, sw2,sh),
		),
		#(sw2-10,sh-sw2-10, sw2+10,sh-sw2+10),
		(sw2-o,sh-sw2-o, sw2+o,sh-sw2+o),
		(sw2-6, sh-sw2+5),
	)
	score = (
		(),
		(
			(sw4,sh-sw2+sw4-k,sw-sw2+8,0,h+k,0,0),
			(sw4+k+11,sh-sw2,sw-sw2-20,sw-sw2-20,sw4-k,-10,-10),
			(17,sh-sw2+sw4+h-1,sw2-5,sw2-5,sw4-h,-10,0),
			(sw2+4,sh-sw2+sw4+h-1,sw2-5,sw2-5,sw4-h,0,-10),
		),
		(
			(sw4-h+2,1,k+h,0,sh-sw2+sw4,0,0),
			(sw4+k+2,1,10,sw4-k-2,sh-sw2+sw4-k-10,0,7),
			(2,1,sw4-h,sw4-h,sw2-1,0,0),
			(2,sw2,10,sw4-h,sh-sw2-10,0,10),
		),
		(
			(sw2+sw4,1,k+h,0,sh-sw2+sw4,0,0),
			(sw2+sw4-h,1,10,sw4-k-2,sh-sw2+sw4-k-10,7,0),
			(sw-10,sw2,10,sw4-h,sh-sw2-10,10,0),
			(sw-sw4+h+k,1,sw4-h,sw4-h,sw2-1,0,0),
		),
	)
	return (paper,score)

class Lock:
	def __init__(self):
		self.var = IntVar()
		self.var.set(0)
	def __del__(self):
		#print "Lock deleted"
		pass
	def wait(self):
		tk.wait_variable(self.var)
	def signal(self):
		self.var.set(1-self.var.get())

class PrefGUI:

	def __init__(self,canvas,size):
		self.c = canvas
		self.paper = None
		self.score = None
		self.games = None
		self.retval = None
		self.snos = None
		self.query = None
		self.anytap = None
		self.blink = None
		self._blink_id = None
		self.handle = {}
		self.cards = {}
		#self.LoadCards()
		nopts = 24
		newopt = True
		try:
			f = open(CONFIG_FILE)
			try:
				self.opt = eval(f.read())
				del self.opt[-1]
				if len(self.opt) < nopts:
					self.opt.extend((0,)*(nopts-len(self.opt)))
				else:
					newopt = False
				self.opt.append(None)
			finally:
				f.close()
		except:
			self.opt = [0]*nopts + [None]
		if newopt:
			self.DefaultOpt(Sochi)
		cardlist.TCardList(sort=self.Sort)
		#(sw,sh) = tk.maxsize()
		(sw,sh) = size
		self.wince = os.name == 'ce'
		if self.wince:
			if sw == 640 or sh == 640:
				self.size = 'big'
				font_size = 16
			else:
				self.size = 'small'
				font_size = 9
		else:
			sw,sh = self.opt[landscape] and (640,480) or (480,640)
			self.size = 'big'
			font_size = 12
		if 0:
			sw,sh = (320,240)
			self.size = 'small'
			font_size = 9
		self.screen_size = (sw,sh)
		#print self.screen_size
		self.bg = '#008200'
		if self.wince:
			self.c.configure(width=sw, height=sh, bg='black')
		self.font_bold = Font(family=FONT, size=font_size, weight='bold')
		self.font_norm = Font(family=FONT, size=font_size, weight='normal')
		self.font_bheight = self.font_bold.metrics('linespace')
		# test for CEUX HI_RES_AWARE mode
		if self.wince and self.font_bheight > font_size*2:
			font_size /= 2
			self.font_bold = Font(family=FONT, size=font_size, weight='bold')
			self.font_norm = Font(family=FONT, size=font_size, weight='normal')
			self.font_bheight = self.font_bold.metrics('linespace')
		#print font_size, self.font_bheight
		if self.wince:
			# Make long press of 'Return' as 'Esc'
			self.press_time = 0
			def key_down(key):
				#print 'Press', key, self.press_time
				if key == 'Return':
					if not self.press_time:
						self.press_time = time.time()
					elif self.press_time > 0 and time.time() - self.press_time > 1:
						self.c.event_generate('<Escape>')
						self.press_time = -1
				else:
					self.keypress(key)
			def key_up(key):
				#print 'Release', key, self.press_time
				if key == 'Return' and self.press_time >= 0:
					sec = time.time() - self.press_time
					self.press_time = 0
					if sec > 1:
						self.c.event_generate('<Escape>')
					else:
						self.keypress(key)
				else:
					self.press_time = 0
			self.c.bind('<KeyPress>', lambda e: key_down(e.keysym))
			self.c.bind('<KeyRelease>', lambda e: key_up(e.keysym))
		else:
			self.c.bind('<Key>', lambda e: self.keypress(e.keysym))
		self.c.bind('<1>', self.click)
		self.c.focus_set()
		self.messages = {
'New Game': 'Новая игра',
'Load Game': 'Загрузить игру',
'Demo': 'Демо',
'Exit': 'Выход',
'Hide': 'Свернуть',
'About': 'О программе',
'Timeout': 'Задержка',
'Hint lead': 'Подсказка хода',
'Hint bid': 'Подсказка заказа',
'Hint discard': 'Подсказка сноса',
'Language': 'Язык',
'Back': 'Назад',
'Pref Club': 'Преферанс',
'Settings': 'Настройки',
'Till push': 'До нажатия',
'Yes': 'Да',
'No': 'Нет',
'sec': 'сек',
'Pass': 'Пас',
'Whist': 'Вист',
'Miser': 'Мизер',
'Half': 'Свои',
'Game limit': 'Размер пули',
'Game paused': 'Игра остановлена',
'Continue': 'Продолжить',
'Save game': 'Сохранить игру',
'Exit game': 'Закончить',
'Score': 'Пуля',
'Open cards': 'Открыться',
'Are you sure': 'Вы уверены',
'Cards order': 'Порядок карт',
'Suits order': 'Порядок мастей',
'Game': 'Игра',
'Interface': 'Интерфейс',
#'Confirm lead': 'Подтвержд. хода',
'Selection Key': 'Клавиша выбора',
'Orientation': 'Ориентация',
'Portrait': 'Книжная',
'Landscape': 'Альбомная',
'Backlight': 'Подсветка',
'Auto': 'Авто',
'On': 'Включена',
'nt': 'бк',
'Hints': 'Подсказки',
'Whists': 'Висты',
'Common': 'Общие',
'Pass game': 'Распасы',
'Score rules': 'Вариант',
'Without 3': 'Уход без 3',
'10 tricks': 'Десятерная',
'Stalingrad': 'Сталинград',
'Left level': 'Уровень левого',
'Right level': 'Уровень правого',
#'Greedy whist': 'Жлобский вист',
'Greedy': 'Жлобский',
#'Semiresponsible': 'Полуответств.',
'Responsible': 'Ответственный',
#'HalfWhist': 'Полвиста',
'HalfWhist': 'Уход за свои',
#'Whist-Pass': 'Пас-Пас-Вист',
'Pass-Pass-Whist': 'Пас-Пас-Вист',
'Progression': 'Прогрессия',
'Game for exit': 'Выход при игре',
'Exit on lost': 'Выход подсадом',
'Open talon': 'Открывать прикуп',
'Whisted': 'Вистуется',
'Checked': 'Проверяется',
'Sochi': 'Сочи',
'Rostov': 'Ростов',
'Leningrad': 'Ленинград',
'W/o 3': 'Без 3',
'spades': 'пик',
'clubs': 'треф',
'diamonds': 'бубей',
'hearts': 'червей',
		}

	def StartBlink(self,e=None):
		#print 'blink',self.blink
		if self.blink:
			try:
				state = self.c.itemcget(self.blink,'state')
				state = state == 'hidden' and 'normal' or 'hidden'
				self.c.itemconfig(self.blink,state=state)
				tk.update()
			except:
				#import traceback
				#traceback.print_exc()
				pass
		self._blink_id = tk.after(500,self.StartBlink)

	def StopBlink(self):
		if self._blink_id:
			tk.after_cancel(self._blink_id)
			self._blink_id = None

	def LoadCards(self):
		path = PATH+"/"+self.size+"/"
		pict = PhotoImage(file=path+'pict.gif')
		sw,sh = self.screen_size
		if self.wince:
			self.c.create_image(sw/2,sh/2,image=pict)
		else:
			pw,ph = pict.width(),pict.height()
			self.c.create_image(pw/2,ph/2,image=pict)
			self.c.configure(width=pw,height=ph)
		tk.update()
		for c in range(7,15):
			for m in (1,2,3,4):
				name = path+'%02d%s.gif'%(c,('','s','c','d','h')[m])
				dname = path+'d%02d%s.gif'%(c,('','s','c','d','h')[m])
				self.cards[c*10+m] = PhotoImage(file=name)
				self.cards['d'+str(c*10+m)] = PhotoImage(file=dname)
		name = path+'back.gif'
		back = PhotoImage(file=name)
		self.cards[None] = back
		self.card_size = (back.width(),back.height())
		for name in ('left','top','ok','esc','cur','hint'):
			file_name = path+name+'.gif'
			self.cards[name] = PhotoImage(file=file_name)
		for m in (1,2,3,4):
			name = path+'%s.gif'%('','s','c','d','h')[m]
			self.cards[m] = PhotoImage(file=name)
		if self.wince:
			tk.after(2000)
			cwin.configure(bg=self.bg)
		else:
			tk.after(3000)
			pass
		self.c.configure(bg=self.bg)
		if not self.wince:
			self.c.configure(width=sw,height=sh)

	def DefaultOpt(self,game):
		if game == Sochi:
			self.opt[pastalon] = 1
			self.opt[pasprogress] = 1
			self.opt[greedywhist] = 1
			self.opt[responsible] = 1
		elif game == Peter:
			self.opt[pastalon] = 1
			self.opt[pasprogress] = 1
			self.opt[greedywhist] = 0
			self.opt[responsible] = 0
		elif game == Rostov:
			self.opt[pastalon] = 0
			self.opt[pasprogress] = 0
			self.opt[greedywhist] = 0
			self.opt[responsible] = 0

	def Sort(self,a,b):
		morder = self.opt[sorder] and [1,2,3,4] or [1,3,2,4]
		return cmp(morder.index(a.CMast),morder.index(b.CMast)) or \
				(self.opt[corder] and cmp(a.CName,b.CName) or cmp(b.CName,a.CName))

	def Card(self,card,hint=None):
		if card:
			name, mast = card.CName, card.CMast
			card = name*10+mast
			dcard = 'd%d'%card
			return (self.cards[card],self.cards[dcard])
		return (self.cards[card],None)

	def DrawCard(self,x,y,card=None,hint=None,disabled=False,ngamer=0,mtag=None,blink=None):
		tags = mtag and ('card', mtag, 'c'+str(ngamer)) or 'c'+str(ngamer)
		imgs = self.Card(card)
		id = self.c.create_image(x,y,image=imgs[0],disabledimage=imgs[1],anchor='nw',tags=tags)
		if disabled: 
			self.c.itemconfig(id,state='disabled')
		if card and hint:
			self.c.create_image(x,y,image=self.cards['hint'],anchor='nw',tags=tags)
		if blink:
			self.blink = self.c.create_image(x,y,image=self.cards['cur'],anchor='nw',tags=tags)
#			if self._blink_id:
#				tk.after_cancel(self._blink_id)
#			self._blink_id = tk.after(500,self.StartBlink)

	def DrawText(self,x,y,txt=None,fg='#ffffff',jst='left',tag=None,nls=True,fnt='bold',an=None,shadow=None):
		#an = jst == 'left' and 'nw' or jst == 'right' and 'ne' or 'n'
		if an is None:
			an = jst == 'left' and 'sw' or jst == 'right' and 'se' or 's'
		if nls:
			txt = self.nls(txt)
		font = fnt == 'bold' and self.font_bold or self.font_norm
		#self.c.create_text(x,y,font='Tahoma 10 bold',text=txt,anchor=an,justify=jst,fill=fg,tags=tag)
		if shadow:
			off = self.size == 'small' and 1 or 2
			self.c.create_text(x+off,y+off,font=font,text=txt,anchor=an,justify=jst,fill=shadow,tags=tag)
		self.c.create_text(x,y,font=font,text=txt,anchor=an,justify=jst,fill=fg,tags=tag)

	def ShowMast(self,x,y,mast,color=None,ngamer=0):
		#self.c.create_image(x,y,image=self.Card(card),anchor='nw',tags='c'+str(ngamer))
		txt = ('','s','c','d','h')[mast]
		clr = mast > 2 and 'red' or 'white'
		#self.c.create_text(x,y,font='Tahoma 10 bold',fill=clr,text=txt,anchor='nw',tags='t'+str(ngamer))
		self.c.create_text(x,y,font=self.font_bold,fill=clr,text=txt,anchor='nw',tags='t'+str(ngamer))

	def Clear(self,ngamer=None,what='c'):
#		self.img.clear(self.bg)
#		if app.mode != halt:
#			(x,y) = self.img.size
#			self.img.polygon((x-10,y-7, x-4,y-7, x-7,y-4), outline=(0,255,0), fill=(0,255,0))
		if ngamer is None:
			self.c.delete('all')
			self.snos = None
			gui.ShowEsc()
			if self.wince and (app.mode == demo or app.mode == run):
				(sw,sh) = self.screen_size
				(cw,ch) = self.card_size
				#x = sw - (self.size == 'big' and 30 or 20)
				x = sw - 3
				y = sh - ch
				h = self.font_bheight
				#self.c.create_text(x,y-h,font=self.font_bold,fill='#005500',text=CurrTime(),anchor='center',tags='time')
				#self.c.create_text(x,y,font=self.font_bold,fill='#005500',text=BattStatus(),anchor='center',tags='batt')
				self.c.create_text(x,y-h,font=self.font_bold,fill='#005500',text=CurrTime(),justify='right',anchor='e',tags='time')
				self.c.create_text(x,y,font=self.font_bold,fill='#005500',text=BattStatus(),justify='right',anchor='e',tags='batt')
		else:
			self.c.delete(what+str(ngamer))

	def ShowHand(self,*args,**kw):
		(sw,sh) = self.screen_size
		if sw > sh:
			self.ShowHand_landscape(*args,**kw)
		else:
			self.ShowHand_portrait(*args,**kw)

	def ShowHand_portrait(self,gamer,idx=-1,hint=None,hint1=None,counter=None):
		nbr = gamer.nGamer
		ncards = gamer.aCards.AllCard()
		(cw,ch) = self.card_size
		(sw,sh) = self.screen_size
		if gamer.closed:
			inc = 5
		elif nbr == 1:
			inc = cw/5
		else:
			inc = ch/4
		ln = ncards*inc + cw-inc
		#mv = 5
		mv = self.size == 'big' and 10 or 8
		if nbr == 1:
			y = sh-ch
			x = (sw-ln)/2
		elif nbr == 2:
			x,y = 1,1
		else:
			x,y = sw-cw,1
		self.Clear(nbr)
		prev = None
		for i in range(0,12):
			#bg = '#ffffff'
			dis = False
			card = gamer.aCards.At(i)
			movtag = None
			if card:
				if gamer.closed:
					card = None
				rx,ry = x,y
				if i == idx:
					self.retval = card
					if nbr == 1:
						ry -= mv
					elif nbr == 2:
						rx += mv
					else:
						rx -= mv
				xo,yo = 0,0
				if card:
					if counter:
						if not (counter.nMin <= i <= counter.nMax):
							#bg = '#e0e0e0'
							dis = True
						else:
							movtag = i == idx and 'movok' or ('mov'+str(i))
					if prev and card.CMast != prev:
						off = self.size == 'small' and 2 or 5
						if nbr == 1:
							#xo += cw/2
							self.c.create_image(rx+xo,ry+yo,image=self.cards['left'],anchor='nw',tags='c'+str(nbr))
							xo += off
							#self.img.line((rx+3,ry, rx+1,ry+2, rx+1,ry+26, rx+4,ry+29),0x404040)
						else:
							self.c.create_image(rx+xo,ry+yo,image=self.cards['top'],anchor='nw',tags='c'+str(nbr))
							yo += off
							#self.img.line((rx,ry+3, rx+2,ry+1, rx+18,ry+1, rx+21,ry+4),0x404040)
					prev = card.CMast
				self.DrawCard(rx+xo,ry+yo,card,(hint == card or hint1 == card),dis,nbr,movtag,i==idx)
				#if nbr == 1 or gamer.closed:
				if nbr == 1:
					x += inc+xo
				else:
					y += inc+yo
		self.redraw(())

	def ShowHand_landscape(self,gamer,idx=-1,hint=None,hint1=None,counter=None):
		nbr = gamer.nGamer
		(cw,ch) = self.card_size
		(sw,sh) = self.screen_size
		if gamer.closed:
			inc = 5
		else:
			inc = cw/5
		ncards = gamer.aCards.AllCard()
		ln = ncards*inc + cw-inc
		mv = self.size == 'big' and 10 or 8
		if nbr == 1:
			if not gamer.closed:
				ln = 0
				for m in (1,2,3,4):
					ncards = gamer.aCards.AllCard(m)
					if ncards:
						ln += ncards*inc + cw-inc
			y = sh-ch
			x = (sw-ln)/2
		elif nbr == 2:
			x,y = 1,self.font_bheight+mv
			#x,y = 1,gamer.closed and 1 or mv
		else:
			x,y = sw-1,self.font_bheight+mv
			#x,y = sw-1,gamer.closed and 1 or mv
		self.Clear(nbr)
		prev = None
		rx,ry = x,y
		if nbr == 3 and ncards:
			mast = not gamer.closed and gamer.aCards.At(0).CMast or None
			ncards = gamer.aCards.AllCard(mast)
			ln = ncards*inc + cw-inc
			rx -= ln
		for i in range(0,12):
			#bg = '#ffffff'
			dis = False
			card = gamer.aCards.At(i)
			movtag = None
			if card:
				xo,yo = 0,0
				if gamer.closed:
					card = None
				if i == idx:
					self.retval = card
#					if nbr == 1:
#						ry -= mv
#					elif nbr == 2:
#						rx += mv
#					else:
#						rx -= mv
					yo -= mv
				if card:
					if counter:
						if not (counter.nMin <= i <= counter.nMax):
							#bg = '#e0e0e0'
							dis = True
						else:
							movtag = i == idx and 'movok' or ('mov'+str(i))
					if prev and card.CMast != prev:
						#off = self.size == 'small' and 2 or 5
						if nbr == 1:
							xo += cw-inc + 2
						elif nbr == 2:
							rx = x
							ry += ch/4
						else:
							ncards = gamer.aCards.AllCard(card.CMast)
							ln = ncards*inc + cw-inc
							rx = x - ln 
							ry += ch/4
					prev = card.CMast
				self.DrawCard(rx+xo,ry+yo,card,(hint == card or hint1 == card),dis,nbr,movtag,i==idx)
				rx += inc+xo
		self.redraw(())

	def ShowMove(self,card=None,gamer=None):
		(cw,ch) = self.card_size
		(sw,sh) = self.screen_size
		#x = (sw - 2*(cw+1))/2
		#y = (sh - 2*(ch+1))/2
		x = sw/2
		if sw < sh:
			y = sh/2
			y -= self.size == 'small' and 15 or 25
		else:
			y = ch+2
		#y = sh/2-ch/2
		if gamer:
			nbr = gamer.nGamer
			if nbr == 1:
				x,y = x-cw/2,y
			elif nbr == 2:
				x,y = x-cw,y-ch
			else:
				x,y = x,y-ch
			if card:
				if self.blink:
					self.c.delete(self.blink)
					self.blink = None
				self.DrawCard(x,y,card,mtag=('m'+str(nbr)))
				self.ShowHand(gamer)
			else:
				#self.img.rectangle((x,y, x+cw,y+ch), self.bg, self.bg)
				id = self.c.find_enclosed(x,y,x+cw,y+ch)
				self.c.delete(id)
		else:
			#self.img.rectangle((x, y, x+(cw+1)*2, y+(ch+1)*2), self.bg, self.bg)
			self.Clear(0)

	def ShowGame(self,gamer,game=None,nMove=0,hint=None):
		nbr = gamer.nGamer
		(cw,ch) = self.card_size
		(sw,sh) = self.screen_size
		#sw2,r = sw/2,30
		if nMove and nMove != -2:
			color = '#ffffff'
		else:
			color = '#ffff00'
		scolor = '#005500'
		if sw < sh:
			if nbr == 2:
				x = cw + 10
				y = self.font_bheight + 5
			elif nbr == 3:
				x = sw - (cw + 10)
				y = self.font_bheight + 5
			else:
				x = sw / 2
				y = sh - (ch + 10)
		else:
			if nbr == 2:
				x = 10
				y = self.font_bheight + 1
			elif nbr == 3:
				x = sw - 10
				y = self.font_bheight + 0
			else:
				x = sw / 2
				y = sh - (ch + 10)
		jst = nbr == 2 and 'left' or nbr == 3 and 'right' or 'center'
		if game:
			tag = 't'+str(nbr)
			self.Clear(nbr,'t')
			## Show controll ############
			if nMove < 0 and app.mode == run:
				self.retval = game
				xc = x+(self.size == 'big' and 50 or 32)
				self.ShowJoy(xc,y+2)
			##############################
			sleep = (color == '#ffffff' and not gamer.human)
			if hint == game:
				color = '#00ffff'
			if game == pas:
				self.DrawText(x,y,'Pass',color,jst,tag,shadow=scolor)
			elif game == vist and not (app.CurrentGame >= g101 and self.opt[check10]):
				self.DrawText(x,y,'Whist',color,jst,tag,shadow=scolor)
			elif game == g86:
				self.DrawText(x,y,'Miser',color,jst,tag,shadow=scolor)
			elif game == halfvist:
				self.DrawText(x,y,'Half',color,jst,tag,shadow=scolor)
			elif game == bez3:
				self.DrawText(x,y,'W/o 3',color,jst,tag,shadow=scolor)
			elif game%10 < 5:
				#text = self.nls(str(game/10)+' ')+self.nls(('','spades','clubs','diamonds','hearts')[game%10])
				#text = unicode(str(game/10)+' ') + (u'',u'\u2660',u'\u2663',u'\u2666',u'\u2665')[game%10]
				#text = unicode(str(game/10)+' ')+(u'',u'\u2664',u'\u2667',u'\u25c7',u'\u2661')[game%10]
				text = unicode(str(game/10)+' ')
				xc = x
				yc = y-self.font_bheight/2
				ac = 'w'
				if nbr == 1:
					jst = 'right'
				elif nbr == 2: 
					xc += self.font_bold.measure(text)
				else:
					x -= self.size == 'small' and 13 or 19
					ac = 'e'
				self.DrawText(x,y,text,color,jst,tag,nls=False,shadow=scolor)
				#self.c.create_text(x,y,font=self.font_bold,text=txt,anchor=an,justify=jst,fill=fg,tags=tag)
				#id = self.c.create_text(x-7-off,y, self.nls(str(game/10)), fill=color)
				#self.ShowMast(x+2+off,y-9,game%10,color=None)
				self.c.create_image(xc,yc,image=self.cards[game%10],anchor=ac,tags=tag)
			elif game%10 == 5:
				text = self.nls(str(game/10)+' ') + self.nls('nt')
				self.DrawText(x,y,text,color,jst,tag,nls=False,shadow=scolor)
			else:
				sleep = False
			self.redraw(())
			if sleep:
				self.sleep(0.5)
		else:
			sw2 = sw/2
			tag = 'i'+str(nbr)
			self.Clear(nbr,'i')
#			if not (self.size == 'small' and sw > sh):
#				r = self.font_bheight*1.5
#			else:
#				r = self.font_bheight+
			r = self.font_bheight*1.4
			if sw < sh:
				cx,cy = sw2,2*self.font_bheight+r
			else:
				if self.size == 'small':
					r = self.font_bheight*1.2
				#cx,cy = r+2,sh-ch/2-r
				cx,cy = r+2,sh-ch-r
			if len(self.c.find_withtag('i0')) == 0:
				arc_color = '#005500'
				self.c.create_arc((cx-r,cy-r,cx+r,cy+r),start=90,extent=120,outline=self.bg,fill=arc_color,tags='i0')
				self.c.create_arc((cx-r,cy-r,cx+r,cy+r),start=210,extent=120,outline=self.bg,fill=arc_color,tags='i0')
				self.c.create_arc((cx-r,cy-r,cx+r,cy+r),start=330,extent=120,outline=self.bg,fill=arc_color,tags='i0')
			if nbr == 1:
				xc,yc = cx, cy+r/2
			elif nbr == 2:
				xc,yc = cx-r*0.433, cy-r*0.25
			else:
				xc,yc = cx+r*0.433, cy-r*0.25
			if nMove:
				if nMove == 1:
					self.DrawText(xc,yc,nMove,color,'center',tag,fnt=(nMove == 1 and 'bold' or 'norm'),an='center')
			else:
				if gamer.nGetsCard:
					s = str(gamer.nGetsCard)
					self.DrawText(xc,yc,gamer.nGetsCard,color,'center',tag,an='center')
					if sw < sh:
						y += nbr == 1 and -self.font_bheight or self.font_bheight
					else:
						if nbr == 1:
							y -= self.font_bheight
						elif nbr == 2:
							x,jst = sw2-cw-10,'right'
						else:
							x,jst = sw2+cw+10,'left'
					#self.DrawText(x,y,'\x95'*gamer.nGetsCard,color,jst,tag,shadow=scolor)
					self.DrawText(x,y,'.'*gamer.nGetsCard,color,jst,tag,shadow=scolor)
					for n in (1,2,3):
#						if n != gamer.nGamer:
#							self.c.itemconfig('m'+str(n),state='disabled')
						if n == gamer.nGamer:
							x,y = self.c.coords('m'+str(n))
							tag = self.c.itemcget('m'+str(n),'tags')
							self.blink = self.c.create_image(x,y,image=self.cards['cur'],anchor='nw',tags=tag)
							self.StartBlink()
						else:
							self.c.itemconfig('m'+str(n),state='disabled')
					self.redraw(())
					self.HitReturn(anytap=True)
					self.StopBlink()
				self.ShowMove()
			self.redraw(())
			#s = u'\u220e'*gamer.nGetsCard + s
			#s = u'\u2579'*gamer.nGetsCard + s

	def HitReturn(self,forcekey=False,ok=True,anytap=False):
		timeout = self.opt[wait]
		if app.mode == demo:
			#self.sleep(0.5)
			self.sleep(2)
		elif not timeout or forcekey:
			if ok:
#				x,y = 2,self.screen_size[1]-2
#				self.DrawText(x,y,(self.opt[selkey] and ' 5' or 'ok'),'#00ff00','left','ok')
#				#self.img.text((x,y),(self.opt[selkey] and ' 5' or 'ok'),(0,255,0))
#				self.redraw(())
				self.ShowOk()
			save_handle = self.handle
			self.handle = {}
			if self.opt[selkey] != 1:
				self.handle[EKeySelect] = lock.signal
			if self.opt[selkey] > 0:
				self.handle[EKey5] = lock.signal
			self.anytap = anytap
			while True:
				lock.wait()
				if app.mode == stop:
					self.StopGame()
					if app.mode != halt:
						continue
				break
			self.anytap = None
			self.handle = save_handle
			if ok:
				self.c.delete('ok')
		else:
			self.sleep(timeout)
		#self.redraw(())

	def ShowJoy(self,x,y):
		self.c.delete('joy')
		acolor = '#00ff00'
		#ocolor = '#005500'
		ocolor = self.bg
		if self.size == 'big':
			w = 50
		else:
			w = 18
		w2,w4,w5 = w/2,w/4,w/5		
		self.c.create_polygon((x, y-w2, x+w2, y-w, x+w, y-w2, x+w2, y),outline=acolor,fill=acolor,tags='joy')
		self.c.create_rectangle((x+w4, y-w4, x+w-w4, y-w+w4),outline=ocolor,fill=ocolor,tags=('joy','joybox'))
		#self.c.create_rectangle((x+w5, y-w5, x+w-w5, y-w+w5),outline=ocolor,fill=ocolor,tags=('joy','joybox'))
		self.ShowOk()

	def ShowOk(self):
		x,y = self.screen_size[0]-1,self.screen_size[1]-1
		self.c.create_image(x,y,image=self.cards['ok'],anchor='se',tags='ok')
		self.redraw(())

	def ShowEsc(self):
		x,y =1,self.screen_size[1]-1
		self.c.create_image(x,y,image=self.cards['esc'],anchor='sw',tags='esc')
		#self.redraw(())

	def ShowPrikup(self,n,card1=None,card2=None):
		(cw,ch) = self.card_size
		(sw,sh) = self.screen_size
		x = sw/2 - cw/2 - cw/4
		if sw < sh:
			y = sh/2 - ch/2
		else:
			y = ch/2+2
		#self.img.rectangle((x-cw, y, x+cw+cw, y+ch), self.bg, self.bg)
		self.Clear(0)
		self.c.delete('out')
		if n and self.snos:
			#ox,oy = sw/2, sh/2+ch/2+10
			ox,oy = sw/2, y+ch+10
			ow,off = self.size == 'small' and (20,3) or (40,6)
			oh = ow/2
			self.c.create_oval((ox-oh,oy,ox+oh,oy+oh),outline='#005500',fill='#005500',tags='out')
			#self.c.create_polygon((ox-3,oy+4,ox+3,oy+4,ox,oy+7),outline='#00ff00',fill='#00ff00',tags='out')
			oy += oh/2-off/2
			self.c.create_polygon((ox-off,oy,ox+off,oy,ox,oy+off),outline='#00ff00',fill='#00ff00',tags='out')
		opencards = (card1 and 1 or 0)+(card2 and 1 or 0)
		if n == 2:
			off = (opencards < 2 and 2 or 0)
			self.DrawCard(x+off,y,card2)
			self.DrawCard(x-off+cw/2,y,card1)
		elif n == 1:
			self.DrawCard(x,y,card1)
		self.redraw(())
		if opencards == 2:
			#self.HitReturn()
			self.HitReturn(anytap=True)

	#def MakeGame(self,gamer,game=None,vistpas=False,hint=None,rightgame=None):
	def MakeGame(self,gamer,game=None,vistpas=False,hint=None):
		val = 0
		if vistpas:
			list = [vist,pas]
			if self.opt[halfwhist] and nGetMinCard4Vist(game) >= 2:
				nRight = gamer.nGamer == 1 and 3 or (gamer.nGamer == 2 and 1 or 2)
				if app.Gamer(nRight).GamesType == pas:
					list = [halfvist,vist]
			                        
		else:
			list = []
			if game:
				list.append(pas)
				val += 1
				if gamer.GamesType == undefined and game < g91:
					list.insert(0,g86)
					val += 1
				#if right gamer or left gamer == pas:
				nRight = gamer.nGamer == 1 and 3 or (gamer.nGamer == 2 and 1 or 2)
				nLeft = gamer.nGamer == 1 and 2 or (gamer.nGamer == 2 and 3 or 1)
				if game >= g61 and game != g86 and (app.Gamer(nRight).GamesType == pas or app.Gamer(nLeft).GamesType == pas):	
                                        if app.Gamer(nRight).GamesType == pas and nRight == app.nCurrentStart.nValue or gamer.nGamer == app.nCurrentStart.nValue:
                                                list.append(game)                                        
				# Set min game after raspas circle
				if game < g61:
					game = gamer.MinTricks()*10+1
					list.append(game)
			else:
				game = gamer.GamesType
				if game == g86:
					return g86
				if self.opt[without3]:
					list.append(bez3)
					val += 1
				list.append(game)
			while True:
				game = NextGame(game)
				list.append(game)
				if game == g105:
					break
		#print list
		game = list[val]
		if list.count(hint):
			val = list.index(hint)
			hint = list[val]
		counter = Tncounter(val,0,len(list)-1)
		def ctrl(key):
			if key == EKeyRightArrow:
				counter.next()
			elif key == EKeyLeftArrow:
				counter.prev()
			elif key == EKeyDownArrow:
				prev = list[counter.nValue]
				if prev < g61 or prev == g86:
					find = 101
				elif int(prev/10) == int(game/10):
					find = 100+prev%10
				else:
					find = prev-10
				if find < game:
					find = game
				while True:
					counter.prev()
					cur = list[counter.nValue]
					if cur == pas or cur == vist or cur == g86 or cur == bez3 or cur == find:
						break
			elif key == EKeyUpArrow:
				prev = list[counter.nValue]
				if prev < g61 or prev == g86:
					find = game
				elif int(prev/10) == 10:
					find = 60+prev%10
				else:
					find = prev+10
				if find < game:
					find = game
				while True:
					counter.next()
					cur = list[counter.nValue]
					if cur == pas or cur == vist or cur == g86 or cur == bez3 or cur == find:
						break
			elif key == EKeySelect:
				counter.nValue = -1
			lock.signal()
		self.handle[EKeyLeftArrow] = lambda:ctrl(EKeyLeftArrow)
		self.handle[EKeyRightArrow] = lambda:ctrl(EKeyRightArrow)
		self.handle[EKeyUpArrow] = lambda:ctrl(EKeyUpArrow)
		self.handle[EKeyDownArrow] = lambda:ctrl(EKeyDownArrow)
		if self.opt[selkey] != 1:
			self.handle[EKeySelect] = lambda:ctrl(EKeySelect)
		if self.opt[selkey] > 0:
			self.handle[EKey5] = lambda:ctrl(EKeySelect)
		while counter.nValue >= 0:
			self.ShowGame(gamer,list[counter.nValue],(vistpas and -2 or -1),hint)
			lock.wait()
			if self.StopGame():
				break
		self.handle = {}
		self.c.delete('joy')
		return self.retval

	def MakeMove(self,gamer,card=None,hint=None,hint1=None,out=None):
		(sw,sh) = self.screen_size
		n = gamer.aCards.Count()
		if n == 1:
			return gamer.aCards.At(0)
		self.snos = (out or gamer.nGamer == 1 and n > 10)
		Min = 0
		Max = n-1
		mastUpDn = sw > sh and gamer.nGamer > 1 and gamer.aCards.At(Min).CMast != gamer.aCards.At(Max).CMast
		if card:
			for mast in (card.CMast,app.CurrentGame%10):
				c = self.opt[corder] and gamer.aCards.MinCard(mast) or gamer.aCards.MaxCard(mast)
				if c:
					Min = gamer.aCards.IndexOf(c)
					Max = gamer.aCards.IndexOf(self.opt[corder] and gamer.aCards.MaxCard(mast) or gamer.aCards.MinCard(mast))
					mastUpDn = False
					break
		if hint:
			Val = gamer.aCards.IndexOf(hint)
			if Val < 0:
				Val = gamer.aCards.IndexOf(hint1)
			if Val < 0:
				Val = 0
		else:
			Val = Min+(Max-Min)/2
		counter = Tncounter(Val,Min,Max)
		def ctrl(key):
			if not self._keylock:
				if key == EKeyDownArrow:
					if out:
						self.retval = None
						counter.nValue = -1
					elif mastUpDn:
						mast = gamer.aCards.At(counter.nValue).CMast
						while gamer.aCards.At(counter.nValue).CMast == mast:
							counter.next()
					else:
						counter.next()
				elif key == EKeyUpArrow:
					if mastUpDn:
						mast = gamer.aCards.At(counter.nValue).CMast
						while gamer.aCards.At(counter.nValue).CMast == mast:
							counter.prev()
					else:
						counter.prev()
				elif key == EKeyRightArrow:
					counter.next()
				elif key == EKeyLeftArrow:
					counter.prev()
				elif key.startswith('mov'):
					counter.nValue = int(key[3:])
				elif key == EKeySelect:
					if out == 2:
						self.retval = False
					counter.nValue = -1
				lock.signal()
		self.handle['mov'] = ctrl
		if gamer.nGamer == 1:
			self.handle[EKeyLeftArrow] = lambda:ctrl(EKeyLeftArrow)
			self.handle[EKeyRightArrow] = lambda:ctrl(EKeyRightArrow)
			if out:
				self.handle[EKeyDownArrow] = lambda:ctrl(EKeyDownArrow)
		else:
			self.handle[EKeyUpArrow] = lambda:ctrl(EKeyUpArrow)
			self.handle[EKeyDownArrow] = lambda:ctrl(EKeyDownArrow)
			if mastUpDn:
				self.handle[EKeyLeftArrow] = lambda:ctrl(EKeyLeftArrow)
				self.handle[EKeyRightArrow] = lambda:ctrl(EKeyRightArrow)
		if self.opt[selkey] != 1:
			self.handle[EKeySelect] = lambda:ctrl(EKeySelect)
		if self.opt[selkey] > 0:
			self.handle[EKey5] = lambda:ctrl(EKeySelect)
		#x,y = 2,self.screen_size[1]-2
		self.blink = None
		self.StartBlink()
		while counter.nValue >= 0:
			self._keylock = True
			if out != 2:
				self.ShowHand(gamer,counter.nValue,hint=hint,hint1=hint1,counter=counter)
			else:
				#self.img.text((x,y),'ok',(0,255,0))
				#self.img.text((x,y),(self.opt[selkey] and ' 5' or 'ok'),(0,255,0))
				#self.DrawText(x,y,(self.opt[selkey] and ' 5' or 'ok'),'#00ff00','left','ok')
				#!self.ShowOk()
				self.redraw(())
			self.ShowOk()
			self._keylock = False
			lock.wait()
			if self.StopGame():
				break
		self.handle = {}
		#self.img.rectangle((x, y-10, x+15, y), fill=self.bg)
		self.c.delete('ok')
		self.StopBlink()
		return self.retval

	def About(self):
		(sw,sh) = self.screen_size
		self.c.delete('esc')
		text = 'PyPref'+ VERSION + "\n"
		if self.opt[lang]:
			text += "PyPref - это карточная игра преферанс, написанная на языке программирования Python. " 
			text += "Одно время PyPref существовал только в версии для смартфонов под управлением Symbian OS. "
			text += "Теперь эта версия игры доступна для Windows, а также на устройствах, где установлен Python с графической средой Tkinter.\n"
		else:
			text += "PyPref is a card game Preferans written in the Python programming language. "
			text += "For some time PyPref existed only in a version for Symbian OS smartphones. "
			text += "Now, this version of the game is also available for Windows and all devices where Python with Tkinter GUI is installed.\n"
		text += "\n* * *\nAuthor (version 2.0): Alexander aka amigo\namigo12@newmail.ru\nhttp://pypref.sf.net\n\nVersions 2.1-2.34: Vadim Zapletin\npreference.gixx@mail.ru\nhttps://python-pref.nethouse.ru"
		text = self.nls(text)
		id = self.c.create_text(sw/2,sh/2,font=self.font_norm,width=sw/3*2,text=text,fill='white',justify='center',tags='about')
		x1,y1,x2,y2 = self.c.bbox(id)
		pad = 10
		x1 -= pad
		y1 -= pad
		x2 += pad
		y2 += pad
		bg = '#005500'
		shadow = '#202020'
		id = self.c.create_rectangle((x1,y1,x2,y2),outline=bg,fill=bg,tags='about')
		self.c.tag_lower(id)
		id = self.c.create_rectangle((x1+2,y1+2,x2+2,y2+2),outline=shadow,fill=shadow,tags='about')
		self.c.tag_lower(id)
		self.HitReturn(anytap=True)
		self.c.delete('about')

	def ShowPaper(self,forcekey=None,load=None):
		def draw_text((x,y0,w1,w2,h,lo,ro),a,new):
			def ls(n,bold=None):
				if bold:
					return self.font_norm.measure(str(n)+'.')
					#return self.font_bold.measure(str(n)+'.')-3
				else:
					return self.font_norm.measure(str(n)+'.')
			y = y0+h
			w = w1
			y0 += 10
			s,ln = '',0
			flag = True
			for i in range(a.Count()-1,-1,-1):
				n = a.At(i)
				l = ls(n)
				if ln+l > w:
					if flag:
						arr = s.split('.')
						if len(arr) >= 2:
							last = arr[-2]
							if len(arr) > 2:
								prev = '.'.join(arr[:-2])+'.'
								#self.img.text((x,y), unicode(prev), '#0000ff', font='LatinPlain12')
								self.DrawText(x,y,prev,'#0000ff',tag='pul',fnt='norm')
							#self.img.text((x+ln-ls(last),y), unicode(last+'.'),(not new and '#0000ff' or 0),font='LatinBold12')
							self.DrawText(x+ln-ls(last,1),y, str(last)+'.',(not new and '#0000ff' or 'black'),tag='pul')
							flag = False
					else:
						#self.img.text((x,y), unicode(s), '#0000ff', font='LatinPlain12')
						self.DrawText(x,y,s,'#0000ff',tag='pul',fnt='norm')
					#y -= 12
					y -= self.font_bheight-2
					if y <= y0:
						break
					x -= lo
					w += lo+ro
					if w > w2:
						w = w2
						x += lo
					s,ln = (str(n)+'.'),l
				else:
					s = str(n)+'.'+s
					ln += l
			if y > y0:
				if flag:
					arr = s.split('.')
					if len(arr) >= 2:
						last = arr[-2]
						if len(arr) > 2:
							prev = '.'.join(arr[:-2])+'.'
							#self.img.text((x,y), unicode(prev), '#0000ff', font='LatinPlain12')
							self.DrawText(x,y,prev,'#0000ff',tag='pul',fnt='norm')
						#self.img.text((x+ln-ls(last),y), unicode(last+'.'),(not new and '#0000ff' or 0),font='LatinBold12')
						self.DrawText(x+ln-ls(last,1),y, str(last)+'.',(not new and '#0000ff' or 'black'),tag='pul')
						flag = False
				else:
					#self.img.text((x,y), unicode(s), '#0000ff', font='LatinPlain12')
					self.DrawText(x,y,s,'#0000ff',tag='pul',fnt='norm')
		#tmp = Image.new(self.img.size)
		#tmp.blit(self.img)
		self.c.delete('pop')
		self.c.delete('esc')
		pul_size = self.size == 'small' and (220,240) or (400,440)
		if self.paper is None:
			#self.paper,self.score = MakePaper(self.img.size)
			self.paper,self.score = MakePaper(pul_size)
		#self.img.clear()
		lincolor = '#909090'
		txtcolor = '#0000ff'
		self.c.create_rectangle((0,0, pul_size[0],pul_size[1]),outline='black',fill='white',tags='pul')
		for coords in self.paper[0]:
			self.c.create_line(coords,fill=lincolor,tags='pul')
		self.c.create_oval(self.paper[1],outline=lincolor,fill='#ffffff',tags='pul')
		#self.img.text(self.paper[2],unicode(str(app.nBulletScore)),txtcolor,font='LatinBold12')
		#x,y = self.paper[2]
		x = pul_size[0]/2
		y = pul_size[1]-x
		self.DrawText(x,y,str(app.nBulletScore),txtcolor,'center',tag='pul',an='center')
		for i in (1,2,3):
			score = app.Gamer(i).aScore
			draw_text(self.score[i][0],score.Bullet,score.New[0])
			draw_text(self.score[i][1],score.Mountan,score.New[1])
			draw_text(self.score[i][2],score.LeftVists,score.New[2])
			draw_text(self.score[i][3],score.RightVists,score.New[3])
		sw2 = pul_size[0]/2
		r = sw2/2-10
		#self.c.create_oval((sw2-r,-r,sw2+r,r),outline=lincolor,fill='#ffff80',tags='pul')
		self.c.create_arc((sw2-r,-r,sw2+r,r),start=0,extent=-180,outline=lincolor,fill='#ffff80',tags='pul')
		for i in (1,2,3):
			vists = app.Gamer(i).aScore.Vists
			#c = i == 1 and (sw2-r/3,r-5) or (i == 2 and (sw2-r+5,11) or (sw2+7,11))
			#lv = len(str(vists))*7
			#c = i == 1 and (sw2-int(lv/2),r-5) or (i == 2 and (sw2-r+5,11) or (sw2+r-2-lv,11))
			#self.img.text(c,unicode(vists),vists < 0 and (150,0,0) or (0,150,0))
			if i == 1:
				x,y,jst = sw2, r-3, 'center'
			elif i == 2:
				x,y,jst = sw2-r+3, self.font_bheight, 'left'
			else:
				x,y,jst = sw2+r-3, self.font_bheight, 'right'
			self.DrawText(x,y,vists,(vists < 0 and '#990000' or '#009900'),jst,tag='pul')
		if forcekey or not(app.mode == demo or self.opt[wait]):
#			x,y = 0,self.img.size[1]
#			self.img.rectangle((x,y-10,x+15,y),fill='#ffffff')
#			#self.img.text((x+1,y-1),'ok',0xb0b0b0)
#			self.img.text((x+1,y-1),(self.opt[selkey] and ' 5' or 'ok'),'#b0b0b0')
			pass
		dx,dy = (self.screen_size[0]-pul_size[0])/2,(self.screen_size[1]-pul_size[1])/2
		self.c.move('pul',dx,dy)
		self.redraw(())
		#self.HitReturn(ok=False,forcekey=forcekey)
		self.query = True
		self.HitReturn(forcekey=forcekey,anytap=(not load))
		retval = None
		#if load:
		#	retval = not self.PopUp(('Yes','No'), 'Load Game')
		if load and self.query:
			retval = True
		self.query = None
		#self.img.blit(tmp)
		#tmp = None
		self.c.delete('pul')
		self.redraw(())
		return retval

	def Query(self,title,default):
		(sw,sh) = self.screen_size
		x,y = sw/2,sh/2
		self.Clear()
		text = self.nls(title) + ':  ' + str(default)
		#self.DrawText(x,y,text,'#ffffff','center',tag='lim',an='center')
		self.DrawText(x,y,'','#ffffff','center',tag='lim',an='center')
		#xc = x+self.font_bold.measure(text)/2+20
		xc = x+self.font_bold.measure(text)/2+25
		yc = y+(self.size == 'big' and 30 or 18)/2
		self.ShowJoy(xc,yc)
		self.retval = default
		save_handle = self.handle
		self.handle = {}
		def ctrl(key):
			if key == EKeyUpArrow:
				self.retval += 10
			elif key == EKeyDownArrow:
				self.retval -= 10
			elif key == EKeyLeftArrow:
				self.retval -= 1
			elif key == EKeyRightArrow:
				self.retval += 1
			else:
				self.query = False
			if self.retval < 1:
				self.retval = 1
			lock.signal()
		self.handle[EKeyRightArrow] = lambda:ctrl(EKeyRightArrow)
		self.handle[EKeyUpArrow] = lambda:ctrl(EKeyUpArrow)
		self.handle[EKeyLeftArrow] = lambda:ctrl(EKeyLeftArrow)
		self.handle[EKeyDownArrow] = lambda:ctrl(EKeyDownArrow)
		self.handle[EKeySelect] = lambda:ctrl(EKeySelect)
		if self.opt[selkey] > 0:
			self.handle[EKey5] = lambda:ctrl(EKeySelect)
		self.query = True
		while self.query:
			text = self.nls(title) + ':  ' + str(self.retval)
			self.c.itemconfig('lim',text=text)
			self.redraw(())
			lock.wait()
		self.handle = save_handle
		return self.retval

	def StopGame(self):
		if app.mode == halt:
			return True
		if app.mode != stop:
			return False
		if self.wince:
			list = ('Continue','Save game','Score','Settings','Exit game','Hide')
		else:
			list = ('Continue','Save game','Score','Settings','Exit game')
		while True:
			i = self.PopUp(list, 'Game paused')
			if i == 0:
				break
			elif i == 1:
				self.SaveGame()
#			elif i == 2:
#				app.mode = run
#				self.ShowPaper(forcekey=True)
#				if app.mode == halt:
#					return True
#				self.ShowOk()
			elif i == 2:
                                app.mode = run # <- fake HitReturn()
                                anytap = self.anytap
                                self.ShowPaper(forcekey=True)                                
                                self.ShowOk()			
                                app.mode = stop
                                self.anytap = anytap                                
			elif i == 3:
				self.Options()				
			elif i == 4:
				if self.YesOrNot('Are you sure'):
					app.mode = halt
					return True
				else:
					break
			else:
				FullScreenOff()
				break
		app.mode = run		
		return False

	def YesOrNot(self,answer):
		list = ('Yes','No')
		while True:
			i = self.PopUp(list, answer)
			if i == 0:
				return True
			return False

	def AskOpen(self):
		if app.mode == demo:
			return True
		return self.YesOrNot('Open cards')

	def Options(self,idx=None,change=None):
		if idx is None:
			if self.wince:
				opts = ('Language','Game','Interface','Backlight','Back')
				oids = (lang,101,102,lighton,-1)
			elif app.mode == halt:
				opts = ('Language','Game','Interface','Orientation','Back')
				oids = (lang,101,102,lighton,-1)
			else:
				opts = ('Language','Game','Interface','Back')
				oids = (lang,101,102,-1)
			#disable = not have_miso and 1 or None
			self.pos = 0
			while gui.PopUp(opts, 'Settings', gui.Options, self.pos, None, optids=oids) < 0:
				pass
			f = open(CONFIG_FILE,'wt')
			f.write(repr(self.opt))
			f.close()
			return
		if change:
			if idx == 101:                                                                        
                                #opts = ('Hints','Level','Whists','Pass game','Type game','Back')
                                opts = ('Common','Whists','Pass game','Hints','Back')
                                self.pos = 0
                                while gui.PopUp(opts, 'Game', gui.Options, self.pos, optids=(111,112,113,114,-1)) < 0:
                                        pass
                                self.pos = 1
                                return                              
			if idx == 111:                              
                                opts = ('Score rules','Without 3','10 tricks','Stalingrad','Left level','Right level','Back')
                                gui.PopUp(opts, 'Common', gui.Options, optids=(scorerules,without3,check10,stalingrad,leftlvl,rightlvl,-1), w=160, ow=41)
                                self.pos = 0
                                return
			if idx == 112:
				#opts = ('Greedy whist','Semiresponsible','HalfWhist','Pass-Pass-Whist','Back')
				opts = ('Greedy','Responsible','HalfWhist','Pass-Pass-Whist','Back')
				gui.PopUp(opts, 'Whist', gui.Options, optids=(greedywhist,responsible,halfwhist,whistpas,-1), w=160)
				self.pos = 1
				return
			if idx == 113:
				opts = ('Progression','Game for exit','Exit on lost','Open talon','Back')
				gui.PopUp(opts, 'Pass game', gui.Options, optids=(pasprogress,pasexit,lostexit,pastalon,-1), w=160, ow=38)
				self.pos = 2
				return
			if idx == 114:
				opts = ('Hint lead','Hint bid','Hint discard','Back')
				gui.PopUp(opts, 'Hints', gui.Options, optids=(hintcard,hintgame,hintdiscard,-1), w=160)
				self.pos = 3
				return
			if idx == 102:
				opts = ('Timeout','Selection Key','Cards order','Suits order','Back')
				gui.PopUp(opts, 'Interface', gui.Options, optids=(wait,selkey,corder,sorder,-1), w=160)
				self.pos = 2
				return
			if self.opt[idx] is None:
				return None
			elif idx == selkey:                                
                                self.opt[idx] += 1
                                if self.opt[idx] > 2:
                                        self.opt[idx] = 0
			elif idx == pasexit or idx == scorerules:
                                if app.mode == stop:
                                        self.opt[idx]
                                else:
                                        self.opt[idx] += 1
                                        if self.opt[idx] > 2:
                                                self.opt[idx] = 0
			elif idx == leftlvl or idx == rightlvl:
                                if app.mode == stop:
                                        self.opt[idx]
                                else:
                                        self.opt[idx] += 1
                                        if self.opt[idx] > 3:
                                                self.opt[idx] = 0
			elif idx == pasprogress:
                                if app.mode == stop:
                                        self.opt[idx]
                                else:
                                        self.opt[idx] += 1
                                        if self.opt[idx] > 4:
                                                self.opt[idx] = 0
			elif idx > 0:
                                if app.mode == stop and (idx == without3 or idx == check10 or idx == stalingrad or idx == greedywhist or idx == responsible or idx == halfwhist or idx == whistpas or idx == lostexit or idx == pastalon):
                                        self.opt[idx]
                                else:
                                        self.opt[idx] = 1 - self.opt[idx]
                                        if idx == lang:
                                                self.pos = 0
                                                return None
                                        if idx == lighton and not self.wince:
                                                (sw,sh) = self.screen_size
                                                self.screen_size = (sh,sw)
                                                self.c.configure(width=sh,height=sw)
                                                self.pos = 3
                                                return None                                                                                                 
			else:
				self.opt[idx] += 1
				if self.opt[idx] > 5:
					self.opt[idx] = 0
			return 1
		if idx > 100 or self.opt[idx] is None:
			return ''
		elif idx == lang:
			return self.nls(self.opt[idx] and 'ru' or 'en')
		elif idx == corder:
			return self.nls(self.opt[idx] and '7..A' or 'A..7')
		elif idx == sorder:
			return self.nls(self.opt[idx] and '1234' or '1324')
		elif idx == selkey:
			return self.nls(self.opt[idx] == 2 and 'ok,5' or (self.opt[idx] and '5' or 'ok'))
		elif idx == lighton:
			if self.wince:
				return self.nls(self.opt[idx] and 'On' or 'Auto')
			else:
				return self.nls(self.opt[idx] and 'Landscape' or 'Portrait')
		elif idx == leftlvl or idx == rightlvl:
			#app.Gamer(idx == leftlvl and 2 or 3).level = self.opt[idx]
			#app.Gamer(1).level = max(app.Gamer(2).level,app.Gamer(3).level)
			app.Setup()
			#list = ('low','med','hight')
			#list = ('*','**','***','****')
			list = ('\x95','\x95\x95','\x95\x95\x95','\x95\x95\x95\x95')
			return self.nls(list[self.opt[idx]])
		elif idx == pasprogress:
			list = ('x1111','x1233','x1234..','x1244','x1248..')
			return self.nls(list[self.opt[idx]])
		elif idx == pasexit:
			list = ('6666','6777','6788')
			return self.nls(list[self.opt[idx]])
		elif idx == scorerules:       
                        self.DefaultOpt(self.opt[idx])
                        app.Setup()
                        list = ('Sochi','Leningrad','Rostov')
                        return self.nls(list[self.opt[idx]])
		elif idx == check10:
                        return self.nls(self.opt[idx] and 'Checked' or 'Whisted')
		elif idx > 0:
			if idx == greedywhist:
				app.Setup()
			return self.nls(self.opt[idx] and 'Yes' or 'No')
		else:
			#return self.opt[idx] and (unicode(str(self.opt[idx])) + self.nls('sec')) or self.nls('Key')
			return self.opt[idx] and (self.nls(str(self.opt[idx])+' ') + self.nls('sec')) or self.nls('Till push')

	def PopUp(self,list,title,opt=None,pos=0,disable=None,optids=None,w=120,ow=32):
		(sw,sh) = self.screen_size
		#lh = 20
		w,xoff = self.size == 'big' and (350,15) or (200,10)
		lh = self.font_bheight+2
		h = (len(list)+1)*lh
		x = (sw-w)/2
		y = (sh-h)/2
		#bg = (0,80,0)
		bg = '#005500'
		tcolor = '#ffffff'
		ocolor = '#ffff00'
		shadow = '#202020'
		#tmp = Image.new((sw,sh))
		#tmp.blit(self.img)
		#self.Clear()
		#self.img.rectangle((x-1,y-1, x+w+1,y+h+1),0xffffff)
		self.c.delete('pop')
		self.c.delete('esc')
		self.c.create_rectangle((x+2,y+2, x+w+2,y+h+2),outline=shadow,fill=shadow,tags='pop')
		self.c.create_rectangle((x,y, x+w,y+h),outline=bg,fill=bg,tags='pop')
		self.c.create_rectangle((x,y, x+w,y+lh),outline=bg,fill=tcolor,tags='pop')
		self.DrawText(x+w/2,y+lh,title,bg,'center','pop')
		#self.img.text((x+3,y+lh-4),self.nls(title),bg)
		off = lh
		i = 0
		for txt in list:
			off += lh
			color = i == disable and self.bg or tcolor
			#self.img.text((x+15,y+off),self.nls(txt),color)
			#self.DrawText(x+15,y+off,txt,color,'left',('pop','pop'+str(i)))
			self.c.create_rectangle((x+1,y+off-lh, x+w-1,y+off),outline=bg,fill=bg,tags=('pop','box'+str(i)))
			#self.DrawText(x+5,y+off,txt,color,'left',('pop','pop'+str(i)))
			self.DrawText(x+xoff,y+off,txt,color,'left',('pop','pop'+str(i)))
			if opt:
				#self.img.text((x+(w-ow),y+off),opt(optids[i]),ocolor)
				#self.DrawText(x+w,y+off,opt(optids[i]),ocolor,'right',('pop','opt'+str(i)),False)
				self.DrawText(x+w-5,y+off,opt(optids[i]),ocolor,'right',('pop','opt'+str(i)),False)
			i += 1
		#lock = e32.Ao_lock()
		#local_lock = Lock()
		counter = Tncounter(pos,0,len(list)-1)
		save_handle = self.handle
		self.handle = {}
		def ctrl(key):
			while True:
				if key == EKeyUpArrow:
					counter.prev()
				elif key == EKeyDownArrow:
					counter.next()
				elif key.startswith('pop') or key.startswith('opt') or key.startswith('box'):
					idx = int(key[3:])
					if idx != disable:
						counter.nValue = idx
						#print 'counter',counter.nValue
				else:
					prev_lng = self.opt[lang]
					prev_ori = self.opt[landscape]
					if opt is None or opt(optids[counter.nValue],True) is None:
						#counter.nValue = ((prev != self.opt[lang] or opt and optids[counter.nValue] > 100) and -2 or -1)
						counter.nValue = ((prev_lng != self.opt[lang] or not self.wince and prev_ori != self.opt[landscape] or opt and optids[counter.nValue] > 100) and -2 or -1)
				if counter.nValue != disable:
					break
			popup_lock.signal()
		self.handle['pop'] = ctrl
		self.handle[EKeyUpArrow] = lambda:ctrl(EKeyUpArrow)
		self.handle[EKeyDownArrow] = lambda:ctrl(EKeyDownArrow)
		self.handle[EKeySelect] = lambda:ctrl(EKeySelect)
		if self.opt[selkey] > 0:
			self.handle[EKey5] = lambda:ctrl(EKeySelect)
		#marker = Image.new((8,10))
		#marker.clear(tcolor)
		prev = counter.nValue
		while counter.nValue >= 0:
			cur = counter.nValue
			#off = 35+cur*lh
			off = lh*2 + cur*lh
			#self.img.rectangle((x,y+lh, x+10,y+h),bg,bg)
			#self.img.blit(marker,target=(x+3,y+off-9),mask=self.masts[cur%4+1])
			self.c.delete('marker')
			#self.DrawText(x+3,y+off,'*',tcolor,'left',('pop','marker'))
			self.DrawText(x+(xoff/2),y+off-2,'\x95',tcolor,'center',('pop','marker'))
#box			self.c.itemconfig('box'+str(prev),fill=bg)
#box			#self.c.itemconfig('box'+str(cur),fill='#007700')
#box			self.c.itemconfig('box'+str(cur),fill='#004400')
			prev = cur
			if opt:
				#self.img.rectangle((x+(w-ow),y+off-15, x+w,y+off+2),bg,bg)
				#self.img.text((x+(w-ow),y+off),opt(optids[cur]),ocolor)
				self.c.itemconfig('opt'+str(cur),text=opt(optids[cur]))
			self.redraw(())
			popup_lock.wait()
		self.handle = save_handle
		#self.img.blit(tmp)
		#tmp = None
		self.c.delete('pop')
		self.redraw(())
		self.ShowEsc()
		if counter.nValue == -2:
			return -1
		return cur

	def LoadGame(self):
		list = []
		for i in ('',1,2,3,4,5):
			try:
				t = os.stat(SAVE_FILE%i)[8]
				d = time.ctime(t).split()
				t = d[3].split(':')
				list.append(unicode("%s %s %s:%s"%(d[1],d[2],t[0],t[1])))
			except:
				list.append('-')
		#list.append(self.nls('Back'))
		list.append('Back')
		i = 0
		while True:
			i = gui.PopUp(list, 'Load Game',pos=i)
			if i > 5:
				return False
			try:
				f = open(SAVE_FILE % (i or ''))
				app.nBulletScore = int(eval(f.readline().rstrip()))
				app.nCurrentStart.nValue = int(eval(f.readline().rstrip()))
				for j in (1,2,3):
					score = app.Gamer(j).aScore
					score.Bullet.Set(eval(f.readline().rstrip()))
					score.Mountan.Set(eval(f.readline().rstrip()))
					score.LeftVists.Set(eval(f.readline().rstrip()))
					score.RightVists.Set(eval(f.readline().rstrip()))
				f.close()
				app.CloseBullet()
				if self.ShowPaper(load=True):
					return True
			except:
				pass

	def SaveGame(self):
		list = []
		for i in ('',1,2,3,4,5):
			try:
				t = os.stat(SAVE_FILE%i)[8]
				d = time.ctime(t).split()
				t = d[3].split(':')
				list.append(unicode("%s %s %s:%s"%(d[1],d[2],t[0],t[1])))
			except:
				list.append('-')
		#list.append(self.nls('Back'))
		list.append('Back')
		i = gui.PopUp(list, 'Save game')
		if i <= 5:
			try:
				f = open(SAVE_FILE % (i or ''),'wt')
				f.write(repr(app.nBulletScore)+"\n")
				f.write(repr(app.nCurrentStart.nValue)+"\n")
				for i in (1,2,3):
					score = app.Gamer(i).aScore
					f.write(repr(score.Bullet)+"\n")
					f.write(repr(score.Mountan)+"\n")
					f.write(repr(score.LeftVists)+"\n")
					f.write(repr(score.RightVists)+"\n")
				f.close()
			except:
				pass

	def ShowScore(self,mode=None):
		(sw,sh) = self.screen_size
		self.Clear()
		sz = self.size == 'small' and 40 or 80
		pause = False
		for i in (1,2,3):
			score = app.Gamer(i).aScore.Vists
			if score:
				pause = True
				if i == 1:
					x,y = (sw-sz)/2,sh-sz
					tx,ty,jst = sw/2,y-5,'center'
				elif i == 2:
					x,y = 0,0
					tx,ty,jst = sz+5,sz+5+self.font_bheight,'left'
				else:
					x,y = sw-sz,0
					tx,ty,jst = sw-sz-5,sz+5+self.font_bheight,'right'
				self.DrawMoney(x,y,score)
				#self.img.text((tx,ty),unicode(str(score)),(score < 0 and (255,20,20) or (255,255,255)))
				self.DrawText(tx,ty,score,(score < 0 and '#ff2020' or 'white'),jst)
				self.redraw(())
		if pause:
			if mode == demo:
				tk.after(2000)
			else:
				self.HitReturn(forcekey=True)

	def DrawMoney(self,x,y,score):
                TPlScore.rcnt = 0
		TPlScore.rprg = 0
		self.c.delete('esc')
		sz,d = self.size == 'small' and (40,10) or (80,20)
		if score > 0:
                        if score < 450:
                                n = int(score/10) + 1
                        else:
                                n = 45
			for i in range(0,n):
				xo = random.randint(0,sz-d)
				yo = random.randint(0,sz-d)
				#self.img.ellipse((x+xo,y+yo, x+xo+d,y+yo+d),(100,100,100),fill=(255,255,0))
				self.c.create_oval((x+xo,y+yo, x+xo+d,y+yo+d),outline='#606060',fill='#ffff00')
				#self.redraw(())
				tk.update_idletasks()
				if not self.wince:
					tk.after(100)

	def nls(self,txt):
		txt = str(txt)
		if self.opt[lang] and self.messages.get(txt):
			txt = self.messages[txt]
		return txt.decode('cp1251').encode('utf-8')

	def keypress(self,key):
		handler = self.handle.get(key)
		if handler:
			handler()

	def click(self,e):
		#print e.x, e.y
#		if self.anytap:
#			self.keypress(EKeySelect)
#			return
		c = self.c
		ids = c.find_overlapping(e.x,e.y,e.x,e.y)
		#print 'overlapping',ids
		if not len(ids):
			if self.anytap:
				self.keypress(EKeySelect)
			return
		id = ids[-1]
		tags = c.gettags(id)
		#print tags, self.anytap
		if 'esc' in tags:
			#c.event_generate('<Escape>')
			exit_handler()
		elif 'ok' in tags:
			#c.event_generate('<Return>')
			self.keypress(EKeySelect)
		elif 'pop' in tags:
			if len(tags) > 2:
				self.handle['pop'](tags[1])
				tk.after(200,lambda:self.keypress(EKeySelect))
		elif self.anytap:
			self.keypress(EKeySelect)
		elif 'joy' in tags:
			(x1,y1,x2,y2) = c.bbox('joybox')
			#print c.bbox('joybox')
			if e.x <= x1:
				self.keypress(EKeyLeftArrow)
			elif e.x >= x2:
				self.keypress(EKeyRightArrow)
			elif e.y <= y1:
				self.keypress(EKeyUpArrow)
			elif e.y >= y2:
				self.keypress(EKeyDownArrow)
		elif 'card' in tags:
			if tags[1] == 'movok':
				self.keypress(EKeySelect)
			elif self.handle.has_key('mov'):
				self.handle['mov'](tags[1])
		elif 'out' in tags:
			self.keypress(EKeyDownArrow)

	def redraw(self,rect):
		self.c.update()

	def sleep(self,interval):
		self.c.update()
		if app.mode != halt:
			tk.after(int(interval*1000),sleep_lock.signal)
			sleep_lock.wait()
			self.c.update()


	def Run(self):
		self.LoadCards()
		list = ('New Game','Load Game','Settings','Demo','About','Exit')
		#list = ('New Game','Load Game','Settings','Demo','About','Exit','Hide')
		while True:
			self.Clear()
			i = self.PopUp(list, 'Python Pref')
			if i == 0:
				app.nBulletScore = self.Query('Game limit', 21)
				if app.nBulletScore > 0:
					app.RunGame()
					self.ShowScore()
			elif i == 1:
				if self.LoadGame():
					#self.ShowPaper()
					app.RunGame(loaded=True)
					self.ShowScore()
			elif i == 2:
				self.Options()
			elif i == 3:
				app.nBulletScore = 21
				app.RunGame(demo)
				self.ShowScore(demo)
			elif i == 4:
				self.About()
			elif i == 5:
				break
			#else:
			#	FullScreenOff()
		if self.wince:
			cwin.destroy()
		self.c.destroy()
		tk.quit()

if __name__ == '__main__':

	tk = Tk()
	size = tk.maxsize()
	tk.title('Python Pref')
	#tk.overrideredirect(1)
	c = Canvas(tk)
	c.pack()
	if os.name == 'ce':
		cwin = c
		cwin.configure(width=size[0], height=size[1], bg='black')
		tk.geometry('+0+0')
		tk.update()
		desk = Toplevel()
		desk.overrideredirect(1)
		c = Canvas(desk)
		c.pack()
		c.bind('<FocusOut>',FullScreenOff)
		hwnd = GetActiveWindow()
		gui = PrefGUI(c,size)
		cwin.bind('<Expose>', lambda e: cwin.focus_set())
		cwin.bind('<Key>', lambda e: gui.keypress(e.keysym))
		cwin.bind('<1>', gui.click)
		FullScreenOn()
		DoNotSleep()
	else:
		gui = PrefGUI(c,size)

	app = TDeskTop(gui)
	lock = Lock()
	popup_lock = Lock()
	sleep_lock = Lock()

	def exit_handler(e=None):
		#print 'exit_handler'
		if app.mode == demo:
			app.mode = halt
		elif app.mode == halt and gui.query:
			gui.retval = -1
			gui.query = False
		elif app.mode == run:
			app.mode = stop
		lock.signal()
		popup_lock.signal()
		sleep_lock.signal()

	gui.c.bind('<Escape>', exit_handler)

	tk.after(10,gui.Run)

	#print 'Wait'
	tk.mainloop()
	#print 'Real Exit'
