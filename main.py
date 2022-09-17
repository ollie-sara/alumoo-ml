import numpy as np
import peewee as pw
from flask import Flask, Response
from db_model import *
from sklearn.cluster import KMeans
import json
import time
import threading

app = Flask(__name__)

pagesize = 15

psdb = pw.PostgresqlDatabase(host='34.65.191.37', port='5432', database='alumoo', user='postgres', password='postgres')
task_clusters = {}
volunteer_clusters = {}

@app.route("/<int:vID>/<int:pg>")
def serve(vID, pg):
    if vID not in volunteer_clusters.keys():
        computeClusters()
        if Volunteers.select().where(Volunteers.volunteer_id == vID).count() <= 0:
            return 'Invalid user ID', 400
    out = {'taskIds': ','.join([str(x) for x in getSortedTaskIds(vID, pg)])}
    return Response(json.dumps(out), mimetype='application/json')

def computeClusters():
    numtasks = Tasks.select().count()

    points = (Tasks
            .select(Tasks.task_id.alias('pid'), Tasks.skills)
            .union_all(Volunteers.select(Volunteers.volunteer_id.alias('pid'), Volunteers.skills)))
    inpt = [(int(p.pid), [float(x) for x in p.skills.split(',')]) for p in points.execute()]

    bestscore = 9999999
    mapping = None
    for i in range(5):
        kmeans = KMeans(n_clusters=i+1, init='k-means++')
        fit = kmeans.fit([x[1] for x in inpt])
        if bestscore > fit.inertia_:
            mapping = kmeans
            bestscore = fit.inertia_
    mapping = mapping.fit_predict([x[1] for x in inpt])
    i = 0
    for mp in mapping[:numtasks]:
        task_clusters[inpt[i][0]] = mp
        i += 1
    for mp in mapping[numtasks:]:
        volunteer_clusters[inpt[i][0]] = mp
        i += 1
    
    print('Clusters recomputed.')

def calculateDistance(skills, point):
    skills = [float(x) for x in skills.split(',')]
    point = [float(x) for x in point.split(',')]
    return np.dot(skills, point)

def getSortedTaskIds(vID, pg):
    if pg < 0:
        return
    center = volunteer_clusters[vID]
    point = Volunteers.select(Volunteers.skills).where(vID == Volunteers.volunteer_id).execute()[0].skills
    tasksInCluster = Tasks.select(Tasks.task_id, Tasks.skills).where(Tasks.task_id << list(filter(lambda x: task_clusters[x] == center, task_clusters.keys()))).execute()
    output = list(zip(*sorted([(x.task_id, calculateDistance(x.skills, point)) for x in tasksInCluster], key=lambda x:x[1])))[0]
    return output[(pagesize*pg)%len(output):(pagesize*(pg+1))%len(output)]

def loop():
    print('Started background loop.')
    starttime = time.time()
    delay = 20.0
    task = None
    while True:
        if task is not None:
            task.cancel()
        computeClusters()
        time.sleep(delay - ((time.time() - starttime) % delay))    

thread1 = threading.Thread(target=loop)
thread2 = threading.Thread(target=app.run, args=('0.0.0.0',))
thread1.start()
thread2.start()
