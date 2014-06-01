class GlobalParams():
    debug = False
    mute = False

    @staticmethod
    def setDebug(debug):
        GlobalParams.debug = debug

    @staticmethod
    def isDebug():
        return GlobalParams.debug

    @staticmethod
    def setMute(mute):
        GlobalParams.mute = mute

    @staticmethod
    def isMute():
        return GlobalParams.mute