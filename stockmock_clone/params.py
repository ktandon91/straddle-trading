from datetime import datetime, time


class Params:
    def __init__(self, date="1/1/2019", entry_time="9:15:00", exit_time="3:15:00",
                 stop_loss=10, combined=False):
        self.date = datetime.strptime(date, "%d/%m/%Y")
        self.entry_hour = int(entry_time.split(":")[0])
        self.entry_minute = int(entry_time.split(":")[1])
        self.entry_second = int(entry_time.split(":")[2])
        self.entry_time = time(hour=self.entry_hour, minute=self.entry_minute, second=self.entry_second)
        self.exit_hour = int(exit_time.split(":")[0])
        self.exit_minute = int(exit_time.split(":")[1])
        self.exit_time = time(hour=self.exit_hour, minute=self.exit_minute)
        self.stop_loss = stop_loss


