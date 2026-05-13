Programs
========

:h2code:`getools.programs`

.. automodule:: getools.programs
   :no-members:
   :no-undoc-members:
   :no-inherited-members:
   :no-special-members:
   :noindex:

   nodes/index
   
``ProgramTree``

.. autoclass:: getools.programs.ProgramTree
   
   .. rubric:: Exceptions

   .. autoexception:: getools.programs.ProgramTree.ProgramInProgressError
   .. autoexception:: getools.programs.ProgramTree.NodeMissingChildError
   .. autoexception:: getools.programs.ProgramTree.MissingAgentError
   .. autoexception:: getools.programs.ProgramTree.BoundToAgentError

   .. rubric:: Properties

   .. autoattribute:: getools.programs.ProgramTree.status
   .. autoattribute:: getools.programs.ProgramTree.root
      :no-value:

   .. rubric:: Methods

   .. automethod:: getools.programs.ProgramTree.__init__
   .. automethod:: getools.programs.ProgramTree._set_agent
   .. automethod:: getools.programs.ProgramTree._collect_nodes
   .. automethod:: getools.programs.ProgramTree._fill_out_program
   .. automethod:: getools.programs.ProgramTree.get_nodes_by_type
   .. automethod:: getools.programs.ProgramTree.get_parent_of_node
   .. automethod:: getools.programs.ProgramTree.__str__