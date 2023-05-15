### This file is purely going to have functions, and no classes, it is only going to take certain arguements
# from its caller and based on them make the graphs and export them, along with certain details that it can
# all return as a dictionary, which can then be assigned from the worker class to the mainui class.


import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os, time, re, json
from datetime import datetime

class General :
    
    @staticmethod
    def get_file_name( path ) :
        head, tail = ntpath.split( path )
        return tail or ntpath.basename( head )
    
    @staticmethod
    def print_info(iterable):
        print('Length is : ', len(iterable))
        print('Type is : ', type(iterable))
        print('Type of iterable[0] is : ', type(iterable[0]))
        print('That iterable is : ', iterable[0])
        
    @staticmethod
    def print_len_type(iterable):
        print('Length is : ', len(iterable))
        print('Type is : ', type(iterable))  
                                                      
    def read_chat_file(filePath):
        with open(filePath, encoding = 'utf8') as fin:
            r = fin.readlines()
        return r

class read:
    
    def make_DataFrames(self, filePath, progressbar, progressLabel, messaging_app):
        
        self.words = []
        eachWordMetaData = []
        eachMessageMetaData = []
        people = set()
        
        if messaging_app == 'Whatsapp':
        
            lines = General.read_chat_file(filePath)
            print(len(lines))
            # removing the unwanted lines
            for l in lines[:]:
                date_regex = re.compile(r"((\d|1[0-2])/[0-2]\d|3[01])/([12]\d{1}[,])")
                match = date_regex.search(l)
                if match == None:
                    lines.remove(l)
                elif 'http' in l:
                    # print('removing coz htt there in ', l)
                    lines.remove(l)
                elif '/' not in l:
                    lines.remove(l)
                elif '<Media' in l:
                    # print('removing coz <med there in ', l)
                    lines.remove(l)
                elif '\n\n' in l:
                    # print('removing coz slnsln not there in ', l)
                    lines.remove(l)
                elif '\\U' in l:
                    # print('what even is this')
                    lines.remove(l)
            print(len(lines))
            # splitting the lines into lists that have words
            for l in lines:
                self.words.append(l.split())

            # removing useless whatsapp info
            for i in self.words:
                try:
                    if i[2] == 'Messages' or i[3] == 'Messages' or i[4] == 'Messages':
                        self.words.remove(i)
                except:
                    print(i)

            # cleaning the date and names, making everything lowercase, removing hyphens
            if '-' in self.words[0][2]: # 24 hour clock, one word name
                print('You are using 24 Hr clock. ')
                for i in self.words: 
                    i[0] = i[0].strip(',')
                    i[3] = i[3].strip(':')
                    for j in range(len(i)):
                        i[j] = i[j].lower()
                    i.remove(i[2])
            elif '-' in self.words[0][3]: # 24 hr clock, 2 word name, or 12 hr clock 1 word name
                print('You are using 12 Hr Clock.')
                for i in self.words: # 12 hr clock 1 word name
                    i[0] = i[0].strip(',')
                    i[4] = i[4].strip(':')
                    for j in range(len(i)):
                        i[j] = i[j].lower()
                    i.remove(i[3])
                    if i[2] == 'AM':
                        i.remove(i[2])
                    else:
                        if int(i[1].split(':')[0]) != 12:
                            i[1] = str(int(i[1].split(':')[0]) + 12) + ':' + str(i[1].split(':')[1])
                        else: 
                            i[1] = '00' + ':' + str(i[1].split(':')[1])
                        i.remove(i[2])

            print(self.words[17])

            # figuring out who the people are by taking the 2 names involved in the first 100 texts
            for i in self.words[:100]:
                print(i[2])
                people.add(i[2])
            print(people)
            self.person1, self.person2 = people

            
            # Changing their datatypes, now that names are known, so as to make counting easier
            # as ints are faster to iterate over than strings. Converting the date to its datetime format.
            for i in self.words:
                if i[2] == self.person1:
                    i[2] = 1
                else: i[2] = 2


            dateformat = '%m/%d/%y %H:%M'
            for i in self.words:
                try:
                    x = datetime.strptime(i[0] + ' ' + i[1], dateformat)
                except ValueError as err:
                    print(i)
                    print('changed date format')
                    dateformat = '%d/%m/%y %H:%M'
                    break

            for i in self.words:
                i[0] = datetime.strptime(i[0] + ' ' + i[1], dateformat)    
                i.remove(i[1])
            

            # Making a list with just the messages and its metadata, just the words and their metadata.
            for i in self.words:
                message = ''
                for j in range(2, len(i)):
                    eachWordMetaData.append([i[1], i[0], i[j]])
                    message += i[j] + ' '
                eachMessageMetaData.append([i[1], i[0], message.strip(' ')])


            # Making DataFrames for each person for words and messages using the lists made above.
            self.wordDf = pd.DataFrame(eachWordMetaData, columns = ['Speaker', 'Date', 'Word'])
            self.wordDf_P1 = self.wordDf[self.wordDf['Speaker'] == 1]
            self.wordDf_P2 = self.wordDf[self.wordDf['Speaker'] == 2]
            self.wordDf = pd.DataFrame(eachWordMetaData, columns = ['Speaker', 'Date', 'Word'])
            self.messageDf = pd.DataFrame(eachMessageMetaData, columns = ['Speaker', 'Date', 'Message'])
            self.messageDf_P1 = self.messageDf[self.messageDf['Speaker'] == 1]
            self.messageDf_P2 = self.messageDf[self.messageDf['Speaker'] == 2]
        
        elif messaging_app == 'Telegram':
            print('messages were taken from telegram')
            
            # defining Empty Dataframes
            self.wordDf = pd.DataFrame(columns = ['Speaker', 'Date', 'Word'])
            self.messageDf = pd.DataFrame(columns = ['Speaker', 'Date', 'Message'])
            
            # Reading the File
            with open(filePath, 'r') as f:
                data = json.load(f)
            for _, i in enumerate(data['messages']):
                if i['type'] == 'message' and type(i['text']) == str:
                    speaker = i['from']
                    date = datetime.strptime(i['date'], '%Y-%m-%dT%H:%M:%S')
                    message = i['text']
                    for j in message.split(' '):
                        self.wordDf = self.wordDf.append({'Speaker' : speaker, 'Date' : date, 'Word' : j}, ignore_index=True)
                    self.messageDf.loc[_] = [speaker, date, message]
            
            # Cleaning and Optimizing the DataFrame
            
            # Deleting Empty Rows
            self.wordDf['Word'].replace('', np.nan, inplace=True)
            self.wordDf.dropna(subset=['Word'], inplace=True)   
            self.messageDf['Message'].replace('', np.nan, inplace=True)
            self.messageDf.dropna(subset=['Message'], inplace=True) 
            
            # Changing People's names to Numebers so its easier to calculate. 
            
            people = set()
            for i in self.wordDf['Speaker']:
                people.add(i)
            
            self.person1, self.person2 = people
            self.wordDf['Speaker'].replace(self.person1, 1, inplace=True)
            self.wordDf['Speaker'].replace(self.person2, 2, inplace=True)
            self.messageDf['Speaker'].replace(self.person1, 1, inplace=True)
            self.messageDf['Speaker'].replace(self.person2, 2, inplace=True)
            
            
            # Creating Sub Data Sets
            self.wordDf_P1 = self.wordDf[self.wordDf['Speaker'] == 1]
            self.wordDf_P2 = self.wordDf[self.wordDf['Speaker'] == 2]
            self.messageDf_P1 = self.messageDf[self.messageDf['Speaker'] == 1]
            self.messageDf_P2 = self.messageDf[self.messageDf['Speaker'] == 2]        
                        
        print('everything done')
        progressbar.setValue(20)  
        
    def calc_statistics(self, progressBar, progressLabel):
        
        # making a statistics list to give back to the UI, that has all the basic info. 
        # rest of the stuff is just basic data collection from dataframes. Nothing imp to explain.

        # Messages Data
        self.totalMessages = len(self.messageDf)
        self.totalMessages_P1 = len(self.messageDf_P1)
        self.totalMessages_P2 = len(self.messageDf_P2)
        self.messagesPerc_P1 = round((self.totalMessages_P1/self.totalMessages) * 100, 2)
        self.messagesPerc_P2 = round((self.totalMessages_P2/self.totalMessages) * 100, 2)

        # Words Data
        self.totalWords = len(self.wordDf)
        self.totalWords_P1 = len(self.wordDf_P1)
        self.totalWords_P2 = len(self.wordDf_P2)
        self.wordsPerc_P1 = round((self.totalWords_P1/self.totalWords) * 100, 2)
        self.wordsPerc_P2 = round((self.totalWords_P2/self.totalWords) * 100, 2)

        # Unique Words
        self.uniqueWords_P1 = self.wordDf_P1['Word'].unique()
        self.uniqueWords_P2 = self.wordDf_P2['Word'].unique()
        self.uniqueWords = self.wordDf['Word'].unique()

        # now some Dates and times
        self.totalMinutes = len(self.messageDf['Date'].unique())
        uniqueDates = list(self.messageDf['Date'].apply(lambda x : x.replace(hour = 0, minute = 0, second = 0)).unique())
        self.totalDays = len(uniqueDates)

        # Finding the total time spent talking, and setting the right unit for it
        self.totalTime = 0
        self.timeUnit = 'M'
        if self.totalMinutes > 60:
            self.totalTime = self.totalMinutes / 60
            self.timeUnit = 'H'
        elif self.totalMinutes > 1440 :
            self.totalTime = self.totalMinutes/1440
            self.timeUnit = 'D'
        else : self.totalTime = self.totalMinutes
        self.totalTime = round(self.totalTime, 2)

        # Finding Unique Words used by each, excluding emojis, and then finding most used words.
        self.wordUsage_P1 = self.wordDf_P1['Word'].value_counts()
        self.wordUsage_P2 = self.wordDf_P2['Word'].value_counts()
        for i in self.wordUsage_P1.index:
            if i == '😂':
                self.wordUsage_P1.pop(i)
        for i in self.wordUsage_P2.index:
            if i == '😂':
                self.wordUsage_P2.pop(i)
        self.mostUsedWord_P1 = self.wordUsage_P1.index[0]
        self.mostUsedWord_P2 = self.wordUsage_P2.index[0]

        # finding the days without talking
        self.dateDifferences = []

        for i in range(1, len(uniqueDates)):
            self.dateDifferences.append(uniqueDates[i] - uniqueDates[i-1])
        self.dateDifferences = np.array(self.dateDifferences).astype('timedelta64[h]')
        for i in range(len(self.dateDifferences)):
            self.dateDifferences[i] = self.dateDifferences[i]/24
        self.dateDifferences = self.dateDifferences.astype('int64')
        self.maxDaysNoTalk = self.dateDifferences.max()

        # Finding the number of days talked continuously.
        self.maxDaysTalk = 0
        count = 0
        for i in range(1, len(self.dateDifferences)):
            if self.dateDifferences[i] == self.dateDifferences[i-1]:
                count += 1
                if count >= self.maxDaysTalk:
                    self.maxDaysTalk = count
            else : count = 1

        # Finding the maximum time spent talking in one day
        # since you cant just take hours, as people talk in different hours wont mean they talk that much time, 
        # we would take minutes, and then divide them to get hours
        self.uniqueMinutes = self.messageDf['Date'].unique()
        count = 1
        self.maxMinutes = 0
        for i in range(1, len(self.uniqueMinutes)):
            if self.uniqueMinutes[i].astype('datetime64[D]') == self.uniqueMinutes[i-1].astype('datetime64[D]'):
                count += 1
                if count >= self.maxMinutes:
                    self.maxMinutes = count
            else: count = 1

        # Setting the right time unit for it
        self.maxTime = 0
        self.timeUnitMostTime = 'M'
        if self.maxMinutes > 60:
            self.maxTime = self.maxMinutes / 60
            self.timeUnitMostTime = 'H'
        else : self.maxTime = self.maxMinutes
        self.maxTime = round(self.maxTime, 2)
        
    def return_statistics(self, progressBar, progressLabel):
        # Appending the general stats to the list to give back to the UI
        
        statisticsList = []
        
        statisticsList.append('Total Number of Messages between both is : ' + str(self.totalMessages) + ', and words is : ' + str(self.totalWords))
        if self.timeUnit == 'M':
            statisticsList.append('Total Number of Minutes spent talking is : ' + str(self.totalTime))
        elif self.timeUnit == 'H':
            statisticsList.append('Total Number of Hours spent talking is : ' + str(self.totalTime))
        elif self.timeUnit == 'D':
            statisticsList.append('Total Number of Days spent talking is : ' + str(self.totalTime))


        statisticsList.append('Average time spent Talking Daily is : ' + str(round(self.totalMinutes/self.totalDays)) + ' Minutes')
        statisticsList.append('Total Messages sent by ' + self.person1 + ' is : ' + str(self.totalMessages_P1) + ' which is ' + str(self.messagesPerc_P1) + ' %')
        statisticsList.append('Total Messages sent by ' + self.person2 + ' is : ' + str(self.totalMessages_P2) + ' which is ' + str(self.messagesPerc_P2) + ' %')
        statisticsList.append('Total Words sent by ' + self.person1 + ' is : ' + str(self.totalWords_P1) + ' which is ' + str(self.wordsPerc_P1) + ' %')
        statisticsList.append('Total Words sent by ' + self.person2 + ' is : ' + str(self.totalWords_P2) + ' which is ' + str(self.wordsPerc_P2) + ' %')
        statisticsList.append('Average Length of Each message of ' + self.person1 + ' is ' + str(round(self.totalWords_P1/self.totalMessages_P1)) + ' Words')
        statisticsList.append('Average Length of Each message of ' + self.person2 + ' is ' + str(round(self.totalWords_P2/self.totalMessages_P2)) + ' Words')
        statisticsList.append('Total Unique words used are ' + str(len(self.uniqueWords)) + ', ' + str(len(self.uniqueWords_P1)) + ' by ' + self.person1 + ' and ' + str(len(self.uniqueWords_P2)) + ' by ' + self.person2)
        statisticsList.append('The Most used word by ' + self.person1 + ' is ' + '\"' + self.mostUsedWord_P1.upper() + '\"' + ', by ' + self.person2 + ' is ' + '\"' + self.mostUsedWord_P2.upper() + '\"')
        statisticsList.append('The Most Days without talking were : ' + str(self.maxDaysNoTalk))
        statisticsList.append('The Most Days talking consecutively were : ' + str(self.maxDaysTalk))
        
        
        if self.timeUnitMostTime == 'M':
            statisticsList.append('Maximum number of Minutes spent talking in one day is : ' + str(self.maxTime))
        elif self.timeUnitMostTime == 'H':
            statisticsList.append('Maximum number of Hours spent talking in one day is : ' + str(self.maxTime))
        progressBar.setValue(42)
        progressLabel.setText('Generating Statistics...')
        time.sleep(.3)
        progressLabel.setText('Done...')
        time.sleep(.3)
        return statisticsList
    
    def make_graphs(self, requiredGraphs, graphWordsList, graphDestPath, progressBar, progressLabel, mainTabs):
        
        progressBar.setValue(50)
        progressLabel.setText('Making Graphs...')
        time.sleep(.3)
        
        try :
            os.mkdir(graphDestPath + '/Graphs')
        except FileExistsError:
            print('exists, skipping')
            progressLabel.setText('Graph Folder Already Exists, skipping')
            time.sleep(.3)
        self.graphDestPath = graphDestPath + '/Graphs/'
        if 'No. of Messages sent Daily' in requiredGraphs:
            self.messages_daily()
            progressBar.setValue(55)
            progressLabel.setText('Messages Daily Done...')
            time.sleep(.3)
        if 'No. of Messages sent Monthly' in requiredGraphs:
            self.messages_monthly()
            progressBar.setValue(67)
            progressLabel.setText('Messages Monthly Done...')
            time.sleep(.3)
        if 'No. of Words sent Daily' in requiredGraphs:
            self.words_daily()
            progressBar.setValue(69)
            progressLabel.setText('Words Daily Done...')
            time.sleep(.5)
        if 'No. of Words sent Monthly' in requiredGraphs:
            self.words_monthly()
            progressBar.setValue(70)
            progressLabel.setText('Words Monthly Done...')
            time.sleep(.3)
        if 'Percentage of Messages' in requiredGraphs:
            self.perc_messages()
            progressBar.setValue(75)
            progressLabel.setText('Percentage of Messages Done...')
            time.sleep(.3)
        if 'Percentage of Words' in requiredGraphs:
            self.perc_words()
            progressBar.setValue(80)
            progressLabel.setText('Percentage of Words Done...')
            time.sleep(.3)
        if 'Time Spent Monthly' in requiredGraphs:
            self.time_spent_monthly()
            progressBar.setValue(85)
            progressLabel.setText('Time Spent Monthly Done...')
            time.sleep(.3)
        if '20 Most Used Words' in requiredGraphs:
            self.top_20_words()
            progressBar.setValue(90)
            progressLabel.setText('Most Used Words Done...')
            time.sleep(.3)
        if 'Time Spent Daily' in requiredGraphs:
            self.time_spent_daily()
            progressBar.setValue(95)
            progressLabel.setText('Time Spent Daily Done...')
            time.sleep(.3)
        if 'Most Active Hours' in requiredGraphs:
            self.active_hours()
            progressBar.setValue(96)
            progressLabel.setText('Most Active Hours Done...')
            time.sleep(.3)
        if 'Length of Each Session' in requiredGraphs:
            self.length_session()
            progressBar.setValue(97)
            progressLabel.setText('Length of Each Session Done...')
            time.sleep(.3)
        if 'Weekly Activity' in requiredGraphs:
            self.time_spent_weekday()
        if graphWordsList != '':
            progressBar.setValue(99)
            progressLabel.setText('Special Words also Done...')
            time.sleep(.3)
            self.particular_words_over_time(graphWordsList)
            
            progressBar.setValue(100)
            progressLabel.setText('Yesss! Everything Done Successfully!')
                


    def messages_daily(self): 
        
        uniqueDates_P1 = self.messageDf_P1['Date'].apply(lambda x : x.replace(hour = 0, minute = 0, second = 0))
        uniqueDates_P2 = self.messageDf_P2['Date'].apply(lambda x : x.replace(hour = 0, minute = 0, second = 0))
        uniqueDates_Both = self.messageDf['Date'].apply(lambda x : x.replace(hour = 0, minute = 0, second = 0))

        # Making DataFrames for Messages Sent Each Day
        messagesEachDay_P1 = uniqueDates_P1.value_counts()
        data = {
            'Dates' : list(messagesEachDay_P1.index),
            'Number of messages' : list(messagesEachDay_P1)
        }
        messagesEachDayDf_P1 = pd.DataFrame(data).sort_values(by = ['Dates'])

        messagesEachDay_P2 = uniqueDates_P2.value_counts()
        data = {
            'Dates' : list(messagesEachDay_P2.index),
            'Number of messages' : list(messagesEachDay_P2)
        }
        messagesEachDayDf_P2 = pd.DataFrame(data).sort_values(by = ['Dates'])

        messagesEachDay_Both = uniqueDates_Both.value_counts()
        data = {
            'Dates' : list(messagesEachDay_Both.index),
            'Number of messages' : list(messagesEachDay_Both)
        }
        messagesEachDayDf_Both = pd.DataFrame(data).sort_values(by = ['Dates'])

        plt.figure(figsize=(20, 7))
        plt.style.use('fivethirtyeight')
        plt.style.use('fivethirtyeight')
        plt.plot(messagesEachDayDf_P1['Dates'], messagesEachDayDf_P1['Number of messages'], label = self.person1, color = '#367ee2', linewidth = 1)
        plt.plot(messagesEachDayDf_P2['Dates'], messagesEachDayDf_P2['Number of messages'], label = self.person2, color = '#3ba566', linewidth = 1)
        plt.plot(messagesEachDayDf_Both['Dates'], messagesEachDayDf_Both['Number of messages'], label = 'Both', color = '#5f4b95', linewidth = 1)
        plt.gcf().autofmt_xdate()
        plt.title(f'{self.person1} with {self.person2} Messages Sent Daily')
        plt.legend(loc = 'best')
        plt.savefig(f'{self.graphDestPath}{self.person1} with {self.person2} Messages Sent Daily.jpg', dpi=300)
        plt.clf()


    def words_daily(self):

        uniqueDates_P1 = self.wordDf_P1['Date'].apply(lambda x : x.replace(hour = 0, minute = 0, second = 0))
        uniqueDates_P2 = self.wordDf_P2['Date'].apply(lambda x : x.replace(hour = 0, minute = 0, second = 0))
        uniqueDates_Both = self.wordDf['Date'].apply(lambda x : x.replace(hour = 0, minute = 0, second = 0))

        # Making DataFrames for words Sent Each Day
        wordsEachDay_P1 = uniqueDates_P1.value_counts()
        data = {
            'Dates' : list(wordsEachDay_P1.index),
            'Number of words' : list(wordsEachDay_P1)
        }
        wordsEachDayDf_P1 = pd.DataFrame(data).sort_values(by = ['Dates'])

        wordsEachDay_P2 = uniqueDates_P2.value_counts()
        data = {
            'Dates' : list(wordsEachDay_P2.index),
            'Number of words' : list(wordsEachDay_P2)
        }
        wordsEachDayDf_P2 = pd.DataFrame(data).sort_values(by = ['Dates'])

        wordsEachDay_Both = uniqueDates_Both.value_counts()
        data = {
            'Dates' : list(wordsEachDay_Both.index),
            'Number of words' : list(wordsEachDay_Both)
        }
        wordsEachDayDf_Both = pd.DataFrame(data).sort_values(by = ['Dates'])



        plt.plot(wordsEachDayDf_P1['Dates'], wordsEachDayDf_P1['Number of words'], label = self.person1, color = '#367ee2', linewidth = 1)
        plt.plot(wordsEachDayDf_P2['Dates'], wordsEachDayDf_P2['Number of words'], label = self.person2, color = '#3ba566', linewidth = 1)
        plt.plot(wordsEachDayDf_Both['Dates'], wordsEachDayDf_Both['Number of words'], label = 'Both', color = '#5f4b95', linewidth = 1)
        plt.gcf().autofmt_xdate()
        plt.title(f'{self.person1} with {self.person2} words Sent Daily')
        plt.legend(loc = 'best')
        plt.savefig(f'{self.graphDestPath}{self.person1} with {self.person2} words Sent Daily.jpg', dpi = 200)
        plt.clf()


    def perc_messages(self):
        plt.pie([self.messagesPerc_P1,  self.messagesPerc_P2], startangle = 90, labels = [self.person1, self.person2], colors = ['#367ee2', '#3ba566'], shadow = True, autopct = '%1.2f%%')
        plt.legend(loc = 'best')
        plt.title(f'{self.person1} and {self.person2} Percentage of Messages Sent')
        plt.savefig(f'{self.graphDestPath}{self.person1} and {self.person2} Percentage of Messages Sent', dpi = 300)
        plt.clf()


    def perc_words(self):

        plt.pie([self.wordsPerc_P1,  self.wordsPerc_P2], startangle = 90, labels = [self.person1, self.person2], colors = ['#367ee2', '#3ba566'], shadow = True, autopct = '%1.2f%%')
        plt.legend(loc = 'best')
        plt.title(f'{self.person1} and {self.person2} Percentage of Words Sent')
        plt.savefig(f'{self.graphDestPath}{self.person1} and {self.person2} Percentage of Words Sent', dpi = 300)
        plt.clf()


    def messages_monthly(self):

        print('you called me again monthly')
        uniqueDates_P1 = self.messageDf_P1['Date'].apply(lambda x : x.replace(day = 1, hour = 0, minute = 0, second = 0))
        uniqueDates_P2 = self.messageDf_P2['Date'].apply(lambda x : x.replace(day = 1, hour = 0, minute = 0, second = 0))
        uniqueDates_Both = self.messageDf['Date'].apply(lambda x : x.replace(day = 1, hour = 0, minute = 0, second = 0))

        # Making DataFrames for Messages Sent Each Day
        messagesEachDay_P1 = uniqueDates_P1.value_counts()
        data = {
            'Dates' : list(messagesEachDay_P1.index),
            'Number of messages' : list(messagesEachDay_P1)
        }
        messagesEachDayDf_P1 = pd.DataFrame(data).sort_values(by = ['Dates'])

        messagesEachDay_P2 = uniqueDates_P2.value_counts()
        data = {
            'Dates' : list(messagesEachDay_P2.index),
            'Number of messages' : list(messagesEachDay_P2)
        }
        messagesEachDayDf_P2 = pd.DataFrame(data).sort_values(by = ['Dates'])

        messagesEachDay_Both = uniqueDates_Both.value_counts()
        data = {
            'Dates' : list(messagesEachDay_Both.index),
            'Number of messages' : list(messagesEachDay_Both)
        }
        messagesEachDayDf_Both = pd.DataFrame(data).sort_values(by = ['Dates'])


        plt.style.use('fivethirtyeight')
        plt.plot(messagesEachDayDf_P1['Dates'], messagesEachDayDf_P1['Number of messages'], label = self.person1, color = '#367ee2', linewidth = 1)
        plt.plot(messagesEachDayDf_P2['Dates'], messagesEachDayDf_P2['Number of messages'], label = self.person2, color = '#3ba566', linewidth = 1)
        plt.plot(messagesEachDayDf_Both['Dates'], messagesEachDayDf_Both['Number of messages'], label = 'Both', color = '#5f4b95', linewidth = 1)
        a = [i.to_pydatetime().strftime('%B') for i in messagesEachDayDf_P1['Dates']]
        plt.xticks(labels = a, ticks = [i.to_pydatetime() for i in messagesEachDayDf_P1['Dates']])
        plt.gcf().autofmt_xdate()
        plt.title(f'{self.person1} with {self.person2} Messages Sent Monthly')
        plt.legend(loc = 'best')
        plt.savefig(f'{self.graphDestPath}{self.person1} with {self.person2} Messages Sent Monthly.jpg', dpi = 300)
        plt.clf()


    def words_monthly(self):

        wordDatesMonthly_P1 = self.wordDf_P1['Date'].apply(lambda x : x.replace(day = 1, hour = 0, minute = 0, second = 0))
        wordDatesMonthly_P2 = self.wordDf_P2['Date'].apply(lambda x : x.replace(day = 1, hour = 0, minute = 0, second = 0))
        wordDatesMonthly_Both = self.wordDf['Date'].apply(lambda x : x.replace(day = 1, hour = 0, minute = 0, second = 0))

        # Making DataFrames for words Sent Each Day
        wordsEachDay_P1 = wordDatesMonthly_P1.value_counts()
        data = {
            'Dates' : list(wordsEachDay_P1.index),
            'Number of words' : list(wordsEachDay_P1)
        }
        wordsEachDayDf_P1 = pd.DataFrame(data).sort_values(by = ['Dates'])

        wordsEachDay_P2 = wordDatesMonthly_P2.value_counts()
        data = {
            'Dates' : list(wordsEachDay_P2.index),
            'Number of words' : list(wordsEachDay_P2)
        }
        wordsEachDayDf_P2 = pd.DataFrame(data).sort_values(by = ['Dates'])

        wordsEachDay_Both = wordDatesMonthly_Both.value_counts()
        data = {
            'Dates' : list(wordsEachDay_Both.index),
            'Number of words' : list(wordsEachDay_Both)
        }
        wordsEachDayDf_Both = pd.DataFrame(data).sort_values(by = ['Dates'])


        plt.style.use('fivethirtyeight')
        plt.plot(wordsEachDayDf_P1['Dates'], wordsEachDayDf_P1['Number of words'], label = self.person1, color = '#367ee2', linewidth = 1.5)
        plt.plot(wordsEachDayDf_P2['Dates'], wordsEachDayDf_P2['Number of words'], label = self.person2, color = '#3ba566', linewidth = 1.5)
        plt.plot(wordsEachDayDf_Both['Dates'], wordsEachDayDf_Both['Number of words'], label = 'Both', color = '#5f4b95', linewidth = 1.5)
        a = [i.to_pydatetime().strftime('%B') for i in wordsEachDayDf_P1['Dates']]
        plt.xticks(labels = a, ticks = [i.to_pydatetime() for i in wordsEachDayDf_P1['Dates']])
        plt.gcf().autofmt_xdate()
        plt.title(f'{self.person1} with {self.person2} words Sent Monthly')
        plt.legend(loc = 'best')
        plt.savefig(f'{self.graphDestPath}{self.person1} with {self.person2} words Sent Monthly.jpg', dpi = 300)
        plt.clf()


    def top_20_words(self):

        wordDatesMonthly_P1 = self.wordDf_P1['Date'].apply(lambda x : x.replace(day = 1, hour = 0, minute = 0, second = 0))
        wordDatesMonthly_P2 = self.wordDf_P2['Date'].apply(lambda x : x.replace(day = 1, hour = 0, minute = 0, second = 0))

        wordsEachDay_P1 = wordDatesMonthly_P1.value_counts()
        data = {
            'Words' : list(self.wordUsage_P1.index),
            'Number' : list(self.wordUsage_P1)
        }
        wordUsageDf_P1 = pd.DataFrame(data).sort_values(by = ['Number'], ascending = False)

        wordUsageDf_P2 = wordDatesMonthly_P2.value_counts()
        data = {
            'Words' : list(self.wordUsage_P2.index),
            'Number' : list(self.wordUsage_P2)
        }
        wordUsageDf_P2 = pd.DataFrame(data).sort_values(by = ['Number'], ascending = False)

        num_of_words = 20

        p1x = np.arange(num_of_words)
        p2x = np.arange(num_of_words) + np.array(0.3)

        plt.bar(p1x, wordUsageDf_P1['Number'][:num_of_words], label = self.person1, color = '#9d63cf', width = 0.3, edgecolor = 'k')
        plt.bar(p2x, wordUsageDf_P2['Number'][:num_of_words], label = self.person2, color = '#ecac74', width = 0.3, edgecolor = 'k')
        l = []
        for i in range(num_of_words):
            l.append(wordUsageDf_P1['Words'][:num_of_words][i])
            l.append(wordUsageDf_P2['Words'][:num_of_words][i])

        t = np.vstack((p1x, p2x)).reshape((-1,),order='F')
        plt.xticks(ticks = t, labels = l, rotation = 45)
        plt.title(f'{self.person1} with {self.person2} Top 20 Words')
        plt.legend(loc = 'best')
        plt.savefig(f'{self.graphDestPath}{self.person1} with {self.person2} Top 20 Words.jpg', dpi = 300)
        plt.clf()
        
        
        
        
        
        
        
        
        
        


    def time_spent_daily(self):

        just_dates = pd.Series(self.messageDf['Date'].unique()).apply(lambda x : x.replace(hour = 0, minute = 0, second = 0))
        HoursDaily = (just_dates.value_counts()/60).sort_index()
        # a = pd.Series([i.to_pydatetime().strftime('%b') for i in HoursDaily.index]).unique()
        plt.plot(HoursDaily.index, HoursDaily, color = '#9d63cf', linewidth = 1.5)
        plt.title(f'{self.person1} with {self.person2} Time Spent Daily')
        plt.xlabel('Dates')
        plt.ylabel('Hours')
        plt.gcf().autofmt_xdate()
        plt.savefig(f'{self.graphDestPath}{self.person1} with {self.person2} Time Spent Daily.jpg', dpi = 300)
        plt.clf()


    def time_spent_monthly(self):      
        just_dates = pd.Series(pd.Series(self.messageDf['Date'].unique()).apply(lambda x : x.replace(day = 1, hour = 0, minute = 0, second = 0)))
        HoursMonthly = (just_dates.value_counts()/60).sort_index()
        a = pd.Series([i.to_pydatetime().strftime('%B-%Y') for i in HoursMonthly.index])
        plt.bar(a, HoursMonthly, color = '#71194b', linewidth = 1.5)
        plt.title(f'{self.person1} with {self.person2} Time Spent Monthly')
        plt.xlabel('Months')
        plt.ylabel('Hours')
        plt.gcf().autofmt_xdate()
        plt.savefig(f'{self.graphDestPath}{self.person1} with {self.person2} Time Spent Monthly.jpg', dpi = 300)
        plt.clf()

    def particular_words_over_time(self, words):
        colors = ['#296a30', '#1d8baf', '#c94a4a', '#9d63cf']
        import math
        for i in range(math.ceil(len(words)/4)):
            for _, word in enumerate(words[i*4:(i+1)*4], start = 0):
                try:
                    particularWordDf = self.wordDf[self.wordDf['Word'] == word]
                    particularWordUsage = particularWordDf['Date'].apply(lambda x : x.replace(hour = 0, minute = 0, second = 0)).value_counts().sort_index()
                    plt.plot(particularWordUsage, color = colors[_], linewidth = 1, label = word)
                    plt.title(f'{self.person1} and {self.person2} Special Word Usages - ' + str(i+1))
                    plt.legend(loc = 'best')
                    plt.xlabel('Dates')
                    plt.ylabel('Number of Times Used')
                    plt.gcf().autofmt_xdate()
                except IndexError as err:
                    print(err)
                    break
            plt.savefig(f'{self.graphDestPath}{self.person1} and {self.person2} Special Word Usages - ' + str(i+1) + '.jpg', dpi = 300)
            plt.clf()
            
        
    def length_session(self):
        uniqueMinutes = self.messageDf['Date'].unique()
        bins = list(np.arange(0, 10, step = .5))
        bins = [1, 2, 3, 4, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 60, 90, 120, 150, 180, 210, 240, 300, 1000]

        uniqueMinutes = pd.Series(uniqueMinutes).sort_values()
        count = 1
        sessions = []
        for i in range(len(uniqueMinutes)-1):
            if uniqueMinutes[i].to_pydatetime().strftime('%y%m%d%h') == uniqueMinutes[i].to_pydatetime().strftime('%y%m%d%h'):
                if uniqueMinutes[i].minute >= uniqueMinutes[i+1].minute - 5:
                    count += 1
                else :
                    sessions.append(count)
                    count = 1
        h,e = np.histogram(sessions, bins=bins)
        plt.bar(range(len(bins)-1),h, width=1, edgecolor='#296a30',  color = '#9bee81')
        labels = []
        labels.append('<1')
        for i in range(1, 13 ):
            labels.append(str(bins[i]) + '-' + str(bins[i+1]))
        for i in ['1 Hr', '1.5 Hr', '2 Hr', '2.5 Hr', '3 Hr', '3.5 Hr', '4 Hr', '5 Hr', '5+ Hrs']:
            labels.append(i)
        plt.xlabel('Minutes')
        plt.ylabel('Number of Sessions')
        plt.title(f'{self.person1} with {self.person2} Length of Texting Sessions')
        plt.xticks(ticks = range(len(bins)-1), labels = labels, rotation = 45)
        plt.savefig(f'{self.graphDestPath}{self.person1} and {self.person2} Session Times.jpg', dpi = 300)
        plt.clf()


    def time_spent_weekday(self):

        uniqueMinutes = pd.Series(self.messageDf['Date'].unique()).sort_values()
        weekdays = [0 for i in range(7)]
        for i in range(len(uniqueMinutes)):
            if uniqueMinutes[i].day_name() == 'Monday':
                weekdays[0] += 1
            elif uniqueMinutes[i].day_name() == 'Tuesday':
                weekdays[1] += 1
            elif uniqueMinutes[i].day_name() == 'Wednesday':
                weekdays[2] += 1
            elif uniqueMinutes[i].day_name() == 'Thursday':
                weekdays[3] += 1
            elif uniqueMinutes[i].day_name() == 'Friday':
                weekdays[4] += 1
            elif uniqueMinutes[i].day_name() == 'Saturday':
                weekdays[5] += 1
            elif uniqueMinutes[i].day_name() == 'Sunday':
                weekdays[6] += 1

        weekdays = [i/60 for i in weekdays]
        plt.bar(range(7), weekdays, color = '#ecac74')
        plt.title(f'{self.person1} with {self.person2} Total Hours Spent over the Week')
        plt.xlabel('WeekDays')
        plt.ylabel('Hours')
        plt.xticks(labels = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'], ticks = np.arange(7), rotation = 10)
        plt.savefig(f'{self.graphDestPath}{self.person1} with {self.person2} Total Time spent Over the Week.jpg', dpi = 300)
        plt.clf()


    def active_hours(self):

        messagesEachHour = self.messageDf['Date'].apply(lambda x : x.replace(day = 1, month = 1, year = 2020, minute = 0, second = 0)).value_counts().sort_index()
        pd.Series(messagesEachHour.index)
        hours = [i.hour for i in pd.Series(messagesEachHour.index)]
        plt.bar(hours, messagesEachHour, color = '#ecac74')
        plt.title(f'{self.person1} with {self.person2} Total Messages Each Hour All Time')
        plt.xlabel('Hours')
        plt.ylabel('Number of Messages')
        plt.savefig(f'{self.graphDestPath}{self.person1} with {self.person2} Total Messages Each Hour All Time.jpg', dpi = 300)
        plt.clf()        
            
            