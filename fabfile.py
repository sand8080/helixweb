import os

from fabric.api import env, run, local
from fabric.colors import green, red, yellow
from fabric.contrib.files import exists
from fabric.contrib.project import rsync_project
from fabric.context_managers import prefix, settings, hide, show
from fabric.utils import abort


def _project_dir():
    return os.path.realpath(os.path.dirname(__file__))


def _get_env():
    p_dir = _project_dir()
    env_path = os.path.join(p_dir, '.env')
    if os.path.exists(env_path):
        return env_path
    else:
        print red("Environment not found")
        raise Exception("Environment not found")


print green("Configuring production environment")
env.hosts = ['helixweb@78.47.11.201']
env.proj_root_dir = '/opt/helixproject/helixweb'
env.proj_root_dir_owner = 'helixweb'
env.proj_root_dir_group = 'helixproject'
env.proj_root_dir_perms = '750'
env.proj_dir = os.path.join(env.proj_root_dir, 'helixweb')
env.proj_dir_owner = 'helixweb'
env.proj_dir_group = 'helixproject'
env.proj_dir_perms = '700'
env.run_dir = os.path.join(env.proj_root_dir, 'run')
env.run_dir_owner = 'helixweb'
env.run_dir_group = 'helixproject'
env.run_dir_perms = '770'
env.static_dir = os.path.join(env.proj_root_dir, 'static')
env.static_dir_owner = 'helixweb'
env.static_dir_group = 'helixproject'
env.static_dir_perms = '750'
env.proj_pythonpath = 'export PYTHONPATH="%s:%s"' % (
    os.path.join(env.proj_dir, 'src'),
    os.path.join(env.proj_dir, '..', 'helixcore', 'src'))
env.local_pythonpath = 'export PYTHONPATH="%s:%s"' % (_project_dir(),
    os.path.join(_project_dir(), '..', 'helixcore', 'src'))
env.rsync_exclude = ['.*', '*.log*', '*.sh', '*.pyc',
    'fabfile.py', 'pip-requirements-dev.txt',
    'uwsgi/*_dev.*', 'settings_dev.py']
env.activate = '. %s/.env/bin/activate' % env.proj_root_dir
print green("Production environment configured")


def config_virt_env():
    proj_env_dir = os.path.join(env.proj_root_dir, '.env')
    if not exists(proj_env_dir):
        print green("Virtualenv creation")
        run('virtualenv %s --no-site-packages' % proj_env_dir)

    with prefix(env.activate):
        print green("Installing required python packages")
        run('pip install -r %s/pip-requirements.txt' % env.proj_dir)


def _check_rd(rd, o_exp, g_exp, p_exp):
    print green("Checking directory %s owner, group, permissions. "
        "Expected: %s, %s, %s" % (rd, o_exp, g_exp, p_exp))
    if exists(rd):
        res = run('stat -c %%U,%%G,%%a %s' % rd)
        o_act, g_act, p_act = map(str.strip, res.split(','))
        if o_act != o_exp or g_act != g_exp or p_act != p_exp:
            abort(red("Directory %s params: %s. Expected: %s" % (
                rd, (o_act, g_act, p_act), (o_exp, g_exp, p_exp))))
        print green("Directory %s checking passed" % rd)
    else:
        abort(red("Directory %s is not exists" % env.proj_dir))


def _fix_rd(rd, o, g, p):
    print green("Setting project directory parameters")
    run('chown %s:%s %s' % (o, g, rd))
    run('chmod %s %s' % (p, rd))
    print green("Checking project directory parameters")


def collectstatic():
    print green("Collecting static files")
    with prefix(env.activate):
        print green("Installing required python packages")
        manage = os.path.join(env.proj_dir, 'src', 'helixweb', 'manage.py')
        run('python %s collectstatic --noinput' % manage)
    print green("Static files collected")


def sync():
    print green("Files synchronization started")
    _check_rd(env.proj_root_dir, env.proj_root_dir_owner,
        env.proj_root_dir_group, env.proj_root_dir_perms)

    print green("Project files synchronization")
    rsync_project(env.proj_dir, local_dir='%s/' % _project_dir(),
        exclude=env.rsync_exclude, delete=True, extra_opts='-q -L')
    # project directory
    _fix_rd(env.proj_dir, env.proj_dir_owner,
        env.proj_dir_group, env.proj_dir_perms)
    _check_rd(env.proj_dir, env.proj_dir_owner,
        env.proj_dir_group, env.proj_dir_perms)
    # run directory
    run('mkdir -p %s' % env.run_dir)
    _fix_rd(env.run_dir, env.run_dir_owner,
        env.run_dir_group, env.run_dir_perms)
    _check_rd(env.run_dir, env.run_dir_owner,
        env.run_dir_group, env.run_dir_perms)
    # static directory
    run('mkdir -p %s' % env.static_dir)
    _fix_rd(env.static_dir, env.static_dir_owner,
        env.static_dir_group, env.static_dir_perms)
    _check_rd(env.static_dir, env.static_dir_owner,
        env.static_dir_group, env.static_dir_perms)
    print green("Files synchronization complete")


def restart_uwsgi():
    print green("Restarting uwsgi")
    run('touch %s/uwsgi/uwsgi.xml' % env.proj_dir)
    print green("Uwsgi restarted")


def deploy_helixcore():
    print green("Deploying helixcore")
    helixcore_fab = os.path.join(_project_dir(), '..', 'helixcore', 'fabfile.py')
    local_fab = os.path.join(_get_env(), 'bin', 'fab')
    local('%s -f %s sync_helixweb' % (local_fab, helixcore_fab))
    print green("Helixcore deployment finished")


def deploy():
    with hide('running', 'stdout'):
        print yellow("Welcome back, commander!")
        print green("Deployment started")
        deploy_helixcore()
        sync()
        config_virt_env()
        collectstatic()
        restart_uwsgi()
        print green("Deployment complete")
        print yellow("Helixweb operational!")