import socket
import _thread
import time
import youtube_dl
from bs4 import BeautifulSoup
import urllib.request
import pyaudio  
import wave  

# create an INET, STREAMing socket
serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# bind the socket to a public host, and a well-known port
serversocket.bind((socket.gethostname(), 8000))
# become a server socket
serversocket.listen(5)

## MAKE VARIABLES FOR IMP STUFF
playlist = [] ## SONGS IN PLAYLIST
que_lenght = 0## for downloader
running = True ## to stop all threads
index = 0
skip = False
stopped = False

def play(name):
	global skip,playlist
	print("playing",name)
	#define stream chunk   
	chunk = 1024  

	#open a wav format music  
	f = wave.open(name+".wav","rb")  
	#instantiate PyAudio  
	p = pyaudio.PyAudio()  
	#open stream  
	stream = p.open(format = p.get_format_from_width(f.getsampwidth()),  
					channels = f.getnchannels(),  
					rate = f.getframerate(),  
					output = True)  
	#read data  
	data = f.readframes(chunk)  

	#play stream  
	while data and (not skip) and running:
		while stopped and running:
			pass
		stream.write(data)  
		data = f.readframes(chunk)  

	#stop stream
	stream.stop_stream()  
	stream.close()  

	#close PyAudio  
	p.terminate()  

def player():
	global running,index,skip
	while(running):
		if(len(playlist) > index):
			try:
				play(playlist[index])
				print("finished playing",playlist[index])
				
				index += 1
				skip = False
			except Exception as e:
				print("error occured in player!", e )
				skip = False
				pass
			
class AppURLopener(urllib.request.FancyURLopener):
	version = "Chrome/46.0"
	pass

def search_link(name):
	## IMPLEMENT SCRAPPING!!!!
	##sample : https://www.google.co.in/search?q=lalala&tbm=
	
	name = name.split(' ')
	temp = ''
	for _ in name:
		temp += _ +'+'
	temp = temp[:-1]
	
	google_link = 'https://www.youtube.com/results?search_query='+temp
	opener = AppURLopener()
	text = opener.open(google_link).read()
	soup = BeautifulSoup(text, 'lxml')
	
	links = []
	s_name = ""
	anc = soup.findAll('a')
	for a in anc:
		if (not a.parent or a.parent.name.lower() != "h3"):
			continue
		try:
			link = a['href']
			#print (a.encode('utf-8'))
			links.append(link)
			s_name = a.text
			print ("#############################",a.text.encode('utf-8'))
			break
		except KeyError:
			continue

	return s_name,"www.youtube.com"+links[0]


def download(name):
	name, link = search_link(name)
	try:
		ydl_opts = {
			'format': 'bestaudio/best',
			'postprocessors': [{
				'key': 'FFmpegExtractAudio',
				'preferredcodec': 'wav',
				'preferredquality': '192',
			}],
			'download_archive': './downloaded',
			'outtmpl': '%(title)s.%(ext)s',
			#'restrictfilenames': True,
		}
		with youtube_dl.YoutubeDL(ydl_opts) as ydl:
			ydl.download([link])
			playlist.append(name)
			
	except:
		pass


def link_download(link):
	
	opener = AppURLopener()
	text = opener.open("https://"+link).read()
	soup = BeautifulSoup(text, 'lxml')
	# - YouTube
	name = soup.find("title").text[:-10]
	
	try:
		ydl_opts = {
			'format': 'bestaudio/best',
			'postprocessors': [{
				'key': 'FFmpegExtractAudio',
				'preferredcodec': 'wav',
				'preferredquality': '192',
			}],
			'download_archive': './downloaded',
			'outtmpl': name+'.%(ext)s',
			#'restrictfilenames': True,
		}
		with youtube_dl.YoutubeDL(ydl_opts) as ydl:
			ydl.download([link])
			playlist.append(name)
			
	except Exception as e:
		print ("Error link download! ", e)
		pass
		
#### ------------------------------------------------------------------start all threads here!!

_thread.start_new_thread( player, () )

print ("Server started!")

def send_list(sock, st = ''):
	list = ''
	for i,_ in enumerate(playlist):
		list += _ 
		if i == index:
			list+='## NOW PLAYING'
		list += ":"
	clientsocket.send((st+":List:"+list).encode('utf-8'))
	

while running:
	try:
		
		# accept connections from outside
		(clientsocket, address) = serversocket.accept()
		# now do something with the clientsocket
		# in this case, we'll pretend this is a threaded server
		data = bytes(clientsocket.recv(1024)).decode('utf-8')
		print (data,"recieved")
		raw = data.split(':')
		print(raw,'raw')
		if(len(raw)>1):
			print ('got if')
			command = raw[0]
			raw = raw[1:]
			song = ""
			for _ in raw:
				song += _
				
			if(command == 'add'):
				print (song+" added")
				_thread.start_new_thread( download, (song,) )
				send_list(clientsocket,song+" added")
			elif(command == 'link'):
				print (song+" added")
				_thread.start_new_thread( link_download, (song,) )
				send_list(clientsocket,song+" added")
			elif (command == 'remove'):
				try:
					que_lenght -= 1
					playlist.pop(playlist.index(song))
					send_list(clientsocket,song+" removed")
				except:
					send_list(clientsocket,song+" not in list")
			elif(command == 'volume'):
				if(song == "p"):
					clientsocket.send("Volume increased!")
				if(song == "m"):
					clientsocket.send("Volume decreased!")
		else:
			if(raw[0]=="stop"):
				## implement this
				stopped = True
				send_list(clientsocket)
			if(raw[0]=="play"):
				## implement this
				stopped = False
				send_list(clientsocket)
			if(raw[0]=="skip"):
				## implement this
				skip = True
				send_list(clientsocket)
				#pass
			
			if(raw[0]=="list"):
				## implement this
				send_list(clientsocket)
			if(raw[0]=="quit"):
				## implement this
				running = False
				send_list(clientsocket)
			if(raw[0]=="reset"):
				## implement this
				index = 0
				send_list(clientsocket)
		## add features to play song using api
		
		clientsocket.close()
	except Exception as e:
		print("An error occured in server: ",e)
		running = False
		serversocket.close()

serversocket.close()
running = False
		