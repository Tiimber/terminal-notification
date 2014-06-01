class GlobalParams():
    debug = False
    mute = False

    @staticmethod
    def set_debug(debug):
        GlobalParams.debug = debug

    @staticmethod
    def is_debug():
        return GlobalParams.debug

    @staticmethod
    def set_mute(mute):
        GlobalParams.mute = mute

    @staticmethod
    def is_mute():
        return GlobalParams.mute