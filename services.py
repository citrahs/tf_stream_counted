import cherrypy, json, time

class CCTVService(object):
    def __init__(self, cond, image_bytes, count_data):
        """ Initialize this object with cond lock for waiting new data, 
            image bytes for the jpeg encoded image, and 
            count data for the object count.
        """
        self.jpeg_bytes = image_bytes
        self.data = count_data
        self.cond = cond
        
    def index(self):
        """ Main index page """
        return "Esri Indonesia"
        
    def count(self):
        """ Return dynamic JSON objects that tells about detection result """
        return json.dumps(self.data)
        
    def stream(self):
        """ Object detection mjpeg streaming services """
        boundary = "hehehe"
        
        cherrypy.response.headers['Content-Type'] = 'multipart/x-mixed-replace;boundary='+boundary
        cherrypy.response.headers['connection'] = 'Keep-Alive'
        cherrypy.response.headers['keep-alive'] = 'Timeout=60000'
        boundaryPlus = "--"+boundary
        contentTypeString = "\r\nContent-Type: image/jpeg\r\n"
        
        def mjpeg():
            """ Mjpeg stream generator. Will wait for incoming new data
                from the main program.
            """
            yield boundaryPlus.encode('UTF-8')
            while True:
                yield contentTypeString.encode('UTF-8')
                yield ("Content-Length: " + str(len(self.jpeg_bytes))).encode('UTF-8')
                yield "\r\n\r\n".encode('UTF-8')
                self.cond.acquire()
                self.cond.wait()
                yield self.jpeg_bytes
                self.cond.release()
                yield boundaryPlus.encode('UTF-8')
        return mjpeg()
        
    index.exposed = True
    count.exposed = True
    stream.exposed = True
    stream._cp_config = {'response.stream': True}