import subprocess
import json
import time


def main():

    slice = subprocess.getoutput("python3 ../vsdnorches-cli.py create slice 1")

    t = subprocess.Popen(['python3', '../vsdnorches-cli.py', 'show', 'topology'], stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    top = t.communicate()[0]
    top = top.decode()
    topology = json.loads(top)
    nodes = topology["nodes"][0]
    node = nodes["id"]

    cmd_add = [
        'python3',
        '../vsdnorches-cli.py',
        'configure',
        'slice',
        slice,
        'add',
        'node',
        node,
        'BR'
    ]

    add = subprocess.Popen(cmd_add, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    virt = add.communicate()[0]
    virt = virt.decode()

    cmd_dep = [
        'python3',
        '../vsdnorches-cli.py',
        'configure',
        'slice',
        slice,
        'deploy'
    ]

    dep = subprocess.Popen(cmd_dep, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    out = dep.communicate()[0]

    print(out)

if __name__ == '__main__':
    start = time.time()
    main()
    end = time.time()
    print(end - start)