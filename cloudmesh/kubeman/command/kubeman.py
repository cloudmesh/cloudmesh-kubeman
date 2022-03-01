from signal import signal, SIGINT

from cloudmesh.kubeman.kubeman import Kubeman

from cloudmesh.common.console import Console
from cloudmesh.common.debug import VERBOSE
from cloudmesh.shell.command import PluginCommand
from cloudmesh.shell.command import command


class KubemanCommand(PluginCommand):

    # noinspection PyUnusedLocal
    @command
    def do_kubeman(self, args, arguments):
        """
        ::
            Usage:
              cms kubeman --info
              cms kubeman --kill [--keep_history]
              cms kubeman --token [--keep_history]
              cms kubeman --about

            Simple management commands for kubernetes for ubuntu 20.04 system.

            Options:
              -h --help
              --keep_history  do not delete the history between different commands
              --token         prints the security token
              --kill          killing the kubernetes environment whne set up wit minikube
              --info          info command
              --run           run the default deploy workflow (till the bug)

            Description:

              cms kubeman --info
                gets information about the running services

              cms kubeman --kill
                kills all services

              cms kubeman --run [--dashboard] [--stormui]
                runs the workflow without interruption till the error occurs
                If --dashboard and --storm are not specified neither GUI is started.
                This helps on systems with commandline options only.

              cms kubeman --step [--dashboard] [--stormui]
                runs the workflow while asking in each mayor step if one wants to continue.
                This helps to check for log files at a particular place in the workflow.
                If the workflow is not continued it is interrupted.

              Credits:
                This script is authored by Gregor von Laszewski, any work conducted with it must cite the following:

                This work is using cloudmesh/kubemanager developed by Gregor von Laszewski. Cube manager is available on GitHub at
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
                    Gregor von Laszewski, Cloudmesh Kubemanager, published on GitHub, URL:TBD, Feb. 2022.
        """
        # VERBOSE(arguments)

        signal(SIGINT, Kubeman.exit_handler)
        global step
        info = arguments["--info"]
        clean = arguments["--kill"]
        if clean:
            k8 = Kubeman()
            k8.kill_services()
        elif info:
            k8 = Kubeman()
            k8.deploy_info()
        elif arguments["--token"]:
            k8 = Kubeman()
            k8.get_token()
        elif arguments["--about"]:
            k8 = Kubeman()
            print(k8.LICENSE)

        else:
            Console.error("Usage issue")
