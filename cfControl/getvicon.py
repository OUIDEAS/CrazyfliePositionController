from viconStream import viconStream
print('worked')

thing = viconStream('CF_1')
thing.vicon_connect()



while True:
    thing.getPos()

