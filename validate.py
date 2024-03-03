#Python script for validating bustabit games

#Feel free to donate :)
#https://bustabit.com/user/andreasviner

import hashlib
import hmac
import requests
import json
import binascii

APP_SLUG = 'bustabit'
GAME_SALT = '000000000000000000011f6e135efe67d7463dfe7bb955663ef88b1243b2deea'
COMMITMENT = '567a98370fb7545137ddb53687723cf0b8a1f5e93b1f76f4a1da29416930fa59'
VX_PUBKEY = 'b40c94495f6e6e73619aeb54ec2fc84c5333f7a88ace82923946fc5b6c8635b08f9130888dd96e1749a1d5aab00020e4'

def get_vx_signature(game_id, game_hash):
    vx_data = get_vx_data(APP_SLUG, game_id, COMMITMENT)
    signature = (vx_data['vx_signature'])
    return signature

def get_vx_data(app_slug, index, commitment):
    query = """
        query AppsMessagesByIndex($appSlug: String!, $index: Int!, $commitment: String!) {
          appBySlug(slug: $appSlug) {
            id
            name
            vx {
              messagesByIndex(commitment: $commitment, index: $index) {
                vx_signature
                message
              }
            }
          }
        }
    """

    response = requests.post('https://server.actuallyfair.com/graphql', headers={'Content-Type': 'application/json'}, data=json.dumps({
        'query': query,
        'variables': {
            'appSlug': app_slug,
            'index': index,
            'commitment': commitment,
        },
    }))

    if response.status_code != 200:
        print(f'Looks like there was a Vx lookup error. Status code: {response.status_code}, response body: {response.text}')
        return None

    json_response = response.json()
    if 'errors' in json_response:
        print(f'There was a Vx error: {json_response["errors"][0]["message"]}')
        return None

    return json_response['data']['appBySlug']['vx']['messagesByIndex'][0]

def game_result(game_hash, nr):
    vx_signature = (get_vx_signature(nr, game_hash))
    n_bits = 52
    hash = hmac.new(bytes.fromhex(vx_signature), bytes.fromhex(game_hash), hashlib.sha256).hexdigest()
    seed = hash[:n_bits // 4]
    r = int(seed, 16)
    X = r / 2**n_bits
    X = 99 / (1 - X)
    result = int(X)
    return max(1, result / 100)



class game_history:
    def __init__(self, ghash, game_nr, iterations = 10):
        self.ghash = ghash
        self.game_nr = game_nr
        self.iterations = iterations

    def __iter__(self):
        return self

    def __next__(self):
        if self.iterations == 0:
            raise StopIteration

        crash = game_result(self.ghash, self.game_nr)

        self.ghash = hashlib.sha256(bytes.fromhex(self.ghash)).hexdigest()
        self.game_nr -= 1
        self.iterations -= 1
        
        return crash
        


if __name__ == "__main__":

    ghash = "61729963ca9d3e3292a43c310444e530c62662bd1647e8158897ea7537bed229"
    game_nr = 10022538

    print("Should print 4.04 if everythings working...")
    print(game_result(ghash, game_nr))

    print("\nPringing last 10 games.....")
    for crash in game_history(ghash, game_nr, 10):
        print(crash)
    



