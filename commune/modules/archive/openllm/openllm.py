import commune as c

class Openllm(c.Module):
    def __init__(self, **kwargs):
        config = self.set_config(config=kwargs)
    def run(self):
        print('Base run')
    