class Machine:
    def __init__(self):
        self.states = ['in', 'out', 'wait', 'on', 'err']
        self.cur_state = 'wait'
    def sensorFeed(self, data):
        if self.cur_state == 'wait':
            if data == 2:
                self.cur_state = 'in'
            elif data == 1 or data == 3:
                self.cur_state = 'err'
        elif self.cur_state == 'in':
            if data == 3:
                self.cur_state = 'on'
            elif data == 0 or data == 1:
                self.cur_state = 'err'
        elif self.cur_state == 'on':
            if data == 1:
                self.cur_state = 'out'
            elif data == 0 or data == 2:
                self.cur_state = 'err'
        elif self.cur_state == 'out':
            if data == 0:
                self.cur_state = 'wait'
            elif data == 2 or data == 3:
                self.cur_state = 'err'
        elif self.cur_state == 'err':
            if data == 0:
                self.cur_state = 'wait'
