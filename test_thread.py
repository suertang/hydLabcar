import threading
import time
def main():
    d=DownThread()

    t=threading.Thread(target=d.run)
    t2=threading.Thread(target=d.run)
    t.start()
    time.sleep(1)
    t2.start()
    #thid2=_thread.start_new_thread(dadada,())
    time.sleep(10)
    d.terminate()
    t.join()
    t2.join()
    print("done")

class DownThread:
    def __init__(self):
        self._running = True

    def terminate(self):
        self._running = False

    def run(self):
        while(self._running):
            print("a ! ")
            time.sleep(2)

    

if __name__=="__main__":
    main()