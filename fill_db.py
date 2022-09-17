import peewee as pw
from db_model import *
from random import random
import numpy as np
from sklearn.datasets import make_blobs

firstnames = []
lastnames = []
emails = []
verbs = []
objects = []
locations = []
impression_content = ['good', 'great', 'terrible', 'amazing', 'wonderful', 'lovely', 'delightful', 'generous', 'uncomfortable']

with open('suggestion-api/schemafiller/firstnames') as f:
    firstnames = [x.strip() for x in f.readlines()]
with open('suggestion-api/schemafiller/lastnames') as f:
    lastnames = [x.strip() for x in f.readlines()]
with open('suggestion-api/schemafiller/emails') as f:
    emails = [x.strip() for x in f.readlines()]
with open('suggestion-api/schemafiller/verbs') as f:
    verbs = [x.strip() for x in f.readlines()]
with open('suggestion-api/schemafiller/objects') as f:
    objects = [x.strip() for x in f.readlines()]
with open('suggestion-api/schemafiller/locations') as f:
    locations = [x.strip() + ", Switzerland" for x in f.readlines()]

psdb = pw.PostgresqlDatabase(host='34.65.191.37', port='5432', database='alumoo', user='postgres', password='postgres')
numtasks = 10000
numusers = 1000
numprojects = 100
skillgen = make_blobs(
    n_samples=numtasks+numusers, 
    n_features=10, 
    centers=5, 
    cluster_std=0.15, 
    center_box=(0.0,1.0)
)[0]

def genskill(i):
    skills = np.clip(skillgen[i], 0, 1)
    return ','.join([str(x) for x in list(skills)])

print('Generating users and volunteers.')
users = []
volunteers = []
v2t = {}
for i in range(numusers):
    firstname = firstnames[int(random() * len(firstnames))]
    lastname = lastnames[int(random() * len(lastnames))]
    avinum = sum([ord(x) for x in firstname] + [ord(x) for x in lastname]) % 8
    users.append(Users.create(
        first_name=firstname,
        last_name=lastname,
        email=f'{firstname}.{lastname}@{emails[int(random()*len(emails))]}',
        img_url=f'/suggestion-api/schemafiller/avatars/avi{avinum}.png'
    ))
    userid = users[len(users)-1].user_id
    skills = genskill(i)
    location = locations[int(random() * len(locations))]
    volunteers.append(Volunteers.create(
        location=location,
        skills=skills,
        user=userid
    ))
    v2t[volunteers[len(volunteers)-1].volunteer_id] = []
    

print('Generating projects.')
projects = []
for i in range(numprojects):
    title = f'Project #{i+1}'
    description = (' and ').join([verbs[int(random()*len(verbs))]+' '+objects[int(random()*len(objects))] for x in range(5)])
    img_url = int(random()*5)
    owner_user = users[int(random() * len(users))].user_id
    projects.append(Projects.create(
        description=description,
        img_url=f'/suggestion-api/schemafiller/projectimgs/proj{img_url}.jpg',
        owner_user=owner_user,
        title=title
    ))
    added = []
    for o in range(50):
        volunteer = volunteers[int(random()*len(volunteers))].volunteer_id
        while volunteer in added:
            volunteer = volunteers[int(random()*len(volunteers))].volunteer_id
        added.append(volunteer)
        ProjectEntityVolunteerEntity.create(
            favorit_projects_project=projects[len(projects)-1].project_id,
            followers_volunteer=volunteer
        )

print('Generating tasks.')
tasks = []
finished_tasks = []
t2v = {}
for i in range(numtasks):
    description = verbs[int(random()*len(verbs))]+' '+objects[int(random()*len(objects))]
    hours_per_week = int(random()*40)
    no_of_volunteers = int(random()*20)
    location = locations[int(random()*len(locations))]
    project = projects[int(random()*len(projects))].project_id
    skills = genskill(i+numusers)
    status = int(random()*4)
    title = f'Task #{i+1}'
    tasks.append(Tasks.create(
        description=description,
        hours_per_week=hours_per_week,
        location=location,
        no_of_volunteers=no_of_volunteers,
        project=project,
        skills=skills,
        status=status,
        title=title
    ))
    taskid = tasks[len(tasks)-1].task_id
    t2v[taskid] = []
    if status != 0:
        volid = volunteers[int(random()*len(volunteers))].volunteer_id
        t2v[taskid].append(volid)
        v2t[volid].append(taskid)
        TaskEntityVolunteerEntity.create(
            tasks_task=taskid,
            volunteers_volunteer=volid
        )
    if status == 0:
        added = []
        for i in range(int(random()*10)):
            volid = volunteers[int(random()*len(volunteers))].volunteer_id
            while volid in added:
                volid = volunteers[int(random()*len(volunteers))].volunteer_id
            added.append(volid)
            TaskEntityVolunteerEntity1.create(
                applicants_volunteer=volid,
                applications_task=taskid
            )
    if status == 3:
        finished_tasks.append(tasks[len(tasks)-1])


print('Generating impressions.')
impressions = []
for task in finished_tasks:
    taskid = task.task_id
    content = impression_content[int(random()*len(impression_content))]
    volunteer = t2v[taskid][int(random()*len(t2v[taskid]))]
    impressions.append(Impressions.create(
        content=content,
        task=taskid,
        volunteer=volunteer,
        img_url=''
    ))


