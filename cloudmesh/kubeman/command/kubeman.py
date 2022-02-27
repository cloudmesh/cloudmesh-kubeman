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
              gregor-deploy.py --info
              gregor-deploy.py --kill [--keep_history]
              gregor-deploy.py --token [--keep_history]
              gregor-deploy.py --about


            Deploys the indycar runtime environment on an ubuntu 20.04 system.

            Arguments:
              FILE        optional input file
              CORRECTION  correction angle, needs FILE, --left or --right to be present

            Options:
              -h --help
              --info       info command
              --run        run the default deploy workflow (till the bug)
              --step       run the default deploy workflow step by step

            Description:

              gregor-deploy.py --info
                gets information about the running services

              gregor-deploy.py --kill
                kills all services

              gregor-deploy.py --run [--dashboard] [--stormui]
                runs the workflow without interruption till the error occurs
                If --dashboard and --storm are not specified neither GUI is started.
                This helps on systems with commandline options only.

              gregor-deploy.py --step [--dashboard] [--stormui]
                runs the workflow while asking in each mayor step if one wants to continue.
                This helps to check for log files at a particular place in the workflow.
                If the workflow is not continued it is interrupted.

              gregor-deploy.py --dashboard
                starts the kubernetes dashboard. Minikube must have been setup before

              gregor-deploy.py --stormui
                starts the storm gui. All of storm must be set up before.

              Examples:
                gregor-deploy.py --run --dashboard --stormui
                    runs the workflow without interruptions including the k8 and storm dashboards

                gregor-deploy.py --step --dashboard --stormui
                    runs the workflow with continuation questions including the k8 and storm dashboards

                gregor-deploy.py --menu
                    allows the selction of a particular step in the workflow

                less $INDYCAR/history.txt

              Possible Bugs:
              1. broken/unused storm-worker-service: The storm-worker-service is mentioned in the storm/setup.sh script.
                 However it is not mentioned in the
                 presentation slide that describes the setup. Furthermore when one starts this service, it does not
                 work and the probe seems to fail. For the reason that it is not mentioned in the guide and does nt work
                 we have not enabled it.
              2. kubectl race condition: A race condition in kubectl was avoided, buy adding an additional second wait time
                 after calling commands.
                 If errors still occur, the wait time is suggested to be increased. Currently, the wait time is set to 1 second.
              3. htm.java: Installation error of htm.java: This uses an outdated htm.java library. It is uncertain if this
                 causes an issue

              Benchmark:
                AMD5950
                +----------------------+----------+---------+
                | Name                 | Status   |    Time |
                |----------------------+----------+---------|
                | kill                 | ok       |  17.134 |
                | download_data        | ok       |   0     |
                | setup_minikube       | ok       |  20.844 |
                | setup_k8             | ok       |  12.507 |
                | setup_zookeeper      | ok       |   7.405 |
                | setup_nimbus         | ok       |   8.462 |
                | setup_storm_ui       | ok       |   4.312 |
                | open_stopm_ui        | ok       | 173.242 |
                | start_storm_workers  | ok       |   3.213 |
                | install_htm_java     | ok       |  52.482 |
                | setup_mqtt           | ok       |  11.591 |
                | start_storm_topology | ok       |  29.605 |
                +----------------------+----------+---------+

                EPY    via vnc
                +----------------------+----------+---------+
                | Name                 | Status   |    Time |
                |----------------------+----------+---------|
                | kill                 | ok       |  19.352 |
                | download_data        | ok       |   0     |
                | setup_minikube       | ok       |  31.828 |
                | setup_k8             | ok       |  12.775 |
                | setup_zookeeper      | ok       |  60.753 |
                | setup_nimbus         | ok       |  93.771 |
                | setup_storm_ui       | ok       |   4.366 |
                | open_stopm_ui        | ok       | 270.364 |
                | start_storm_workers  | ok       |   3.213 |
                | install_htm_java     | ok       | 183.767 |
                | setup_mqtt           | ok       | 122.997 |
                | start_storm_topology | ok       |  52.876 |
                | minikube_setup_sh    | ok       |  37.129 |
                | start_socket_server  | ok       | 113.281 |
                +----------------------+----------+---------+

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
        VERBOSE(arguments)

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
