Introduction
============

This documentation explains the goals and scope as well as the functionalitities
and known issues of this documentation.
Currently this documentation is not completed and is just in its setup and development stage. 

.. _about:

About FlyByGen
--------------

.. _exampleCometRender:

.. figure:: ExampleCometRender.png
   :width: 500 

   Automatically generated comet example image with dust jets.

As you can see in the :ref:`exampleCometRender` image the pipeline is able to generate automatically
any kind of image from a fly-by scenario. 
It was primarly developed for the Comet Interceptor mission with the goal in mind to generate in future
images of comet fly-bys for other mission scenarios.


Issues
------
Json files cannot be updated during runtime before they have been loaded. They are loaded during the process and thus changing them during runtime (before the render starts) can lead to unwanted results
s




.. _exampleRST:

Example Restructured Text
=========================

.. _baseStats:

Base Stats
~~~~~~~~~~


The base stats for these Pokémon can be obtained from the general
`base stats list`_. If you need to compute total damage done in battle or the
current HP for a given Pokémon, you can use :ref:`NumPy array <arrays.ndarray>`
objects.

.. _core series: https://bulbapedia.bulbagarden.net/wiki/Core_series
.. _base stats list: https://bulbapedia.bulbagarden.net/wiki/List_of_Pok%C3%A9mon_by_base_stats_(Generation_I)

=========== ====== ========== =========== ========= =========== ========= ===========
**Pokémon** **HP** **Attack** **Defense** **Speed** **Special** **Total** **Average**
----------- ------ ---------- ----------- --------- ----------- --------- -----------
 Bulbasaur    45       49         49          45        65         253       50.6
 Charmander   39       52         43          65        50         249       49.8
 Squirtle     44       48         65          43        50         250       50.0
=========== ====== ========== =========== ========= =========== ========= ===========

Pokémon details
~~~~~~~~~~~~~~~

For these three Pokémon, you can check out their pokédex entries below.

.. tab-set::

   .. tab-item:: Bulbasaur

         * Seed Pokémon
         * Type: :bdg-success:`grass` :bdg-dark:`poison`
         * Abilities: Overgrow, Chlorophyll

   .. tab-item:: Charmander

         * Lizard Pokémon
         * Type: :bdg-warning:`fire`
         * Abilities: Blaze, Solar power

   .. tab-item:: Squirtle

         * Tiny turtle Pokémon
         * Type: :bdg-primary:`water`
         * Abilities: Torrent, Rain dish

Usage
-----

You can create an instance of Bulbasaur called ``friend``, for example, by doing

.. code::

   >>> import pokedex
   >>> friend = pokedex.Bulbasaur()
