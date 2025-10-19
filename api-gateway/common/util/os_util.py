# edit at 2024-04-10
# cp /Users/kimmyounghoon/Works/mkay/common/api-gateway/common/util/* ./api-gateway/common/util/

from subprocess import PIPE, Popen

def cmdline(command):
    process = Popen(
        args=command,
        stdout=PIPE,
        shell=True
    )
    return process.communicate()[0]

