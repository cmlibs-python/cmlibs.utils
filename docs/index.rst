OpenCMISS Utils
===============

The **OpenCMISS Utils** is a collection of Python utilities to support working with the OpenCMISS Zinc library.
This package provides six modules

#. geometry.plane
#. zinc.field
#. zinc.finiteelement
#. zinc.general
#. zinc.material
#. image

These modules are surfaced under the namespace package *opencmiss* within the *utils* package.
To use these modules the following import statement can be used::

  import opencmiss.utils.geometry.plane
  import opencmiss.utils.zinc.finiteelement

Geometry
--------

The *geometry* package contains a module *plane*.
The *plane* module encapsulates describing a plane (a point and a normal vector) in an OpenCMISS Zinc way.
It also encapsulates a way to serialise a description of a plane.

Zinc
----

The *zinc* package is made up of four modules.
The modules are aimed at raising the API level of the Zinc library making it easier to perform common tasks.
The *field* module deals with creating and querying fields.
The *finiteelement* module deals with creating finite elements.
This includes creating nodes and querying node extents.
The *general* module makes available Python Context Managers for Zinc objects that send messages.
The *material* module add functionality to create a material from an image field.

Image
-----

The *image* module contains a function for extracting the coordinates of the corners of a DICOM image.

Package API
-----------

Geometry Package
****************

Plane
+++++

.. automodule:: opencmiss.utils.geometry.plane
   :members:

Zinc Package
************

Field
+++++

.. automodule:: opencmiss.utils.zinc.field
   :members:

FiniteElement
+++++++++++++

.. automodule:: opencmiss.utils.zinc.finiteelement
   :members:

General
+++++++

.. automodule:: opencmiss.utils.zinc.general
   :members:

Material
++++++++

.. automodule:: opencmiss.utils.zinc.material
   :members:

Image Module
************

.. automodule:: opencmiss.utils.image
   :members:
