from PySide2.QtCore import QObject, Signal
from PySide2.QtGui import QFontDatabase

from .Connection import DataConnection, ExecConnection
from .GlobalAttributes import Location
from .Script import Script
from .global_tools.Debugger import Debugger
from .Design import Design


class Session(QObject):
    """The Session class represents a project and holds all project-level
    data such as nodes."""

    new_script_created = Signal(Script)
    script_renamed = Signal(Script)
    script_deleted = Signal(Script)


    def __init__(
            self,
            flow_performance_mode: str = 'pretty',
            animations_enabled: bool = True,
            flow_theme_name: str = 'ueli',
            # debug_messages_enabled: bool = False,
            threaded: bool = False,
            parent: QObject = None,
            flow_data_conn_class=DataConnection,
            flow_exec_conn_class=ExecConnection,
            project: dict = None
    ):
        super().__init__(parent=parent)

        self._register_fonts()

        self.scripts: [Script] = []
        self.nodes = []  # list of node CLASSES
        self.threaded = threaded
        if threaded:
            self.custom_thread = self.thread()
            self.gui_thread = self.thread().thread()

        # connections
        self.flow_data_conn_class = flow_data_conn_class
        self.flow_exec_conn_class = flow_exec_conn_class

        self.design = Design(
            performance_mode=flow_performance_mode,
            animations_enabled=animations_enabled
        )

        self.design.set_flow_theme(name=flow_theme_name)
        self.design.set_flow_theme(name=flow_theme_name)  # temporary
        #   the double call is just a temporary fix for an issue I will address in a future release.
        #   Problem: because the signal emitted when setting a flow theme is directly connected to the according slots
        #   in NodeItem as well as NodeItem_TitleLabel, the NodeItem's slot (which starts an animation which
        #   uses the title label's current and theme dependent color) could get called before the title
        #   label's slot has been called to reinitialize this color. This results in wrong color end points for the
        #   title label when activating animations.
        #   This is pretty nasty since I cannot think of a nice fix for this issue other that not letting the slot
        #   methods be called directly from the emitted signal but instead through a defined procedure like before.

        if project:
            self.load(project)


    def _register_fonts(self):
        QFontDatabase.addApplicationFont(Location.PACKAGE_PATH+'/resources/fonts/poppins/Poppins-Medium.ttf')
        QFontDatabase.addApplicationFont(Location.PACKAGE_PATH+'/resources/fonts/source code pro/SourceCodePro-Regular.ttf')
        QFontDatabase.addApplicationFont(Location.PACKAGE_PATH+'/resources/fonts/asap/Asap-Regular.ttf')


    def register_nodes(self, node_classes):
        """Registers a list of Nodes which you then can access in all scripts"""

        for n in node_classes:
            self.register_node(n)


    def register_node(self, node_class):
        """Registers a Node which then can be accessed in all scripts"""

        self.nodes.append(node_class)


    def create_script(self, title: str, flow_size: list = None, create_default_logs=True, gui_parent=None) -> Script:
        """Creates and returns a new script"""

        script = Script(session=self, title=title, flow_size=flow_size, create_default_logs=create_default_logs,
                        gui_parent=gui_parent)

        self.scripts.append(script)
        self.new_script_created.emit(script)
        return script


    def _load_script(self, config: dict):
        """Loads a script from a project dict"""

        script = Script(session=self, config=config)
        self.scripts.append(script)
        self.new_script_created.emit(script)


    def rename_script(self, script: Script, title: str):
        """Renames an existing script"""
        script.title = title
        self.script_renamed.emit(script)


    def check_new_script_title_validity(self, title: str) -> bool:
        if len(title) == 0:
            return False
        for s in self.scripts:
            if s.title == title:
                return False

        return True


    def delete_script(self, script: Script):
        """Deletes an existing script"""

        self.scripts.remove(script)
        self.script_deleted.emit(script)


    def debugger(self) -> Debugger:
        """(WIP) Returns the session's debugger"""
        pass


    def load(self, project: dict) -> bool:
        """Loads a project and raises an error if required nodes are missing"""
        if 'scripts' not in project:
            return False

        for s in project['scripts']:
            self._load_script(config=s)


    def serialize(self) -> list:
        """Returns a list with 'config data' of all scripts for saving the project"""

        scripts_data = []
        for script in self.scripts:
            scripts_data.append(script.config_data())
        return scripts_data


    def all_nodes(self):
        """Returns a list containing all Node objects used in any flow which is useful for advanced project analysis"""

        nodes = []
        for s in self.scripts:
            for n in s.flow.nodes:
                nodes.append(n)
        return nodes


    def save_as_project(self, fpath: str):
        """Convenience method for directly saving the the all content as project to a file"""
        pass


    def set_stylesheet(self, s: str):
        """Sets the session's stylesheet which can be accessed by NodeItems.
        You usually want this to be the same as your window's stylesheet."""

        self.design.global_stylesheet = s
