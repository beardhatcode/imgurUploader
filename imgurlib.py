#!/usr/bin/python3
# Name: Imgur Uploader Lib
# By Robbert Gurdeep Singh
################################################################################

import http.client,urllib.parse,base64
import ssl
import json
import os




class ImgurConnector:
    def __init__(self):
        self.ID="7c61d06d1fd1c60"
        self.secret="85846f896ea90dbc5dd07d8329be7aff75c25301"
        self.keyfile=os.path.join(os.path.dirname(__file__),"pin.txt")

        context = ssl.create_default_context()
        self.conn = http.client.HTTPSConnection('api.imgur.com', 443, context=context)

        if(os.path.isfile(self.keyfile)):
            self.getToken()
        else:
            self.getToken(True)


    def GETRequest(self,what):

        headers = {"Content-type": "application/x-www-form-urlencoded",
                    "Accept": "text/plain",
                    "Authorization":"Bearer "+self.accesdata["access_token"]}

        self.conn.request("GET", "/3/"+what,None,headers)


        response = self.conn.getresponse()
        data = response.read().decode("utf-8")

        if(response.status == 403):
            self.refreshToken()
            return self.GETRequest(what)


        data=json.loads(data)
        return data


    def POSTRequest(self,what,param):
        headers = {"Content-type": "application/x-www-form-urlencoded",
                    "Accept": "text/plain",
                    "Authorization":"Bearer "+self.accesdata["access_token"]}

        param=urllib.parse.urlencode(param)

        self.conn.request("POST", "/3/"+what,param,headers)

        response = self.conn.getresponse()
        data = response.read().decode("utf-8")

        if(response.status == 403):
            self.refreshToken()
            return self.POSTRequest(what,param)


        data=json.loads(data)
        return data


    def getToken(self,pin=None):

        if(pin == True):
            print("Go to:\nhttps://api.imgur.com/oauth2/authorize?client_id={0}&response_type=pin".format(self.ID))
            pin=input("Pin:").rstrip()


        if(pin != None):
            param=urllib.parse.urlencode({'client_id': self.ID,
                                          "client_secret":self.secret,
                                          'grant_type':"pin",
                                          'pin':pin})
            headers = {"Content-type": "application/x-www-form-urlencoded",
                        "Accept": "text/plain",
                        "Authorization":"Client-ID "+self.ID}

            self.conn.request("POST", "/oauth2/token",param,headers)
            response = self.conn.getresponse()
            data = response.read().decode("utf-8")
            data=json.loads(data)

            if(response.status != 200):
                print("Error ",response.status,":Something went wrong (",data['data']['error'],")")
                return self.getToken(True)

            with open(self.keyfile, 'w') as outfile:
                json.dump(data, outfile)
        else:
            with open(self.keyfile, 'r') as infile:
                data=json.load(infile)

            if 'access_token' not in data:
                print("No token found...")
                self.getToken(True)



        self.accesdata=data

    def refreshToken(self):
        param=urllib.parse.urlencode({'client_id': self.ID,
                                      "client_secret":self.secret,
                                      'grant_type':"refresh_token",
                                      'refresh_token':self.accesdata["refresh_token"]})
        headers = {"Content-type": "application/x-www-form-urlencoded",
                    "Accept": "text/plain",
                    "Authorization":"Client-ID "+self.ID}

        self.conn.request("POST", "/oauth2/token",param,headers)
        response = self.conn.getresponse()
        data = response.read().decode("utf-8")
        data=json.loads(data)

        if response.status != 200:
            print("Could not refresh token...")
            print(data)
            return self.getToken(True);

        with open(self.keyfile, 'w') as outfile:
            json.dump(data, outfile)


        self.accesdata=data


class Imgur:
    def __init__(self):
        self.connector = ImgurConnector();

    def changeImageInfo(self,imgId,title=None,desc=None):
        param = {}

        if(title!=None):
            param["title"]=title;

        if(desc!=None):
            param["description"]=desc

        return self.connector.POSTRequest("image/"+imgId,param)


    def listImages(self):
        return self.connector.GETRequest("account/me/images")["data"]

    def uploadImage(self,path):
        param={"type":"base64","name":os.path.basename(path)}
        with open(path, "rb") as image_file:
            param["image"] = base64.b64encode(image_file.read())


        return self.connector.POSTRequest("image",param)







