class Machine:
    def __init__(self):
        self.states = ['out', 'wait', 'analyze', 'on', 'err']
        self.cur_state = 'wait'
        self.state_count = 0
    def sensorFeed(self, data):
        if self.cur_state == 'wait':
            if data == 2:
                self.cur_state = 'on'
                self.state_count = 0
            elif data == 1 or data == 3:
                self.cur_state = 'err'
                self.state_count = 0
            else:
                self.state_count += 1
        elif self.cur_state == 'on':
            if data == 1:
                self.cur_state = 'analyze'
                self.state_count = 0
            elif self.state_count > 20:
                self.cur_state = 'err'
                self.state_count = 0
            else:
                self.state_count += 1
        elif self.cur_state == 'analyze':
            self.cur_state = 'out'
        elif self.cur_state == 'out':
            if data == 0:
                self.cur_state = 'wait'
                self.state_count = 0
            elif data == 2 or data == 3:
                self.cur_state = 'err'
                self.state_count = 0
            else:
                self.state_count += 1
        elif self.cur_state == 'err':
            if data == 0:
                self.cur_state = 'wait'
                self.state_count = 0
            else:
                self.state_count += 1
