import threadedServer

if __name__ == '__main__':
    procID = 0
    if len(sys.argv) > 1:
        procID = int(sys.argv[1])
    threadedServer.main(procID)