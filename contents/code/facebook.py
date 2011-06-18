from PyQt4.QtXml import QDomDocument
from PyQt4.QtNetwork import *
from PyQt4.QtCore import *
from PyKDE4.kdeui import KNotification
from PyQt4.QtGui import QPixmap


class FacebookManager(QObject) :
    
    authExpired = pyqtSignal()
    queryFailed = pyqtSignal()
    notificationsChanged = pyqtSignal(int)
    
    def __init__(self, settings) :
        QObject.__init__(self)
        #self.accessToken = authToken
        self.settings = settings
        
        self.NetworkManager = QNetworkAccessManager()
        #QObject.connect(self.NetworkManager, SIGNAL("finished(QNetworkReply*)"), self.__handleReply)
        self.NetworkManager.finished.connect(self.__handleReply)
        
        self.queryString = "SELECT title_html, created_time, now() FROM notification WHERE recipient_id = me() AND is_unread = 1 "
        self.__notifications = 0
        
        self.updateQueries()
        
        self.activeQuery = ""
        
    def updateQueries(self) :
        print("== Updating Queries ==")
        self.fullqueryURL = QUrl("https://api.facebook.com/method/fql.query")
        self.fullqueryURL.addQueryItem("query", self.queryString)
        self.fullqueryURL.addQueryItem("format", "xml")
        self.fullqueryURL.addQueryItem("access_token", self.settings["access_token"])
        
        #self.miniqueryURL = QUrl("https://api.facebook.com/method/fql.query")
        #self.miniqueryURL.addQueryItem("query", (self.queryString + " AND updated_time = now() - " + str(self.settings["pollinterval"])))
        #self.miniqueryURL.addQueryItem("format", "xml")
        #self.miniqueryURL.addQueryItem("access_token", self.settings["access_token"])
        
        #self.__runQuery(True)
        
    def __runQuery(self) :
        #check if settings["access_token"] exists
        if self.settings["access_token"] == "" :
            print("ERROR! Not Authenticated")
            self.authExpired.emit()
            return
            
            # or self.activeQuery.error() != QNetworkReply.NoError
        if self.activeQuery != "" :
            print(">>>>>>>> ERROR! : Previous Query Still Incomplete! Aborting")
            #self.activeQuery.abort()
            self.__notifications = -1
            self.queryFailed.emit()
	else :
	    print("== Sending Query ==")
	    self.activeQuery = self.NetworkManager.get(QNetworkRequest(self.fullqueryURL))
                
    def __handleReply(self, reply) :
        self.activeQuery = ""
        
        if reply.error() != QNetworkReply.NoError :
            print(">>>>>>>> ERROR! : Network Error (" + reply.errorString() + ")")
            self.__notifications = -1
            self.queryFailed.emit()
            return
            
        doc = QDomDocument()
        doc.setContent(reply)
        root = doc.documentElement()
        
        if root.tagName() == "error_response" :
            print(">>>>>>>> ERROR! : Facebook Server Returned Error ")
            err = root.firstChildElement("error_code").text()
            if int(err) == 190 :
                self.queryFailed.emit()
                self.__notifications = -1
                self.authExpired.emit()
            print("\tError Code : " + err)
            print("\tError Message : " + root.firstChildElement("error_msg").text())
            
        elif root.tagName() == "fql_query_response" :           
            notificationList = root.elementsByTagName("notification")
            print("== Recived Query Result ==")
            print("\tTotal Notifications : " + str(notificationList.length()))
            
            for i in range(notificationList.length()) :
                notification = notificationList.at(i)
                print(unicode(notification.namedItem("title_html").toElement().text()))
                
                children = notification.namedItem("title_html").toElement().childNodes()
                print("title has " + str(children.length()) + " children")
                
                for j in range(children.length()) :
                    print(notificationList.at(i).nodeType())
                    print(children.at(j).nodeName())
                    
                if (int(notificationList.at(i).namedItem("anon").toElement().text()) - int(notificationList.at(i).namedItem("created_time").toElement().text())) <= self.settings["pollinterval"] :
                    print("\tNotification " + str(i) + " is New! Firing KNotification::event()")
                    #self.emit(SIGNAL("newNotification(QDomNode *)"), notificationList.at(i))
                    KNotification.event(KNotification.Notification, "You're Popular! :P",notificationList.at(i).namedItem("title_html").toElement().text(), QPixmap(self.settings["notification_icon"]))
                
        else :
            print(">>>>>>>> ERROR! : Facebook Server returned Unexpected Output : ")
            print(doc.toByteArray())
            
        if notificationList.length() != self.__notifications :
            self.__notifications = notificationList.length()
            self.notificationsChanged.emit()
            
    def checkNewNotifications(self) :
        self.__runQuery()
        
    def refreshNotifications(self) :
        self.__runQuery()
        
    def notifications(self) :
        return self.__notifications