from peewee import *

database = PostgresqlDatabase(host='34.65.191.37', port='5432', database='alumoo', user='postgres', password='postgres')

class UnknownField(object):
    def __init__(self, *_, **__): pass

class BaseModel(Model):
    class Meta:
        database = database

class Users(BaseModel):
    email = TextField(column_name='Email')
    first_name = TextField(column_name='FirstName')
    img_url = TextField(column_name='ImgUrl')
    last_name = TextField(column_name='LastName')
    user_id = AutoField(column_name='UserId')

    class Meta:
        table_name = 'Users'

class Projects(BaseModel):
    description = TextField(column_name='Description')
    img_url = TextField(column_name='ImgUrl')
    owner_user = ForeignKeyField(column_name='OwnerUserId', field='user_id', model=Users)
    project_id = AutoField(column_name='ProjectId')
    title = TextField(column_name='Title')

    class Meta:
        table_name = 'Projects'

class Tasks(BaseModel):
    description = TextField(column_name='Description')
    hours_per_week = IntegerField(column_name='HoursPerWeek')
    location = TextField(column_name='Location')
    no_of_volunteers = IntegerField(column_name='NoOfVolunteers')
    project = ForeignKeyField(column_name='ProjectId', field='project_id', model=Projects)
    skills = TextField(column_name='Skills')
    status = IntegerField(column_name='Status')
    task_id = AutoField(column_name='TaskId')
    title = TextField(column_name='Title')

    class Meta:
        table_name = 'Tasks'

class Volunteers(BaseModel):
    location = TextField(column_name='Location')
    skills = TextField(column_name='Skills')
    user = ForeignKeyField(column_name='UserId', field='user_id', model=Users)
    volunteer_id = AutoField(column_name='VolunteerId')

    class Meta:
        table_name = 'Volunteers'

class Impressions(BaseModel):
    content = TextField(column_name='Content')
    img_url = TextField(column_name='ImgUrl')
    impression_id = AutoField(column_name='ImpressionId')
    task = ForeignKeyField(column_name='TaskId', field='task_id', model=Tasks)
    volunteer = ForeignKeyField(column_name='VolunteerId', field='volunteer_id', model=Volunteers)

    class Meta:
        table_name = 'Impressions'

class ProjectEntityVolunteerEntity(BaseModel):
    favorit_projects_project = ForeignKeyField(column_name='FavoritProjectsProjectId', field='project_id', model=Projects)
    followers_volunteer = ForeignKeyField(column_name='FollowersVolunteerId', field='volunteer_id', model=Volunteers)

    class Meta:
        table_name = 'ProjectEntityVolunteerEntity'
        indexes = (
            ((), True),
        )
        primary_key = CompositeKey('favorit_projects_project', 'followers_volunteer')

class TaskEntityVolunteerEntity(BaseModel):
    tasks_task = ForeignKeyField(column_name='TasksTaskId', field='task_id', model=Tasks)
    volunteers_volunteer = ForeignKeyField(column_name='VolunteersVolunteerId', field='volunteer_id', model=Volunteers)

    class Meta:
        table_name = 'TaskEntityVolunteerEntity'
        indexes = (
            ((), True),
        )
        primary_key = CompositeKey('tasks_task', 'volunteers_volunteer')

class TaskEntityVolunteerEntity1(BaseModel):
    applicants_volunteer = ForeignKeyField(column_name='ApplicantsVolunteerId', field='volunteer_id', model=Volunteers)
    applications_task = ForeignKeyField(column_name='ApplicationsTaskId', field='task_id', model=Tasks)

    class Meta:
        table_name = 'TaskEntityVolunteerEntity1'
        indexes = (
            ((), True),
        )
        primary_key = CompositeKey('applicants_volunteer', 'applications_task')

class EfMigrationsHistory(BaseModel):
    migration_id = CharField(column_name='MigrationId', primary_key=True)
    product_version = CharField(column_name='ProductVersion')

    class Meta:
        table_name = '__EFMigrationsHistory'

