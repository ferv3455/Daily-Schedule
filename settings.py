import pickle

class Settings:
    def __init__(self, shutdown=1, darkmode=1):
        self.shutdown = shutdown
        self.darkmode = darkmode

    def loadFile(self, filename):
        with open(filename, "rb") as fin:
            settings = pickle.load(fin)
            self.shutdown = settings.shutdown
            self.darkmode = settings.darkmode

    def dumpFile(self, filename):
        with open(filename, "wb") as fout:
            pickle.dump(self, fout)

if __name__ == "__main__":
    with open("settings.dat", "wb") as fout:
        s = Settings()
        pickle.dump(s, fout)
