# -*- coding: UTF-8 -*-
from app import create_app,db
from app.models import User,Role,Post
from flask_script import Manager,Shell
from flask_migrate import Migrate,MigrateCommand

app = create_app('production')
manager = Manager(app)
migrate = Migrate(app,db)

def make_shell_context():
    return dict(app=app,User=User,Role=Role,db=db,Post=Post)
manager.add_command('shell',Shell(make_context=make_shell_context))
manager.add_command('db',MigrateCommand)

if __name__ == '__main__':
    manager.run()
