Mesh Projection Step
====================

Overview
--------

The **Mesh Projection** step is an interactive plugin for the MAP-Client.

This plugin takes a `Zinc` compatible mesh EX file as an input, and provides an interactive GUI allowing the user to create a projection of the mesh onto a plane.
It utilises the `cmlibs.widgets` `Orientation` handler and `FixedAxisTranslation` handler to help the user define and visualise the plane used for the projection.
The **Mesh Projection** step outputs a new `Zinc` EX file defining the projected mesh.

Specification
-------------

Information on this plugin's specifications is available :ref:`here <mcp-meshprojection-specification>`.

Configuration
-------------

Information on this plugin's configuration is available :ref:`here <mcp-meshprojection-configuration>`.

Workflow Setup
--------------

Information on setting up a workflow with this plugin can be found :ref:`here <mcp-meshprojection-workflow-setup>`.

Instructions
------------

When the plugin loads for the first time you should see something like the image displayed in :numref:`fig-mesh-projection-initial`.
That is, you should see lines of your mesh displayed with yellow lines and white spheres depicting the nodes in the mesh.

.. _fig-mesh-projection-initial:

.. figure:: _images/mesh-projection-initial.png
   :figwidth: 100%
   :align: center

   **Mesh Projection** user interface just after loading.

Graphics Coordinates
^^^^^^^^^^^^^^^^^^^^

The coordinate fields used for the mesh and marker (data-point) definitions are determined automatically, but can be changed using the
combo-boxes in the `Graphics Coordinates` section if required. If the mesh EX file input does not contain any data-points, the
`Datapoint Coordinate Field` combo-box will be empty, and no data-points will be displayed.

Projection
^^^^^^^^^^

The `Auto Align Plane` button creates, if the projection plane does not yet exist, and sets the orientation of the plane to a linear least squares fit of the mesh.
The `Project` button projects the mesh onto the projection plane as indicated by the flat white surface.
The slider is used to set the final orientation of the projection onto the 2D plane.
The `Project` button and slider are only available once the projection plane has been created using the `Auto Align Plane` button.

Visibility
^^^^^^^^^^

There are a number of check-boxes in the `Visibility` section of the user interface (UI). Initially, only `Mesh` and `Markers` (data-points) are enabled - as these are the only graphics that have been created at this point.
The check-boxes for the `Surfaces` (projection plane), `Projected Mesh` and `Projected Markers` will be automatically enabled once the associated graphics have been initialised.

The size of the mesh nodes and data-points can be adjusted with the `Node Size` spin box.
If the points appear too small or if they aren't initially visible, try increasing this value.

The `Plane Alpha` value can also be adjusted to control the opacity of the projection plane, which may aid the user in the plane manipulation and projection process.
Initially the projection plane is not visible, so changing this value will have no visual effect.

Preview
^^^^^^^

The preview panel provides an indication of what the final output will look like.
The preview is updated whenever the projection is updated either through the `Project` button or through changing the slider value.

View
^^^^

The `View All` button will reset the view of the mesh so that the whole mesh is visible within the scene.

General
^^^^^^^

The `Continue` button will finish the step and continue with the workflow execution.

Usage
-----

The scene viewer currently has four modes: `View`, `Selection`, `Orientation` and `Translation` - indicated by the text in the bottom left of the view window.
The `View` mode is activated by default and allows the user to change the view-point of the scene using the mouse.
`Selection` mode can be activated by holding the **S** key on the keyboard.
The user can select a single graphics item at a time or drag a selection box over everything they wish to select.
Currently, being able to select graphic items does not lead to any additional capabilities.

`Orientation` and `Translation` modes are used to manipulate the orientation and position of the projection plane (using the corresponding `Orientation` and `FixedAxisTranslation` `CMLibs` scene handlers).
Both modes are disabled until the user generates an initial projection plane.
The `Translation` mode is for the user to be able to shift the plane representation in a fixed direction.
This does not affect the projection of the mesh onto the plane in any way.
The `Orientation` mode is for changing the projection plane from the best fit position.
To first generate a projection plane, the user must click `Auto Align Plane` in the `Projection` section of the UI; this will automatically create a projection plane and visualise a bounded segment of that plane in the scene viewer.

.. _fig-mesh-projection-plane:

.. figure:: _images/mesh-projection-plane.png
   :figwidth: 100%
   :align: center

   **Mesh Projection** step with auto-generated projection plane.

At this point, we should have a valid projection plane - as in :numref:`this figure <fig-mesh-projection-plane>` - and we can project our input mesh onto this plane using the `Project` button in the `Projection` section.

.. _fig-mesh-projection-projection:

.. figure:: _images/mesh-projection-projection.png
   :figwidth: 100%
   :align: center

   **Mesh Projection** step with mesh projected onto plane.

Any markers (data-points) associated with the input mesh will also be projected onto the plane.

A final orientation action can be performed by using the slider to rotate the current projection by.
The slider can be set anywhere between -180 degrees and +180 degrees.
The preview panel will show the final alignment of the projection that will be output when the step is completed.

Plane Manipulation
^^^^^^^^^^^^^^^^^^

If the users wishes to adjust the orientation of the plane, they may activate the `Orientation` handler by holding the **O** key on the keyboard.
While active, the `Orientation` handler will allow the user to rotate the projection plane around a rotation point by clicking and dragging the mouse within the scene viewer.
The rotation point is indicated by a blue sphere. This will be positioned at the centre of the plane by default, but may be selected and dragged to any position on the projection plane.

.. _fig-mesh-projection-orientation:

.. figure:: _images/mesh-projection-orientation.png
   :figwidth: 100%
   :align: center

   **Mesh Projection** step with `Orientation` handler active.

Similarly, the position of the projection plane may be adjusted with the `FixedAxisTranslation` handler.
This handler can be activated using the **T** key on the keyboard. While active, a set of translation arrows will be displayed in the centre of the projection plane.
There are two arrows for each Cartesian axis and these arrows can be dragged to translate the plane in the direction they specify.

.. _fig-mesh-projection-translation:

.. figure:: _images/mesh-projection-translation.png
   :figwidth: 100%
   :align: center

   **Mesh Projection** step with `FixedAxisTranslation` handler active.

The user will need to press the `Project` button again after making any adjustments to the plane orientation or position.

For more information on the `Orientation` and `FixedAxisTranslation` handlers, please refer to the `CMLibs Widgets documentation <https://abi-mapping-tools.readthedocs.io/en/stable/cmlibs.widgets/docs/index.html>`_ for these classes - found under `Handlers`.

Finishing
---------

Clicking the `Continue` button will output the mesh projection as well as any projected markers (data-points) to a `Zinc` EXF file and will execute any additional workflow steps connected to the **Mesh Projection** step.
