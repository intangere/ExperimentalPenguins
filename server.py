from autobahn.twisted.websocket import WebSocketServerProtocol, \
    WebSocketServerFactory

from json import loads, dumps

#Todo
#*Remove duplicate code
#*Add broadcast function for multi-user messaging
#*Validate each packet
#* Validate room size when a user is moving
#** This needs to map to both the client and server from some config?

users = {'rooms': {}}
rooms = ['main', 'right1']

for room in rooms:
    users['rooms'][room] = {}

users['in_use'] = []


# MESSAGE LENGTH VERIFY
# ROOMVERIFY() UNCTOIN
# SOME ENCRYPTION MAYBE
# MSGPACK
#MONADS

class MyServerProtocol(WebSocketServerProtocol):

    def onConnect(self, request):
        self.username = None
        print("Client connecting: {0}".format(request.peer))

    def onOpen(self):
        print("WebSocket connection open.")

    def onMessage(self, payload, isBinary):
        if isBinary:
            print("Binary message received: {0} bytes".format(len(payload)))
        else:
            data = loads(payload.decode('utf8'))

            print('Received JSON: %s' % data)

            _type = data['type']

            try:
               getattr(self, '_%s' % _type)(data, payload, isBinary)
            except Exception as e:
               print(e)
               print('Not recognized')

    def _username(self, data, payload, isBinary):

        username = data['username']

        print('User registering as %s' % username)

        if not username or len(username) > 15:
           self.sendMessage(dumps({'type': 'username', 'error': 'Username is invalid'}).encode(), isBinary)
           self.transport.loseConnection()
           return

        if not username in users['in_use']:
           users['in_use'].append(username)
           self.username = username
           self.sendMessage(dumps({'type': 'username', 'accepted': True}).encode(), isBinary)
        else:
           self.sendMessage(dumps({'type': 'username', 'error': 'Username is taken'}).encode(), isBinary)
           self.transport.loseConnection()

    def _join(self, data, payload, isBinary):

        user_data = data['data']
        username = user_data['username']
        room = user_data['room']

        if room not in rooms:
           print('Invalid room. Disconnecting')
           self.close()
           return

        if getattr(self, 'username', None):
           self.removeUserFromRooms()

        users['rooms'][room][username] = (self, user_data)

        for _, user in users['rooms'][room].items():
            if user[0] != self:
               user[0].sendMessage(payload, isBinary)

        print('User %s has joined!' % username)

        for room, _users in users['rooms'].items():
            print('%s User Count: %s' % (room, len(_users)))


    def _move(self, data, payload, isBinary):

        username = data['username']
        room = data['room']

        users['rooms'][room][username][1]['direction'] = data['direction']
        users['rooms'][room][username][1]['shape']['x'] = data['sx2']
        users['rooms'][room][username][1]['shape']['y'] = data['sy2']

        for _, user in users['rooms'][room].items():
            if user[0] != self:
               user[0].sendMessage(payload, isBinary)

    def _message(self, data, payload, isBinary):

        room = data['room']

        for _, user in users['rooms'][room].items():
            if user[0] != self:
               user[0].sendMessage(payload, isBinary)

    def _users(self, data, payload, isBinary):
        user_list = []

        room = data['room']

        for _, user in users['rooms'][room].items():
            if user[0] != self:
               user_list.append(user[1])

        self.sendMessage(dumps({'users': user_list, 'type': 'users'}).encode(), isBinary)

    def removeUserFromRooms(self):
        for room, _users in users['rooms'].items():
            if self.username in _users:
               del users['rooms'][room][self.username]
               for _, user in _users.items():
                   user[0].sendMessage(dumps({'type': 'leave', 'username': self.username, 'room': room}).encode(), False)

    def onClose(self, wasClean, code, reason):

        print("WebSocket connection closed: {0}".format(reason))

        #del users[self.username]

        #if getattr(self, 'username', None):
        self.removeUserFromRooms()

        if getattr(self, 'username'):
           users['in_use'].remove(self.username)

        print('User Count: %s' % len(users['in_use']))

if __name__ == '__main__':

    import sys

    from twisted.python import log
    from twisted.internet import reactor

    log.startLogging(sys.stdout)

    factory = WebSocketServerFactory(u"ws://127.0.0.1:9000")
    factory.protocol = MyServerProtocol
    # factory.setProtocolOptions(maxConnections=2)

    # note to self: if using putChild, the child must be bytes...

    reactor.listenTCP(9000, factory)
    reactor.run()
