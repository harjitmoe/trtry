#!/usr/bin/python -i

# Three or more matching in a row or column constitute a match

# Matches only self, not overwritable
normtiles=["red.gif","green.gif","blue.gif","yellow.gif","magenta.gif","cyan.gif"]

# Matches all, not overwritable.  Should be about one in ten occurance where there
# are six normal tiles.
wildcard="wild.gif"

# Matches not even self, not overwritable.  One in 50? 100? 400 occurance.
dunce="dunce.gif"

# Matches not even self, only overwritable tile, initial state, matches become 
# this.
# When the shape of the piece to put down does not appear at any orientation in 
# this tile, all of these tiles are replaced by dunces and game ends.
# When there are none of these for any reason, game ends.
bg="bg.gif"

width=9
height=9

from tkinter import *
from Canvas import *

try:
	from ImageTk import *
except ImportError:
	pass

root=Tk()
rootc=Canvas(root,width=16*width+3+7+16+16+16,height=16*height+6+13)
rootc.pack(expand=1,fill=BOTH)

for n,v in enumerate(normtiles):
	normtiles[n]=PhotoImage(file=v)

wildcard=PhotoImage(file=wildcard)
dunce=PhotoImage(file=dunce)
bg=PhotoImage(file=bg)

canvasf=Frame(rootc,border=1,relief=RAISED)
canvas=Canvas(canvasf,width=16*width,height=16*height)
canvas.pack(expand=1,fill=BOTH)
canvasW=Window(rootc,0,0,anchor=NW,window=canvasf)

import os
if os.path.exists("undercoat.gif"):
        undergrid=[]
        undercoat=PhotoImage(file="undercoat.gif")
        for i in range(width):
                line=[]
                for j in range(height):
                	line.append(ImageItem(canvas,i*16,j*16,anchor=NW,image=undercoat))
                undergrid.append(line)
        del line

grid=[]
for i in range(width):
	line=[]
	for j in range(height):
		line.append(ImageItem(canvas,i*16,j*16,anchor=NW,image=bg))
	grid.append(line)
del line

mask=PhotoImage(file="mask.gif")
nomask=PhotoImage(file="nomask.gif")
fade1=PhotoImage(file="fadeout_first.gif")
fade2=PhotoImage(file="fadeout_last.gif")

grid_mask=[]
for i in range(width):
	line=[]
	for j in range(height):
		line.append(ImageItem(canvas,i*16,j*16,anchor=NW,image=nomask))
		#NB Cyclic reference for convenience - but if using on pre-gc or gc-less Python consider removing maskee
		grid[i][j].masker=line[-1]
		line[-1].maskee=grid[i][j]
	grid_mask.append(line)
del line

def matching(a,b):
	a=str(a["image"])
	b=str(b["image"])
	if str(bg) in (a,b):
		return 0
	if str(dunce) in (a,b):
		return 0
	if str(wildcard) in (a,b):
		return 1
	return a==b

try:
	Set=set
except NameError:
	from sets import Set

def _matches_in_row(row):
	i=j=k=None
	ms=Set()
	for cell in row:
		if not i:
			i=cell
		elif not j:
			j=cell
		else:
			k=cell
			#All three conditions needed due to wildcards
			if matching(i,j) and matching(j,k) and matching(i,k):
				ms.update(Set([i,j,k]))
			i,j=j,k
	return ms

def matches():
	ms=Set()
	for row in grid:
		ms.update(_matches_in_row(row))
	for col in zip(*grid):
		ms.update(_matches_in_row(col))
	return list(ms)

def match_op():
	matches_l=matches()
	num_got=len(matches_l)
	import math
	points_got=int(math.floor(math.exp(num_got-2)+0.5))*5
	import time
	for i in matches_l:
		i.masker["image"]=fade1
	root.update()
	time.sleep(0.05)
	for i in matches_l:
		i.masker["image"]=fade2
	root.update()
	time.sleep(0.05)
	for i in matches_l:
		i["image"]=bg
		i.masker["image"]=nomask
	global score
	score+=points_got
	scoreL["text"]=score

from random import random
from random import choice as rchoice

def genrand():
	n=random()
	if n<=0.1:
		return wildcard
	elif n<=0.1025:
		return dunce
	else:
		return rchoice(normtiles)

def randtrio():
	return genrand(),genrand(),genrand()

class Box(Frame):
	def __init__(self,mastr,sq,*a,**k):
		self.highlight=0
		Frame.__init__(self,mastr,border=0,*a,**k)
		self.ca=Canvas(master=self,border=0,width=48,height=48)
		self.ca.pack(expand=1,fill=BOTH)
		self.l=ImageItem(self.ca, 0,16, anchor=NW)
		self.t=ImageItem(self.ca, 16,0, anchor=NW)
		self.c=ImageItem(self.ca, 16,16, anchor=NW)
		self.b=ImageItem(self.ca, 16,32, anchor=NW)
		self.r=ImageItem(self.ca, 32,16, anchor=NW)
		self.seq=sq
	def setup(self):
		self.c["image"]=self.seq[1]
		if self.orient in "<>":
			self.t["image"]=self.b["image"]=""
			if self.orient=="<":
				self.l["image"]=self.seq[0]
				self.r["image"]=self.seq[2]
			else:
				self.l["image"]=self.seq[2]
				self.r["image"]=self.seq[0]
		else:
			self.l["image"]=self.r["image"]=""
			if self.orient=="^":
				self.t["image"]=self.seq[0]
				self.b["image"]=self.seq[2]
			else:
				self.t["image"]=self.seq[2]
				self.b["image"]=self.seq[0]
		if self.highlight:
			self.set_highlight()
	def set_highlight(self):
		if hasattr(self,"curhlt"):
			for i,j in self.curhlt:
				grid_mask[i][j]["image"]=nomask
		i,j=self.curpt
		self.curhlt=[self.curpt]
		grid_mask[i][j]["image"]=mask
		if self.orient in "<>":
			grid_mask[i-1][j]["image"]=mask
			self.curhlt.append((i-1,j))
			grid_mask[i+1][j]["image"]=mask
			self.curhlt.append((i+1,j))
		else:
			grid_mask[i][j-1]["image"]=mask
			self.curhlt.append((i,j-1))
			grid_mask[i][j+1]["image"]=mask
			self.curhlt.append((i,j+1))
	def turn(self,evt=None):
		save_orient=self.orient
		try:
			self.orient={"<":"^", "^":">", ">":"V", "V":"<"}[self.orient]
		except IndexError:
			pass #Won't validate in step below so keep calm
		if not self.coords_validate(*self.curpt):
			self.orient=save_orient
	def __setattr__(self,n,v):
		self.__dict__[n]=v
		if n=="seq":
			self.orient="<" #NB Triggers the below
		elif n=="orient":
			self.setup()
		elif n=="highlight" and v:
			self.curpt=(1,1) #NB Triggers the below
		elif n=="curpt":
			self.set_highlight()
	def left(self,event=None):
		x,y=self.curpt
		x-=1
		if not self.coords_validate(x,y):
			return
		self.curpt=x,y
	def right(self,event=None):
		x,y=self.curpt
		x+=1
		if not self.coords_validate(x,y):
			return
		self.curpt=x,y
	def up(self,event=None):
		x,y=self.curpt
		y-=1
		if not self.coords_validate(x,y):
			return
		self.curpt=x,y
	def down(self,event=None):
		x,y=self.curpt
		y+=1
		if not self.coords_validate(x,y):
			return
		self.curpt=x,y
	def coords_validate(self,x,y):
		if x<0 or x>(width-1):
			return 0
		if y<0 or y>(height-1):
			return 0
		if self.orient in "<>" and (x<1 or x>(width-2)):
			return 0
		if self.orient in "^V" and (y<1 or y>(height-2)):
			return 0
		return 1
	def drop(self,event=None):
		if hasattr(self,"curhlt"):
			b,a,c=self.curhlt #Constants regardless of orient, then orient-dependants
			if self.orient in ">V": #Thin end is first: reverse order here
				c,a=a,c
			for x,y in (a,b,c):
				if str(grid[x][y]["image"])!=str(bg):
					return
			for i,j in self.curhlt:
				grid_mask[i][j]["image"]=nomask
			grid[a[0]][a[1]]["image"]=self.seq[0]
			grid[b[0]][b[1]]["image"]=self.seq[1]
			grid[c[0]][c[1]]["image"]=self.seq[2]
			match_op()
			#TODO: Duncing out on game over
			topbox.highlight=1 #Resets, see __setattr__
			topbox.seq=midbox.seq
			midbox.seq=basebox.seq
			basebox.seq=randtrio()
		elif not self.highlight:
			raise TypeError("trying to drop a trio without an associated highlight area")
		else:
			raise SystemError("set to highlight but no current highlight")

topbox=Box(rootc,randtrio())
topbox.highlight=1
topboxW=Window(rootc,16*width+3+7,0,anchor=NW,window=topbox)

midbox=Box(rootc,randtrio())
midboxW=Window(rootc,16*width+3+7,16*3,anchor=NW,window=midbox)

basebox=Box(rootc,randtrio())
baseboxW=Window(rootc,16*width+3+7,16*6,anchor=NW,window=basebox)

score=0
scoreL=Label(rootc,text=score)
scoreW=Window(rootc,(16*width+3)/2,16*height+6,anchor=N,window=scoreL)

root.bind("<Key-space>",topbox.turn)
root.bind("<Key-Left>",topbox.left)
root.bind("<Key-Right>",topbox.right)
root.bind("<Key-Up>",topbox.up)
root.bind("<Key-Down>",topbox.down)
root.bind("<Key-Return>",topbox.drop)

root.title("TriTryst (My Version)")
root.focus_force()

#This seems to be a better mainloop construct from IDLE perspective
while 1:
	try:
		root.update()
	except TclError:
		break
