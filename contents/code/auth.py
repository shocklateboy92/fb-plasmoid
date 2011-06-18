from PyQt4.QtCore import *
from PyQt4.QtNetwork import *
from PyQt4.QtWebKit import *


class AuthenticationManager(QObject) :
    
    #finished = pyqtSignal(['QNetworkReply'], name='finished')
    accessTokenChanged = pyqtSignal()
    
    def __init__(self, settings) :
        QObject.__init__(self)
        self.settings = settings
        
        self.networkManager = QNetworkAccessManager()
        #QObject.connect(self.networkManager, SIGNAL("finished(QNetworkReply*)"), self.__handleReply)
        #self.finished.connect(self.__handleReply)
        self.networkManager.finished.connect(self.__handleReply)
        
        self.appid = '172712822755160'
        self.app_secret = '70fcd4802f2a54e77c843d08b56189a5'
        self.blankRedirectUrl = "http://www.facebook.com/connect/login_success.html"
        
        self.authURL = QUrl("https://www.facebook.com/dialog/oauth")
        self.authURL.addQueryItem("client_id", self.appid)
        self.authURL.addQueryItem("redirect_uri", self.blankRedirectUrl)
        self.authURL.addQueryItem("access_type", "client_credentials")
        
        self.tokenBaseUrl = QUrl("https://graph.facebook.com/oauth/access_token")
        self.tokenBaseUrl.addQueryItem("client_id", self.appid)
        self.tokenBaseUrl.addQueryItem("client_secret", self.app_secret)
        self.tokenBaseUrl.addQueryItem("redirect_uri", self.blankRedirectUrl)
        
        self.__browser = QWebView()
        
        #self.cache = QFile(".cache")
        #self.__readCache()
        
    #def __readCache(self) :
        #if (self.cache.open(QIODevice.ReadOnly | QIODevice.Text) == False) :
            #print(">>>>>>>> ERROR! : Unable to open file! Will have to Authenticate Session Manually")
            #self.reauthenticate()
        #else :
            #self.__parseToken(QTextStream(self.cache).readAll())
            #self.cache.close()
            
    def __parseToken(self, data) :
        data = data.split('&')[0]
        self.settings["access_token"] = str(data.split('=')[1])
        self.accessTokenChanged.emit()
        
    def reauthenticate(self) :
        if self.__browser.isVisible() :
            return
        self.__browser.load(QUrl(self.authURL))
        #QObject.connect(self.__browser, SIGNAL("urlChanged(const QUrl)"), self.__slotRedirect)
        self.__browser.urlChanged.connect(self.__slotRedirect)
        self.__browser.show()
        
    def __slotRedirect(self, url):
        print("Browser Redirect :")
        print(url.toString())
        
        code = url.queryItemValue("code")
        if code != "" :
            print("Got Code\n")
            print(code)
            print("Getting : ")
            self.tokenBaseUrl.addQueryItem("code", code)
            print(self.tokenBaseUrl)
            self.networkManager.get(QNetworkRequest(self.tokenBaseUrl));
            self.__browser.hide()
            
    def __handleReply(self, reply) :
        print("Data Recieved : ")
        print("\tFrom URL :" + reply.url().toString())
        data = reply.readAll()
        print(data)
        
        #TODO: change to check QNetworkReply rather than QUrl
        if(reply.url() == self.tokenBaseUrl) :
            if (data.contains("access_token=")) :
                self.__parseToken(data)
            else :
                print(">>>>>>>> ERROR! : Invalid Response! Unable to obtain Access Token")
        #self.browser.hide()
        
    #def __writeCache(self, data) :
        
        #if (self.cache.open(QIODevice.WriteOnly | QIODevice.Truncate | QIODevice.Text) == False) :
            #print(">>>>>>>> ERROR! : Unable to open file! Session will not be saved")
            #return
            
        #self.cache.write(data)
        #self.cache.close()
        
    def accessToken(self) :
        return self.settings["access_token"]