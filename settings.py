import pickle

class Settings:
    def __init__(self, shutdown=1, darkmode=1):
        self.shutdown = shutdown
        self.darkmode = darkmode

if __name__ == "__main__":
    with open("settings.dat", "wb") as fout:
        s = Settings()
        pickle.dump(s, fout)
