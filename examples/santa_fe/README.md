# Santa Fe Problem
__________________________________
This is an implementation of the Santa Fe Problem for demontration purposes.
In ```src/``` you will find four files showing how to use the abstract classes 
provided in the ```grammaticalevolutiontools``` package to easily define a
```World```, ``Grammar``, and ``Agent`` for Santa Fe. 

## Files

### ```src/santafe_world.py```
This file shows how to use the provided ```GridWorld``` from
```grammaticalevolutiontools.worlds.grid_world``` to implement a ```SantaFeWorld```, 
which reads the santa fe trail layout from ```resources/GRID.txt```. Feel free
to edit the size of the map or locations of the *#'s* which indicate the location of
the food in the world, and see how the location of the food is automatically 
updated in ```SantaFeWorld```.

### ```src/santafe_agent.py```
This file shows how to customize ```GridAgent``` from 
```grammaticalevolutiontools.worlds.grid_world``` to create an agent specifically 
designed for out Santa Fe World. Besides the basic commands available in 
```GridWorldAgent``` like ```turn_left```, ```turn_right```, and ```move_forward```, 
the SantaFeAgent also adds a command to check if there is food ahead. 
These commands are called from the subclasses ```ExecutableNode``` 
defined in the ```SantaFeGrammar```.

### ```src/santafe_food.py```
This file defines the ```SantaFeFood``` class, which inherits from ```GridWorldReward```,
a subclass of both ```WorldObject``` and ```RewardObjectMixin```. This is simply an object
representing the food along the Santa Fe trail that an agent can pick up. It is 
programmed by default to give a reward of 1 and then remove itself from
the World upon agent interaction.

### ```src/grammar.py```
This file defines the ```Grammar``` used by the ```SantaFeAgent``` class to create
programs. Notice ```SantaFeGrammar``` is not a subclass of ```Grammar``` but rather an instance.
Nodes are defined in the ```SantaFeGrammar``` context using the predefined, abstract 
classes of ```ProgramNode``` found in ```grammaticalevolutiontools.programs.nodes```. 
While these are subclasses of ```ProgramNode```, the ```@as_grammar_node``` decorator 
creates a new class and converts them to subclasses of ```GrammarNode```. This allows 
us to easily create custom subclasses of ```ProgramNode```, keep their hierarchy, and 
all of our custom behavior, but also have them still work inside of a ```Grammar```, and
also take advantage of the more efficient ```GrammarNode``` implementation.

This grammar is based on the context-free grammar found in ```resources/grammar.txt```.
However, this file is just for reference and is not automatically parsed. The Grammar
defined in ```grammar.py``` also does not strictly follow the same Grammar structure provided 
in the file, but may skip non-terminals that have another non-terminal as their only 
possible child, for example *\<condition>*.

### ```santafe.ipynb```
This is a jupyter notebook that shows how the ```SantaFeWorld```, ```SantaFeAgent```,
```SantaFeFood``` classes, along with the ```SantaFeGrammar```, are all used together
in a simple grammatical evolution task. It demonstates how to build a simple
genetic algorithm using the existing tools for cross-over and mutation found
in ```grammaticalevolutiontools.evolution```, that work with the ```AgentProgram``` class. 
It also shows how to automatically record a simulation, and create a 
customizable ```WorldAnimation``` object for a ```GridWorld``` subclass. 