import sys
import os

def detection_histogram(scores, classes, category_index):
    i = 0
    result = {"person":0, "bicycle":0, "car":0, "motorcycle":0, "bus":0, "train":0, "truck":0}
    while(scores[i]>0.4 and i < scores.size):
        try:
            result[ category_index[classes[i]]["name"] ] = result[ category_index[classes[i]]["name"] ] + 1
        except KeyError:
            pass
        i = i + 1
    return result

def main():
    import numpy as np
    import tensorflow as tf
    import cherrypy
    import threading
    import cv2

    from services import CCTVService

    BIND_ADDRESS = sys.argv[1]
    BIND_PORT = int(sys.argv[2])
    EXTERNAL_ADDRESS = BIND_ADDRESS if sys.argv[3] == "0" else sys.argv[3]
    EXTERNAL_PORT = BIND_PORT if sys.argv[4] == "0" else sys.argv[4]
    VIDEO_STREAM_SOURCE_URL = sys.argv[5]
    OBJECTID = int(sys.argv[6])
    CCTV_NAME = sys.argv[7]
    CCTV_ADDRESS =  sys.argv[8]
    VIDEO_STREAM_DETECTION_URL = EXTERNAL_ADDRESS+":"+str(EXTERNAL_PORT)+"/stream"
    CCTV_HEIGHT = int(sys.argv[9])
    CCTV_LON = float(sys.argv[10])
    CCTV_LAT = float(sys.argv[11])
    
    # Start Web Service
    cond = threading.Condition()
    service = CCTVService(cond, b'', {})
    cherrypy.server.socket_host = BIND_ADDRESS
    cherrypy.server.socket_port = BIND_PORT
    server = threading.Thread(target=cherrypy.quickstart, args=[service])
    server.start()

    PATH_TO_MODELS = os.path.join("..","models")
    sys.path.append(os.path.join(sys.path[0], PATH_TO_MODELS, "research"))
    sys.path.append(os.path.join(sys.path[0], PATH_TO_MODELS, "research", "object_detection"))
    
    from utils import label_map_util
    from utils import visualization_utils as vis_util

    MODEL_NAME = 'ssd_mobilenet_v1_coco_2017_11_17'
    PATH_TO_CKPT = os.path.join(sys.path[0], PATH_TO_MODELS, "research", "object_detection", MODEL_NAME, "frozen_inference_graph.pb")
    PATH_TO_LABELS = os.path.join(sys.path[0], PATH_TO_MODELS, "research", "object_detection", "data", "mscoco_label_map.pbtxt")
    NUM_CLASSES = 90

    detection_graph = tf.Graph()
    with detection_graph.as_default():
        od_graph_def = tf.GraphDef()
        with tf.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
            serialized_graph = fid.read()
            od_graph_def.ParseFromString(serialized_graph)
            tf.import_graph_def(od_graph_def, name='')

    label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
    categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=NUM_CLASSES, use_display_name=True)
    category_index = label_map_util.create_category_index(categories)
    cap = cv2.VideoCapture(VIDEO_STREAM_SOURCE_URL)

    with detection_graph.as_default():
        with tf.Session(graph=detection_graph) as sess:
            while True:
                ret, image_np = cap.read()
                image_np_expanded = np.expand_dims(image_np, axis=0)
                image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')
                boxes = detection_graph.get_tensor_by_name('detection_boxes:0')
                scores = detection_graph.get_tensor_by_name('detection_scores:0')
                classes = detection_graph.get_tensor_by_name('detection_classes:0')
                num_detections = detection_graph.get_tensor_by_name('num_detections:0')
                # Actual detection.
                (boxes, scores, classes, num_detections) = sess.run(
                    [boxes, scores, classes, num_detections],
                    feed_dict={image_tensor: image_np_expanded})
                # Visualization of the results of a detection.
                vis_util.visualize_boxes_and_labels_on_image_array(
                    image_np,
                    np.squeeze(boxes),
                    np.squeeze(classes).astype(np.int32),
                    np.squeeze(scores),
                    category_index,
                    use_normalized_coordinates=True,
                    line_thickness=2,
                    min_score_thresh=.4)
                data = detection_histogram(np.squeeze(scores), np.squeeze(classes).astype(np.int32), category_index)
                service.data = {"geometry":{"x":CCTV_LON, "y":CCTV_LAT},"attributes": {**{"OBJECTID":OBJECTID,"name":CCTV_NAME, "address":CCTV_ADDRESS, "source_url":VIDEO_STREAM_SOURCE_URL, "ip_detection":VIDEO_STREAM_DETECTION_URL}, **data}}
                _, jpeg_bytes_tmp = cv2.imencode('.jpg', image_np) # to jpeg
                service.jpeg_bytes = jpeg_bytes_tmp.tobytes()
                
                cond.acquire()
                cond.notifyAll()
                cond.release()

if __name__ == "__main__":
    if len(sys.argv) != 12:
        print("Usage:\r\n  python object_detection_tutorial_stream_counted.py "+
            "<BIND_ADDRESS> <BIND_PORT> <EXTERNAL_ADDRESS> <EXTERNAL_PORT> <VIDEO_STREAM_SOURCE_URL> "+
            "<OBJECTID> <CCTV_NAME> <CCTV_ADDRESS> <CCTV_HEIGHT> <CCTV_LON> <CCTV_LAT>")
        sys.exit(1)
    main()