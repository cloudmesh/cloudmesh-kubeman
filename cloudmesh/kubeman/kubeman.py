"""
Kubeman. Cloudmesh KUbemanager allows the easy management of pods and services for kubernetes.
It has a small but very useful set of commands.
"""
import os
import textwrap
import time

import cloudmesh.kubeman
from cloudmesh.common.Shell import Shell
from cloudmesh.common.StopWatch import StopWatch
from cloudmesh.common.StopWatch import benchmark
from cloudmesh.common.console import Console
from cloudmesh.common.util import banner as cloudmesh_banner
from cloudmesh.common.util import str_banner
from cloudmesh.kubeman.__version__ import version


class Kubeman:
    commands = {}

    @staticmethod
    def exit_handler(signal_received, frame):
        """
        Kube manager has a build in Benchmark framework. In case you
        press CTRL-C, this handler asures that the benchmarks will be printed.

        :param signal_received:
        :type signal_received:
        :param frame:
        :type frame:
        :return:
        :rtype:
        """
        # Handle any cleanup here
        StopWatch.start("exit")
        print('SIGINT or CTRL-C detected. Exiting gracefully')
        StopWatch.stop("exit")

        exit(0)

    def set_dashboard(self, dashboard=True):
        """
        Kubernetes has a dashboard. by default cloudmesh kubeman displays it.
        With ths function the behaviour can be changed.

        :param dashboard:
        :type dashboard:
        :return:
        :rtype:
        """
        self.dashboard = dashboard

    def __init__(self, dashboard=False):
        """
        Set up cloudmesh kubeman. If the dashboard is set to TRue (default)
        the dashboard get displayed with the appropriate method.

        :param dashboard:
        :type dashboard:
        """
        self.dashboard = dashboard
        # cloudmesh/kubemanager
        self.screen = os.get_terminal_size()
        self.token = None
        self.ip = None
        self.LOCATION = cloudmesh.kubeman.__file__.replace("/__init__.py", "")

    def banner(self, msg):
        """
        prints the msg as banner, and adds it to the history.txt file

        :param msg:
        :type msg:
        :return:
        :rtype:
        """
        cloudmesh_banner(msg, c="#")
        self.add_history(str_banner(txt=msg.strip()))

    def hline(self, n=None, c="-"):
        """
        prints a horizontal line

        :param n:
        :type n:
        :param c:
        :type c:
        :return:
        :rtype:
        """
        if self.screen.columns is None:
            n = n or 79
        if n is None:
            n = 79
        try:
            print(int(n) * c)
        except:
            print(79 * c)

    def kill_services(self, pid=None, keep_history=True):
        """
        kills minikube

        :param pid:
        :type pid:
        :param keep_history:
        :type keep_history:
        :return:
        :rtype:
        """
        StopWatch.start("kill_services")
        self.banner("kill_services")
        try:
            if not keep_history:
                os.remove("history.txt")
        except:
            pass
        #pid = self.find_pid("8001")
        self.os_system(f"kill -9 {pid}")
        self.os_system("minikube stop")
        self.os_system("minikube delete")
        StopWatch.stop("kill_services")

    def find_pid(self, port):
        """
        find the process using a specific port

        :param port:
        :type port:
        :return:
        :rtype:
        """
        try:
            r = self.Shell_run(f"ss -lntupw | fgrep {port}").strip().split()[6].split(",")[1].split("=")[1]
            return r
        except:
            return ""

    def add_history(self, msg):
        """
        add the msg to the history

        :param msg:
        :type msg:
        :return:
        :rtype:
        """
        m = msg.strip()
        file = open("history.txt", "a")  # append mode
        file.write(f"{msg}\n")
        file.close()
        os.system("sync")

    def get_token(self, admin="admin-user"):
        """
        find the administartion user token

        :param admin:
        :type admin:
        :return:
        :rtype:
        """
        if self.token is None:
            Console.blue("TOKEN NAME")
            found = False
            while not found:
                name = self.Shell_run(f"kubectl -n kubernetes-dashboard get secret | grep {admin}").split()[0]
                if admin in name:
                    found = True
                else:
                    time.sleep(1)
                    print (".")

            Console.blue("TOKEN")
            found = False
            while not found:
                r = self.Shell_run(f"kubectl -n kubernetes-dashboard describe secret {name}")
                if "token:" in r:
                    found = True
                else:
                    time.sleep(1)
                    print (".")

            lines = r.splitlines()
            for line in lines:
                if line.startswith("token:"):
                    break
            line = line.replace("token:", "").strip()
            self.token = line
        return self.token

    def execute(self, commands, sleep_time=1, driver=os.system):
        """
        execute the given command and add it to the history.txt file

        :param commands:
        :type commands:
        :param sleep_time:
        :type sleep_time:
        :param driver:
        :type driver:
        :return:
        :rtype:
        """

        self.hline()
        print(commands)
        self.hline()

        result = ""
        for command in commands.splitlines():
            command = command.strip()
            self.add_history(command)
            if command.strip().startswith("#"):
                Console.blue(command)
            else:
                Console.blue(f"running: {command}")
                r = driver(command)
                if driver == os.system:
                    if (str(r) == "0"):
                        print()
                        Console.ok(f"# {command} .ok.")
                        self.hline(".")
                    else:
                        Console.error(f"# {command}\n{r}")
                        self.hline(".")
                else:
                    print(r)

                result = result + str(r)
                time.sleep(sleep_time)
        return result

    def os_system(self, command):
        """
        runs the command with os.system and ads it to history.txt

        :param command:
        :type command:
        :return:
        :rtype:
        """
        return self.execute(command, driver=os.system)

    def Shell_run(self, command):
        """
        runs the command with cloudmesh.SHell.run and adds it to the history

        :param command:
        :type command:
        :return:
        :rtype:
        """
        return self.execute(command, driver=Shell.run)

    def clean_script(self, script):
        """
        cleans up a script to remove leading sapces from each llline

        :param script:
        :type script:
        :return:
        :rtype:
        """
        return textwrap.dedent(script).strip()

    def setup_minikube(self, memory=10000, cpus=8, sleep_time=0):
        """
        set up a minikube instance with given resource specifications

        :param memory:
        :type memory:
        :param cpus:
        :type cpus:
        :param sleep_time:
        :type sleep_time:
        :return:
        :rtype:
        """
        StopWatch.start("setup_minikube")
        self.banner("setup_minikube")
        memory = memory * 8
        script = f"""
        minikube delete
        minikube config set memory {memory}
        minikube config set cpus {cpus}
        minikube start driver=docker
        """
        self.execute(script, driver=os.system)
        time.sleep(sleep_time)
        StopWatch.stop("setup_minikube")

    def setup_k8(self):
        """
        add administrative users to k8

        :return:
        :rtype:
        """
        StopWatch.start("setup_k8")
        self.banner("setup_k8")
        # "enable-skip-login"
        script = \
            f"""
        kubectl apply -f https://raw.githubusercontent.com/kubernetes/dashboard/v2.4.0/aio/deploy/recommended.yaml
       
        # create user
        kubectl create -f {self.LOCATION}/account.yaml
        
        # create role
        kubectl create -f {self.LOCATION}/role.yaml    
        """
        self.execute(script, driver=os.system)

        token = self.get_token()

        print(token)

        script = \
            f"""
        # start dashboard
        # cd {self.LOCATION}; 
        kubectl proxy &
        """
        self.execute(script, driver=os.system)
        StopWatch.stop("setup_k8")

    def get_minikube_ip(self):
        """
        get the minikube ip

        :return:
        :rtype:
        """
        if self.ip is None:
            self.ip = self.Shell_run("minikube ip").strip()
        return self.ip

    def open_k8_dashboard(self, display=True):
        """
        open the kubernetes daskboard

        :param display:
        :type display:
        :return:
        :rtype:
        """
        self.banner("open_k8_dashboard")
        if self.dashboard or display:
            token = self.get_token()
            self.hline()
            print("TOKEN")
            self.hline()
            print(token)
            self.hline()
            found = False
            # wait for the dashboard to be reachable
            while not found:
                command = "curl http://localhost:8001/api/v1/namespaces/kubernetes-dashboard/services/https:kubernetes-dashboard:/proxy/#/login"
                result = Shell.run(command)
                found = "<title>Kubernetes Dashboard</title>" in result
                time.sleep(1)
                print(".", end="")

            self.execute("gopen http://localhost:8001/api/v1/namespaces/kubernetes-dashboard/services/https:"
                         "kubernetes-dashboard:/proxy/#/login", driver=os.system)

    def wait_for_pod(self, name, state="Running"):
        """
        wait for a specific pod to be in the state specified. The name will be searched for. It can be the partial name of a pod.
        Make sure you implement and use a unique naming scheme.

        :param name:
        :type name:
        :param state:
        :type state:
        :return:
        :rtype:
        """
        print(f"Starting {name}: ")
        found = False
        while not found:
            try:
                r = Shell.run("kubectl get pods").splitlines()
                r = Shell.find_lines_with(r, name)[0]
                if state in r:
                    found = True
                    print(f"ok. Pod {name} {state}")
                else:
                    print(".", end="", flush=True)
                    time.sleep(1)
            except:
                print(".", end="", flush=True)
                time.sleep(1)

    def menu(self, steps):
        """
        a menu of functions without parameters. The functions are listed as arry in steps

        :param steps: list of function names (no parameters allowed)
        :type steps: function names
        :return:
        :rtype:
        """
        next_choice = 0
        c = ""
        while True:
            self.hline()
            print("q : quit")
            print("i : info")

            # for index in range(len(steps)):
            #    print(f"{index:<2}: {steps[index][1]}")
            for index in range(len(steps)):
                print(f"{index:<2}: {steps[index].__name__}")

            self.hline()
            print(f"Suggested choice: {next_choice}")
            i = input("Choice:           ")
            try:
                next_choice = int(i) + 1
            except:
                pass
            print(f'You typed >{i}<')
            self.hline()
            if i == "q":
                return
            elif i == "i":
                self.deploy_info()
            else:
                i = int(i)
                f = steps[i]
                f()

    def get_pods(self):
        """
        returns the information from the pods

        :return:
        :rtype:
        """
        return self.Shell_run(f"kubectl get pods")

    def get_services(self):
        """
        returns the information of the services

        :return:
        :rtype:
        """
        return self.Shell_run(f"kubectl get services")

    def deploy_info(self):
        """
        returns some elementary deployment information

        :return:
        :rtype:
        """
        try:
            ip = self.get_minikube_ip()
            print("IP:               ", ip)
        except:
            pass

        pods = self.get_pods()
        print("PODS")
        print(pods)

        services = self.get_services()
        print("SERVICES")
        print(services)

        self.hline()
        print("VERSION:               ", version)
        self.hline()
        print("TOKEN")
        self.os_system(
            "kubectl -n kubernetes-dashboard describe secret "
            "$(kubectl -n kubernetes-dashboard get secret "
            "| grep admin-user | awk '{print $1}')")
        print()

    # The license
    LICENSE = \
        """
                                         Apache License
                                   Version 2.0, January 2004
                                http://www.apache.org/licenses/
        
           Copyright 2022 Gregor von Laszewski, University of Virginia
        
           Licensed under the Apache License, Version 2.0 (the "License");
           you may not use this file except in compliance with the License.
           You may obtain a copy of the License at
        
               http://www.apache.org/licenses/LICENSE-2.0
        
           Unless required by applicable law or agreed to in writing, software
           distributed under the License is distributed on an "AS IS" BASIS,
           WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
           See the License for the specific language governing permissions and
           limitations under the License.
        
           Credits:
        
            This script is authored by Gregor von Laszewski, any work 
            conducted with it must cite the following:
        
            This work is using cloudmesh/kubemanager developed by 
            Gregor von Laszewski. Cube manager is available on GitHub 
            \cite{github-las-kubemanager}.
        
            @misc{github-las-cubemanager,
                author={Gregor von Laszewski},
                title={Cloudmesh Kubemanager},
                url={TBD},
                howpublished={GitHub, PyPi},
                year=2022,
                month=feb
            }
        
            Text entry for citation in other then LaTeX documents:
        
                This work is using cloudmesh/kubemanager developed 
                by Gregor von Laszewski. Cube manager is available 
                on GitHub [1].
        
                [1] Gregor von Laszewski, Cloudmesh Kubemanager, 
                    published on GitHub, URL:TBD, Feb. 2022.
        
        """
