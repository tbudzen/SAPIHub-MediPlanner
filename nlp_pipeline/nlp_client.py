import socket
import sys
import time

op_codes = ["PING", "REQUEST", "REQUESTALL", "TRAIN", "STAT", "STATUS", "SHUTDOWN"]
answers = ["OK", "PENDING", "FAILED"]

class NLPClient:

    server_host = "127.0.0.1"
    server_port = 20000

    def readAnswer(self, client_0):
        s_from = ""
        try:
            s_from = client_0.recv(32768)
        except ConnectionResetError as e:
            print("Connection reset by server.")
        return s_from

    def sendPing(self):

        time_1 = time.time()

        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((self.server_host, self.server_port))
        client.send(bytearray("PING      ", "utf-8"))

        s_from = self.readAnswer(client)
        s_from = str(s_from, "utf-8")

        print("Server response is: " + s_from)

        client.close()

        time_2 = time.time()

        t_delta = time_2 - time_1

        print("Total command time = " + str(t_delta) + " [s]")


    def sendShutdown(self):

        time_1 = time.time()

        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((self.server_host, self.server_port))
        client.send(bytearray("SHUTDOWN  ", "utf-8"))

        s_from = self.readAnswer(client)
        s_from = str(s_from, "utf-8")

        print("Server response is: " + s_from)

        client.close()

        time_2 = time.time()

        t_delta = time_2 - time_1

        print("Total command time = " + str(t_delta) + " [s]")

    def sendTrain(self):

        time_1 = time.time()

        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((self.server_host, self.server_port))
        client.send(bytearray("TRAIN     ", "utf-8"))

        s_from = self.readAnswer(client)
        s_from = str(s_from, "utf-8")

        print("Server response is: " + s_from)

        client.close()

        time_2 = time.time()

        t_delta = time_2 - time_1

        print("Total command time = " + str(t_delta) + " [s]")

    def sendStat(self):

        time_1 = time.time()

        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((self.server_host, self.server_port))
        client.send(bytearray("STAT      ", "utf-8"))

        s_from = self.readAnswer(client)
        s_from = str(s_from, "utf-8")

        print("Server response is: \n" + s_from)

        client.close()

        time_2 = time.time()

        t_delta = time_2 - time_1

        print("Total command time = " + str(t_delta) + " [s]")

    def sendStatus(self):

        time_1 = time.time()

        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((self.server_host, self.server_port))
        client.send(bytearray("STATUS    ", "utf-8"))

        s_from = self.readAnswer(client)
        s_from = str(s_from, "utf-8")

        print("Server response is: \n" + s_from)

        client.close()

        time_2 = time.time()

        t_delta = time_2 - time_1

        print("Total command time = " + str(t_delta) + " [s]")

    def sendRequest(self, fname):

        time_1 = time.time()

        f = open(fname, "r", encoding="utf-8", errors='ignore')
        s = f.readlines()
        f.close()

        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((self.server_host, self.server_port))
        client.send(bytearray("REQUEST   ", "utf-8"))
        client.send(bytearray("".join(s), "utf-8"))

        s_from = self.readAnswer(client)
        if s_from != "": s_from = str(s_from, "utf-8")

        client.close()

        time_2 = time.time()

        t_delta = time_2 - time_1

        print("Total command time = " + str(t_delta) + " [s]")

        print(s_from)

    def sendRequestAll(self):

        time_1 = time.time()

        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((self.server_host, self.server_port))
        client.send(bytearray("PROCESSALL", "utf-8"))

        s_from = self.readAnswer(client)
        if s_from != "": s_from = str(s_from, "utf-8")

        client.close()

        time_2 = time.time()

        t_delta = time_2 - time_1

        print("Total command time = " + str(t_delta) + " [s]")

        print(s_from)

if __name__ == "__main__":
    cnt = len(sys.argv)
    if cnt >= 2:
        opcode = sys.argv[1]
        if opcode in op_codes:
            pl = NLPClient()
            if cnt == 3:
                if opcode == "REQUEST":
                    fname = sys.argv[2]
                    pl.sendRequest(fname)
                else:
                    print("Unknown opcode: " + opcode)
            elif cnt == 2:
                if opcode == "PING":
                    pl.sendPing()
                elif opcode == "TRAIN":
                    pl.sendTrain()
                elif opcode == "PROCESSALL":
                    pl.sendRequestAll()
                elif opcode == "STAT":
                    pl.sendStat()
                elif opcode == "STATUS":
                    pl.sendStatus()
                elif opcode == "SHUTDOWN":
                    pl.sendShutdown()
                else:
                    print("Unknown opcode: " + opcode)