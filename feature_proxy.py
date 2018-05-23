import cherrypy, requests, json, time

template = {}
INTERNAL_FEATURE_ADDRESS = [ 
    "172.27.100.181:9091/stream",
    "172.27.100.181:9092/stream",
    "172.27.100.181:9093/stream",
    "172.27.100.181:9094/stream",
    "172.27.100.181:9095/stream",
    "172.27.100.181:9096/stream",
    "172.27.100.181:9097/stream",
    "172.27.100.181:9098/stream",
    "172.27.100.181:9099/stream"
]

class FeatureProxy(object):
    def index(self):
        """ Return a Esri JSON Feature """
        for feature in INTERNAL_FEATURE_ADDRESS:
            fjson = requests.get(feature).json()
            template["features"].append(fjson)
        return json.dumps(template)
    index.exposed = True
    
if __name__ == "__main__":
    with open("template.json", "r") as file:
        template = json.load(file)
    cherrypy.server.socket_host = "localhost"
    cherrypy.server.socket_port = 9000
    cherrypy.quickstart(FeatureProxy())
    