class TokenInfo:
    def __init__(self, info):
        self.info = info
        self.tokens = self._get_tokens()

    def _get_tokens(self):
        res = self.info.spot_metadata()
        return {token['name']: token for token in res['tokens']}

    def get_token(self, coin_short):
        if coin_short not in self.tokens:
            self.tokens = self._get_tokens()
        return self.tokens.get(coin_short)