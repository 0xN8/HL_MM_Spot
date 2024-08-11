from tools.config import coinShort

class TokenInfo:
    def __init__(self, info):
        self.info = info
        self.tokens = self.getTokens()

    def getTokens(self):
        res = self.info.spot_meta()
        return {token['name']: token for token in res['tokens']}

    def getToken(self):
        if coinShort not in self.tokens:
            self.tokens = self.getTokens()
        return self.tokens.get(coinShort)