import socket
import math
import time
import sys

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 11000
LANE_WIDTH = 1.06
LANE_LENGTH = 5.0
STEP_DELAY = 0.02
INITIAL = {
    "p": LANE_WIDTH / 2, # position
    "s": 1.0, # speed
    "a": 0.0, # angle
    "i": 0.0, # spin
}

class PositionClient:

    def __init__(self, host, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.address = (host, port)

    def send(self, x, y):
        self.sock.sendto(self.encode(x, y), self.address)

    def encode(self, x, y):
        return "{:f},{:f}".format(x, y).encode("UTF-8")

class TrajectoryGenerator:

    def __init__(self, client, config):
        self.client = client
        self.x = config["p"]
        self.y = 0
        self.s = config["s"]
        self.a = math.radians(config["a"])
        self.i = math.radians(config["i"])

    def step(self, sec):
        d = sec * self.s
        self.x += math.sin(self.a) * d
        self.y += math.cos(self.a) * d
        self.a += sec * self.i
        return sec

    def roll(self):
        t = time.time()
        while self.onLane():
            self.client.send(self.x / LANE_WIDTH, self.y / LANE_LENGTH)
            t += self.step(time.time() - t)
            time.sleep(STEP_DELAY)

    def onLane(self):
        return (
            self.y >= 0 and self.y <= LANE_LENGTH
            and self.x >= 0 and self.x <= LANE_WIDTH
        )

class CommandUI:

    def __init__(self, host, port, initial):
        self.client = PositionClient(host, port)
        self.config = initial.copy()

    def printWelcome(self):
        print("Generates bowling ball trajectories for testing.\n"
            "Sends position in UDP to {}:{:d}".format(*self.client.address))

    def printUsage(self):
        print("Type: a=-5.1[enter], plain [enter] to roll, q[enter] to exit")

    def mainLoop(self):
        self.printWelcome()
        self.printUsage()
        on = True
        names = ("p", "s", "a", "i")
        while on:
            print("(p)osition={:.2f}m width (s)peed={:.2f}m/s "
                "(a)ngle={:.2f}° sp(i)n={:.2f}°/s".format(
                    *(self.config[n] for n in names)))
            try:
                cmd = input("# ").strip()
                if not cmd:
                    print("Roll!")
                    TrajectoryGenerator(self.client, self.config).roll()
                elif cmd == "q":
                    on = False
                elif cmd[1:2] == "=" and cmd[0] in names:
                    self.adjust(cmd[0], cmd[2:])
                else:
                    self.printUsage()
            except EOFError:
                on = False

    def adjust(self, name, source):
        try:
            self.config[name] = float(source)
        except ValueError:
            pass

if __name__ == "__main__":
    print("Usage {} [host] [port]".format(sys.argv[0]))
    host = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_HOST
    port = int(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_PORT
    ui = CommandUI(host, port, INITIAL)
    ui.mainLoop()
