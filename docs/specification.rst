.. _mcp-meshprojection-specification:

Ports
-----

This plugin:

* **uses**:

  * *http://physiomeproject.org/workflow/1.0/rdf-schema#file_location*

and

* **provides**:

  * *http://physiomeproject.org/workflow/1.0/rdf-schema#file_location* (*http://physiomeproject.org/workflow/1.0/rdf-schema#exf_file*)

The **uses** port imports a `Zinc` EX file defining the input mesh.
The **provides** port outputs a `Zinc` EX file defining the mesh projection.
The **provides** port is also compatible with the more refined `exf_file` port schema.
