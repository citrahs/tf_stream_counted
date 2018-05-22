import cherrypy
import json, time

class CCTVService(object):
    jpeg_bytes = b''
    data = {}
    cond = ""
    def __init__(self, cond, image_bytes, count_data):
        self.jpeg_bytes = image_bytes
        self.data = count_data
        self.cond = cond
    def index(self):
        return "Hello World!"
        
    def count(self):
        return json.dumps(self.data)
        
    def stream(self):
        boundary="hehehe"
        cherrypy.response.headers['Content-Type'] = 'multipart/x-mixed-replace;boundary='+boundary  # see http://stackoverflow.com/questions/20837460/firefox-doesnt-restore-server-sent-events-connection
        cherrypy.response.headers['Connection'] = 'Keep-Alive'         # see http://cherrypy.readthedocs.org/en/latest/advanced.html#how-streaming-output-works-with-cherrypy
        cherrypy.response.headers['Keep-Alive'] = 'Timeout=60000'         # see http://cherrypy.readthedocs.org/en/latest/advanced.html#how-streaming-output-works-with-cherrypy
        
        def always_hehe():
            yield ("--"+boundary).encode('UTF-8')
            while True:
                
                yield "\r\nContent-Type: image/jpeg\r\n".encode('UTF-8')
                yield ("Content-Length: " + str(len(self.jpeg_bytes))).encode('UTF-8')
                yield "\r\n\r\n".encode('UTF-8')
                self.cond.acquire()
                self.cond.wait()
                self.cond.release()
                yield self.jpeg_bytes
                yield ("--"+boundary).encode('UTF-8')
                
        return always_hehe()
    index.exposed = True
    count.exposed = True
    stream.exposed = True
    stream._cp_config = {'response.stream': True}

#cherrypy.quickstart(CCTVService())
