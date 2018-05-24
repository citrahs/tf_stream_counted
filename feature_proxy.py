import cherrypy, requests, json, time, copy

template = {}
INTERNAL_FEATURE_ADDRESS = [ 
    "http://172.27.100.181:9090/count",
    "http://172.27.100.181:9091/count",
    "http://172.27.100.181:9092/count",
    "http://172.27.100.181:9093/count",
    "http://172.27.100.181:9094/count",
    "http://172.27.100.181:9095/count",
    "http://172.27.100.181:9096/count",
    "http://172.27.100.181:9097/count",
    "http://172.27.100.181:9098/count",
    "http://172.27.100.181:9099/count",
    "http://172.27.100.181:9100/count",
    "http://172.27.100.181:9101/count"
]

class FeatureProxy(object):
    def index(self):
        """ Return a Esri JSON Feature """
        template_copy = []
        for feature in INTERNAL_FEATURE_ADDRESS:
            fjson = {}
            try:
                req = requests.get(feature, timeout=0.0007)
                fjson = req.json()
                if len(fjson)>0:
                    template_copy["features"].append(fjson)
            except:
                print("exceptione")
                pass
        return json.dumps(template_copy)
    index.exposed = True
    
if __name__ == "__main__":
    cherrypy.server.socket_host = "172.27.100.181"
    cherrypy.server.socket_port = 8080
    cherrypy.quickstart(FeatureProxy())
    
