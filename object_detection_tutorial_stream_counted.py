import numpy as np
import tensorflow as tf
import os
import sys
import cherrypy
import threading
import cv2

from services import CCTVService

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
    # Start Web Service
    cond = threading.Condition()
    service = CCTVService(cond, b'', {})
    cherrypy.server.socket_host = sys.argv[2]
    cherrypy.server.socket_port = int(sys.argv[3])
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
    cap = cv2.VideoCapture(sys.argv[1])

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
                service.data = {"streamInfo":{"OBJECTID":"","name":"", "address":"", "ip_source":"", "ip_detection":"", "lon":0.0, "lat":0.0}, "data":data}
                _, jpeg_bytes_tmp = cv2.imencode('.jpg', image_np) # to jpeg
                service.jpeg_bytes = jpeg_bytes_tmp.tobytes()
                
                cond.acquire()
                cond.notifyAll()
                cond.release()

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage:\r\n  python object_detection_tutorial_stream_counted.py <NETWORK_CCTV_ADDRESS> <bind_address> <bind_port>")
        sys.exit(1) 
    main()
   #param 1 camera cctv address 'http://114.110.17.6:8896/image.jpg?type=motion&camera=1'
   #param 2 bind address
   #param 3 bind port