from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtNetwork import *
from PyKDE4.plasma import Plasma
from PyKDE4.kdecore import KStandardDirs, KSharedConfig, KConfigGroup
from PyKDE4 import plasmascript
from auth import AuthenticationManager
from facebook import FacebookManager
import popen2


class FacebookWidget(plasmascript.Applet):   
    def __init__(self,parent,args=None):
        plasmascript.Applet.__init__(self,parent)
        
    sharedconfig = None
    
    
    def init(self):       
        self.setHasConfigurationInterface(False)
        self.resize(125, 125)
        self.setAspectRatioMode(Plasma.Square)
        self.setBackgroundHints(Plasma.Applet.TranslucentBackground)
        self.layout = QGraphicsLinearLayout(self.applet)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.layout.setOrientation(Qt.Horizontal)
        self.background = Plasma.IconWidget()
        self.layout.addItem(self.background)
        
        print(self.config().config().name())
        
        popen2.Popen3("xdg-icon-resource install --size 128 facebook_icon.png facebook-plasmoid")
                      
        self.initSettings()
        
        self.background.clicked.connect(self.onClick)
        
        self.authManager = AuthenticationManager(self.settings)
        self.fbManager = FacebookManager(self.settings)
        
        self.timer = QTimer()
        self.timer.setInterval(self.settings["pollinterval"] * 1000)
        
        self.timer.timeout.connect(self.fbManager.checkNewNotifications)
        self.fbManager.notificationsChanged.connect(self.updateIcon)
        self.fbManager.authExpired.connect(self.authManager.reauthenticate)
        self.authManager.accessTokenChanged.connect(self.fbManager.updateQueries)
        self.authManager.accessTokenChanged.connect(self.writeSettings)
        self.fbManager.queryFailed.connect(self.onQueryFail)
        
        self.updateIcon(0)
        self.fbManager.refreshNotifications()
        self.timer.start()
        
    def onClick(self) :
        print("== Icon Clicked == ")
        cmd = str(self.settings["browser"]) + " http://www.facebook.com/"
        print("\tLaunching : " + cmd)
        popen2.Popen3(cmd)
#	popen2.Popen3("xdg-open http://www.facebook.com/")
        
    def onQueryFail(self) :
        self.updateIcon(" ")

    def updateIcon(self, notifications) :
        pix = QPixmap(self.settings["background_icon"])
        canvas = QPainter(pix)
        canvas.setRenderHint(QPainter.SmoothPixmapTransform)
        canvas.setRenderHint(QPainter.Antialiasing)
        rect = pix.rect()
        
        canvas.setPen(Qt.red)
        factor = rect.height() / canvas.fontMetrics().height()
        f = canvas.font()
        f.setPointSizeF(f.pointSizeF()*factor)
        canvas.setFont(f)
        canvas.drawText(rect, Qt.AlignVCenter | Qt.AlignHCenter, str(notifications))
        canvas.end()
        
        self.background.setIcon(QIcon(pix))
        self.background.update()
        
    #def writeDefaults(self, path) :
        #c = []
        #c.append("pollinterval=3")
        #c.append("notification_icon=" + unicode(self.package().path()) + "contents/facebook_icon.svg")
        #c.append("background_icon=" + unicode(self.package().path()) + "contents/facebook_icon.svg")
        #c.append("browser=xdg-open")
        
        
    def writeSettings(self) :
        settings = self.settings
        
        cg = self.config()
        cg.writeEntry("access_token", settings["access_token"])
        cg.writeEntry("pollinterval", settings["pollinterval"])
        cg.writeEntry("notification_icon", settings["notification_icon"])
        cg.writeEntry("background_icon", settings["background_icon"])
        cg.writeEntry("browser", settings["browser"])
            
        cg.sync()
        
    def initSettings(self) :
        print("In FacebookWidget::initSettings():")
        cg = self.config()
        #cg.sync()
        settings = {}
        settings["access_token"] = cg.readEntry("access_token", "").toString()
        settings["pollinterval"] = int(cg.readEntry("pollinterval", "3").toString())
        settings["notification_icon"] = cg.readEntry("notification_icon", unicode(self.package().path()) + "contents/facebook_icon.svg").toString()
        settings["background_icon"] = cg.readEntry("background_icon", unicode(self.package().path()) + "contents/facebook_icon.svg").toString()
        settings["browser"] = cg.readEntry("browser", "xdg-open").toString()
        #self.writeSettings(settings)
        #c.append("access_token=")
        
        #self.settings["access_token"] = self.authManager.accessToken()
        #3
        #self.settings["notification_body_element"] =
        #self.settings["notificatoin_title_element"]
        #settings["notification_icon"] = unicode(self.package().path()) + "contents/facebook_icon.svg"
        #unicode(self.package().path()) + "contents/facebook_icon.svg"
        #"weblaunch"
        #""
        #print(self.settings["pollinterval"])
        #print(self.settings["pollinterval"])
        self.settings = settings
        
    def config(self) :
        if self.sharedconfig == None :
            rcpath = KStandardDirs.locateLocal("config", "fb-plasmoidrc")
            self.sharedconfig = KSharedConfig.openConfig(rcpath)
            
            self.initSettings()
            self.writeSettings()
        
        return KConfigGroup(self.sharedconfig, "main")
        
    #def configChanged(self) :
        #self.settings = self.initSettings()
        
        
    #def __del__(self) :
        #self.writeSettings(self.settings)
        
#end FacebookWidget                
 
def CreateApplet(parent):
    return FacebookWidget(parent)
        
    
#https://graph.facebook.com/oauth/access_token?client_id=172712822755160&client_secret=70fcd4802f2a54e77c843d08b56189a5&grant_type=client_credentials
#https://www.facebook.com/dialog/oauth?client_id=172712822755160&redirect_uri=http://www.facebook.com/connect/login_success.html&access_type=client_credentials

#SELECT notification_id, sender_id, title_html, body_html, href FROM notification WHERE recipient_id=me() AND is_unread = 1 AND is_hidden = 0
