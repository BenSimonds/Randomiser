Randomiser Readme:
------------------------------

For more about the add on, visit: http://bensimonds.com/2014/04/02/randomiser-add-on/

Installation:
----------------

To install the add-on, you can either place the Randomiser_addon.py file in your scripts/addons directory for blender manually, or use the "Install from File" option in blenders User Preferences - Addons menu, and select Randomiser.py from the file browser.


----------
Usage:
----------

Visit the following link for a video about how to use the script:
https://www.youtube.com/watch?v=ys7Rh76jUN8

Mesh Objects:
-------------------

	- Select object and enable randomise from the Object tab of the properties editor.
	- Specify a Group to sample object data from.
	- Update Method can either be set to Frequency, which updates the object data every set number of frames, or manual, which updates every time the “Time” property changes. The manual method is probably the more natural way for blender users, where you simply add keys to drive the change. The Frequency option is just there due to my hatred of adding keyframes where I could specify a couple of offset/speed parameters instead.

Text Objects:
-----------------
	- Select Text Object and enable randomise from the Object Data tab of the properties editor (text properties).
	- The Update Method options work the same as before.
	- Specify a Generate Method.
	- Based on this you will have different options for the source, choose either one of the procedural options, or for the text block options, specify the name of the text block you want to use in the Text Datablock property.

Adding Noise to Text:
-----------------------------
	- Specify a Noise Method, Mask or Random.
	- For Mask, provide a comma delimited list of indices (positions) in the string to replace with noise.
	- For Random, specify a threshold for the proportion of indices to be replaced with noise.
	- Specify a source for the noise. This can be either a text block or one of the procedural options as before.
	- Other options such as Update Noise Independently let you specify how the noise positions are selected and how they are updated. 	- The Ignore Whitespace option prevents indices being replaced if the character is a space or new line.

-------
Tips:
-------

	- If Randomiser can’t find the text source it’s looking for it will display an error message (or characters from it) as the text output. This is a cue to check the console for more information about the error and to check your settings.
	- The Typewriter and Ticker effects (and others) use a Text Datablock as the source for the text to display. This means a text block in the Text Editor, not another Text Object in the 3D Viewport.
	- When using noise consider using a monospace font – this keeps the characters the same width when replaced and stops the text “jiggling” too much.