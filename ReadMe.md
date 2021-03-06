# _Chit Chat Charts_

![](https://github.com/KrishnarajT/Chit-Chat-Charts/blob/master/chit%20chat%20charts2.png)

This is a GUI made for making analysis of your Social Media Chats easier. It gives statistics about your chat file, things like time spent, most used words, number of messages etc, and then plots this data as a timeline for many available attributes you can choose from. It then stores these graphs in your preferable directory.

## Installation # to be added

### _Windows_
You just install the Latest version from Github, follow the installer and launch the app.

### _Linux_
Same thing, install the linux executable from the latest Release. 

##### Executable :
You can download the tar.gz File from github and install accordingly.

## Usage

1. Get your chat text file into your computer. 
   
   i) For whatsapp, open the chat you want, go to the Menu>More>Export Chat>Without Media and copy the file.
   
   ii) For Instagram, go to settings, privacy, export data.

   iii) For telegram on PC, go to chat, exoport chat history.

2. Drag and drop this file into the GUI, or select its location manually, then select the folder where you want the graphs to be.
3. Set graph preferences and select the kind of graphs you want.

Your graphs will be exported to the graph directory that you chose under the folder `Graphs`


## Compatibility

You can select text files from these apps to analyze.

1. Whatsapp (.txt files)
2. Instagram (.json files) # not yet done
3. Telegram (.json files) # not yet done


## To-Do
1. Add compatibility for instagram and telegram files.
2. Add new tabs to show graphs within the app.
3. Add Emoji support
4. Upload to AUR, debian repos and create linux and windows Executables.
5. Add a good theme support

## Credits
I did this with pyQt5, pandas and matplotlib in python. Thanks to the websites that helped me learn pyQt and refer to its documentation. 
