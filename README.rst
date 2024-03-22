====================
Mesh Projection Step
====================

The **Mesh Projection** step is an interactive plugin for the MAP-Client.
The MAP Client is a workflow management application written in Python.
It can be found at https://github.com/MusculoskeletalAtlasProject/mapclient.

This plugin takes a `Zinc` compatible mesh EX file as an input, and provides an interactive GUI allowing the user to create a projection
of the mesh onto a plane. It utilises the `cmlibs.widgets` `Orientation` handler and `FixedAxisTranslation` handler to help the user define
and visualise the plane used for the projection. The **Mesh Projection** step outputs a new `Zinc` EX file defining the projected mesh.

Please refer to the plugin documentation for details on how to set up and run this step.


Inputs
------
- **exf_file** [Zinc EX file] - A `Zinc` EX file defining the input mesh.

Outputs
-------
- **exf_file** [Zinc EX file] - A `Zinc` EX file defining the mesh projection.
