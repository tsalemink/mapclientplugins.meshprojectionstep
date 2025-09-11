"""
MAP Client Plugin Step
"""
import json
import os

from PySide6 import QtGui
from cmlibs.utils.zinc.node import project_nodes
from cmlibs.zinc.context import Context

from mapclient.mountpoints.workflowstep import WorkflowStepMountPoint

from mapclientplugins.meshprojectionstep.configuredialog import ConfigureDialog
from mapclientplugins.meshprojectionstep.model.meshprojection import MeshProjectionModel
from mapclientplugins.meshprojectionstep.view.meshprojection import MeshProjectionWidget


class MeshProjectionStep(WorkflowStepMountPoint):
    """
    Skeleton step which is intended to be a helpful starting point
    for new steps.
    """

    def __init__(self, location):
        super(MeshProjectionStep, self).__init__('Mesh Projection', location)
        self._configured = False  # A step cannot be executed until it has been configured.
        self._category = 'Model Projection'
        # Add any other initialisation code here:
        self._icon = QtGui.QImage(':/meshprojectionstep/images/model-viewer.png')
        # Ports:
        self.addPort(('http://physiomeproject.org/workflow/1.0/rdf-schema#port',
                      'http://physiomeproject.org/workflow/1.0/rdf-schema#uses',
                      'http://physiomeproject.org/workflow/1.0/rdf-schema#file_location'))
        self.addPort([('http://physiomeproject.org/workflow/1.0/rdf-schema#port',
                       'http://physiomeproject.org/workflow/1.0/rdf-schema#provides',
                       'http://physiomeproject.org/workflow/1.0/rdf-schema#file_location'),
                      ('http://physiomeproject.org/workflow/1.0/rdf-schema#port',
                       'http://physiomeproject.org/workflow/1.0/rdf-schema#provides',
                       'http://physiomeproject.org/workflow/1.0/rdf-schema#exf_file_location')
                      ])
        # Port data:
        self._input_mesh_file = None  # http://physiomeproject.org/workflow/1.0/rdf-schema#file_location
        self._output_mesh_file = None
        # Config:
        self._config = {
            'datapoint-coordinates': 'coordinates',
            'fixed': False,
            'identifier': '',
            'mesh-coordinates': 'coordinates',
            'normal': [0, 0, 1],
            'point': [0, 0, 0],
            'standardise-output': False,
        }

        self._view = None
        self._model = None

    def execute(self):
        """
        Add your code here that will kick off the execution of the step.
        Make sure you call the _doneExecution() method when finished.  This method
        may be connected up to a button in a widget for example.
        """
        if self._config['fixed']:
            self._fixed_execution()
        else:
            self._user_execution()

    def _fixed_execution(self):
        output_location = self._output_location()
        if not os.path.exists(output_location):
            os.makedirs(output_location)

        self._output_mesh_file = os.path.join(output_location, 'fixed-projected-mesh.exf')

        model = MeshProjectionModel()
        model.load(self._input_mesh_file, mesh_coordinates_name=self._config['mesh-coordinates'])
        plane_size = model.calculate_plane_size()
        model.create_projection_plane(self._config['point'], self._config['normal'], plane_size)
        model.project(self._config['mesh-coordinates'], self._config['datapoint-coordinates'])
        model.write_projected_mesh(
            self._output_mesh_file,
            self._config['mesh-coordinates'],
            self._config['datapoint-coordinates'],
            standardise_output=self._config['standardise-output'])

        self._doneExecution()

    def _user_execution(self):
        if self._view is None:
            self._model = MeshProjectionModel()
            self._view = MeshProjectionWidget(self._model)
            self._view.register_done_execution(self._doneExecution)

        self._view.set_identifier(self._config['identifier'])
        self._view.set_location(self._output_location())
        self._view.set_standardise_output(self._config['standardise-output'])
        self._view.clear()
        self._view.load(self._input_mesh_file)
        self._setCurrentWidget(self._view)

    def _output_location(self):
        return os.path.join(self._location, self._config['identifier'])

    def setPortData(self, index, dataIn):
        """
        Add your code here that will set the appropriate objects for this step.
        The index is the index of the port in the port list.  If there is only one
        uses port for this step then the index can be ignored.

        :param index: Index of the port to return.
        :param dataIn: The data to set for the port at the given index.
        """
        self._input_mesh_file = dataIn  # http://physiomeproject.org/workflow/1.0/rdf-schema#file_location

    def getPortData(self, index):
        """
        Add your code here that will return the appropriate objects for this step.
        The index is the index of the port in the port list.  If there is only one
        provides port for this step then the index can be ignored.

        :param index: Index of the port to return.
        """
        return self._output_mesh_file if self._config['fixed'] else self._view.get_output_file()  # http://physiomeproject.org/workflow/1.0/rdf-schema#file_location

    def configure(self):
        """
        This function will be called when the configure icon on the step is
        clicked.  It is appropriate to display a configuration dialog at this
        time.  If the conditions for the configuration of this step are complete
        then set:
            self._configured = True
        """
        dlg = ConfigureDialog(self._main_window)
        dlg.identifierOccursCount = self._identifierOccursCount
        dlg.setConfig(self._config)
        dlg.validate()
        dlg.setModal(True)

        if dlg.exec_():
            self._config = dlg.getConfig()

        self._configured = dlg.validate()
        self._configuredObserver()

    def getIdentifier(self):
        """
        The identifier is a string that must be unique within a workflow.
        """
        return self._config['identifier']

    def setIdentifier(self, identifier):
        """
        The framework will set the identifier for this step when it is loaded.
        """
        self._config['identifier'] = identifier

    def serialize(self):
        """
        Add code to serialize this step to string.  This method should
        implement the opposite of 'deserialize'.
        """
        return json.dumps(self._config, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    def deserialize(self, string):
        """
        Add code to deserialize this step from string.  This method should
        implement the opposite of 'serialize'.

        :param string: JSON representation of the configuration in a string.
        """
        self._config.update(json.loads(string))

        d = ConfigureDialog()
        d.identifierOccursCount = self._identifierOccursCount
        d.setConfig(self._config)
        self._configured = d.validate()
