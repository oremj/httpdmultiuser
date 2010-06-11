from collections import defaultdict
import os
from subprocess import PIPE, Popen
from urllib2 import urlopen, URLError


float_format = lambda a: "%.2f" % a
int_format = lambda a: "%d" % a

class Apache(object):
    def __init__(self, name, front_ports, back_ports):
        self.name = name
        self.front_ports = front_ports.split(',')
        self.back_ports = back_ports.split(',')

    @property
    def pid(self):
        try:
            return open("/var/run/httpd-%s.pid" % self.name).read().strip()
        except IOError:
            return None

    def _run_svc_cmd(self, cmd):
        p = Popen('service httpd-%s %s' % (self.name, cmd),
                   stdout=PIPE, stderr=PIPE, shell=True)
        return p.communicate()

    def restart(self):
        self._run_svc_cmd('restart')

    def reload(self):
        self._run_svc_cmd('reload')

    def _ps_stats(self):
        if not self.running:
            return {}

        p = Popen(['/bin/ps', 'axo', 'user,pid,ppid,%cpu,%mem,command'],
                    stdout=PIPE)
        out = p.communicate()[0]
        procs = []
        for l in out.split('\n')[1:]:
            try:
                user, pid, ppid, cpu, mem, cmd = l.split(None, 5)
            except ValueError:
                continue
            cpu, mem = float(cpu), float(mem)
            if ppid == self.pid:
                procs.append([cpu, mem])

        return {
            'children': int_format(len(procs)),
            'cpu': float(sum(p[0] for p in procs)),
            'mem': float(sum(p[1] for p in procs)),
        }

    def _apache_stats(self):
        try:
            u = urlopen("http://localhost:%s/server-status?auto"
                            % self.back_ports[0])
        except URLError:
            return {}

        stats = {}
        interesting = ['BytesPerSec', 'ReqPerSec']
        for l in u.readlines():
            type, value = l.split(":")
            if type in interesting:
                stats[type] = float_format(float(value))
            if type == 'Scoreboard':
                scoreboard = {}
                for c in value:
                    scoreboard[c] = scoreboard.get(c, 0) + 1

        stats['Working'] = int_format(scoreboard.get('W', 0))
        stats['Idle'] = int_format(scoreboard.get('_', 0))
        stats['Open'] = int_format(scoreboard.get('.', 0))

        return stats

    def stats(self):
        stats = self._ps_stats()
        stats.update(self._apache_stats())
        stats['name'] = self.name
        return stats

    @property
    def running(self):
        return self.pid is not None

    def __repr__(self):
        return "Apache('%s','%s')" % (self.pid, self.name)

    def __eq__(self, other):
        if self.name == other.name:
            return True
        else:
            return False


def print_report(apaches, sort='name'):
    format = ("%(name) -33s"
              "%(children) -6s"
              "%(cpu) -6s"
              "%(mem) -6s"
              "%(ReqPerSec) -6s"
              "%(Working) -4s"
              "%(Idle) -4s"
              "%(Open) -4s")
    
    print format % {
        'name': 'NAME',
        'children': 'CHLD',
        'cpu': 'CPU',
        'mem': 'MEM',
        'ReqPerSec': "R/s",
        'Working': "WK",
        'Idle': "IL",
        'Open': "OP",
    }

    stats = [a.stats() for a in apaches]
    stats.sort(cmp=lambda a,b: cmp(a.get(sort), b.get(sort)))
    
    for stat in stats:
        print format % defaultdict(lambda: 'off', stat)


def all_apaches():
    info_dir = "/etc/apaches-info"
    apaches = []
    for f in (os.path.join(info_dir, i) for i in os.listdir(info_dir)):
        apaches.append(Apache(*open(f).read().strip().split(':')))
    return apaches


if __name__ == '__main__':
    a = all_apaches()
    print_report(a)
