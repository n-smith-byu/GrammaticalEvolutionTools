Programs
========

:h2code:`grammaticalevolutiontools.programs`

.. automodule:: grammaticalevolutiontools.programs
   :no-members:
   :no-undoc-members:
   :no-inherited-members:
   :no-special-members:
   :noindex:

   nodes/index
   
``ProgramTree``

.. autoclass:: grammaticalevolutiontools.programs.ProgramTree
   
   .. rubric:: Exceptions

   .. autoexception:: grammaticalevolutiontools.programs.ProgramTree.ProgramInProgressError
   .. autoexception:: grammaticalevolutiontools.programs.ProgramTree.NodeMissingChildError
   .. autoexception:: grammaticalevolutiontools.programs.ProgramTree.MissingAgentError
   .. autoexception:: grammaticalevolutiontools.programs.ProgramTree.BoundToAgentError

   .. rubric:: Properties

   .. autoattribute:: grammaticalevolutiontools.programs.ProgramTree.status
   .. autoattribute:: grammaticalevolutiontools.programs.ProgramTree.root
      :no-value:

   .. rubric:: Methods

   .. automethod:: grammaticalevolutiontools.programs.ProgramTree.__init__
   .. automethod:: grammaticalevolutiontools.programs.ProgramTree._set_agent
   .. automethod:: grammaticalevolutiontools.programs.ProgramTree._collect_nodes
   .. automethod:: grammaticalevolutiontools.programs.ProgramTree._fill_out_program
   .. automethod:: grammaticalevolutiontools.programs.ProgramTree.get_nodes_by_type
   .. automethod:: grammaticalevolutiontools.programs.ProgramTree.get_parent_of_node
   .. automethod:: grammaticalevolutiontools.programs.ProgramTree.__str__