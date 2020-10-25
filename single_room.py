from autobahn.twisted.websocket import WebSocketServerProtocol, \
    WebSocketServerFactory

from json import loads, dumps

#Todo
#*Remove duplicate code
#*Add broadcast function for multi-user messaging
#*Validate each packet

users = {}
rooms = ['main', 'right1']

class MyServerProtocol(WebSocketServerProtocol):

    def onConnect(self, request):
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

    def _join(self, data, payload, isBinary):

        user_data = data['data']
        username = user_data['username']
        room = user_data['room']

        if users.get(username):
           print('Username taken. Disconnecting client..')
           self.close()
           return

        if room not in rooms:
           print('Invalid room. Disconnecting')
           if getattr(self, 'room'):
              try:
                 del users[self.room][username]
              except Exception as e:
                 pass
           self.close()
           return

        users[room][username] = (self, user_data)

        for _, user in users.items():
            if user[0] != self:
               user[0].sendMessage(payload, isBinary)

        self.username = username

        print('User %s has joined!' % username)
        print('User Count: %s' % len(users))

    def _move(self, data, payload, isBinary):

        username = data['username']
        users[username][1]['direction'] = data['direction']
        users[username][1]['shape']['x'] = data['sx2']
        users[username][1]['shape']['y'] = data['sy2']

        for _, user in users.items():
            if user[0] != self:
               user[0].sendMessage(payload, isBinary)

    def _message(self, data, payload, isBinary):
        for _, user in users.items():
            if user[0] != self:
               user[0].sendMessage(payload, isBinary)

    def _users(self, data, payload, isBinary):
        user_list = []

        for _, user in users.items():
            if user[0] != self:
               user_list.append(user[1])

        self.sendMessage(dumps({'users': user_list, 'type': 'users'}).encode(), isBinary)

    def onClose(self, wasClean, code, reason):

        print("WebSocket connection closed: {0}".format(reason))

        del users[self.username]

        print('User Count: %s' % len(users))

        for _, user in users.items():
            user[0].sendMessage(dumps({'type': 'leave', 'username': self.username, 'room': self.room}).encode(), False)

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
