import asyncio
import websockets
import commune as c

class WSClient(c.Module):
    
    
    def __init__(self,
                module = None,
                 ip = '0.0.0.0',
                 port:int=None,
                 verbose:bool = False,
                 key = None,
                 start:bool = True):
        if ':' in ip:
            ip, port = ip.split(':')
        self.ip = c.resolve_ip(ip)
        self.port = c.resolve_port(port)
        self.address = f'ws://{self.ip}:{self.port}'
        self.verbose = verbose
        self.key = c.get_key(key)
        self.serializer = c.module('serializer')()

    def resolve_address(cls, address=None):
        if address == None:
            address = self.address
        if not 'ws://' in address:
            address = f'ws://{address}'
        assert isinstance(address, str), f'address must be a string, not {type(address)}'
        return address

    async def async_forward(self, fn='info', args=None, kwargs=None, address=None):
        
        if args == None:
            args = []
        if kwargs == None:
            kwargs = {}
        
        data = {'fn':fn, 'args':args, 'kwargs':kwargs}
        data = self.serializer.serialize(data)
        address = self.resolve_address(address=address)
        response = ''
        async with websockets.connect(address) as websocket:
            await websocket.send(data)
            
            while True:
                new_element = await websocket.recv()
                if new_element == '<BREAK>':
                    break
                response += new_element
        
        c.print(response)
        response = self.serializer.deserialize(response)
              
        
        return response
    
    def forward(self, *args, **kwargs):
        return asyncio.get_event_loop().run_until_complete(self.async_forward(*args, **kwargs))

    @staticmethod
    async def recv(address):
        chunks = []
        async with websockets.connect(address) as websocket:
            chunk = await websocket.recv(address)
            chunks.append(chunk)
