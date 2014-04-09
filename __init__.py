# ***** BEGIN GPL LICENSE BLOCK *****
#
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ***** END GPL LICENCE BLOCK *****


bl_info = {
    "name": "Randomiser",
    "author": "Ben Simonds",
    "version": (0, 3),
    "blender": (2, 7, 0),
    "location": "Properties > Object Data > Randomise",
    "description": "Tools for randomising and animating text data (and some limited object data). Website: http://bensimonds.com/2014/04/02/randomiser-add-on/",
    #"warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Object",
    }

import bpy
from .Randomiser_addon import *


# Randomiser UI:

class RandomiserPanelObject(bpy.types.Panel):
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"
    bl_label = "Randomise Object Data"
    
    def draw(self, context):
        ob = bpy.context.active_object
        randomise = ob.randomiser
        layout = self.layout

        row = layout.row()
        row.prop(randomise, "use_randomise")
        if randomise.use_randomise:
            # draw layout for randomise method: freq/man:
            row = layout.row()
            row.prop(randomise, "update_method")
            row = layout.row()
            row.prop(randomise, "offset")
            
            if randomise.update_method == "man":
                row = layout.row()
                row.prop(randomise, "time")
            if randomise.update_method == "freq":
                row = layout.row()
                row.prop(randomise, "frequency")
        
            layout.separator()

            row = layout.row()
            row.prop(randomise, "generate_method")
            row = layout.row()
            row.prop(randomise, "source_group")    

class RandomiserPanelText(bpy.types.Panel):
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "data"
    bl_label = "Randomise Text Data"

    @classmethod
    def poll(self, context):
        ob = bpy.context.active_object
        return ob.type == 'FONT'


    def draw(self, context):
        ob = bpy.context.active_object
        if ob.type == 'FONT':
            text_data = ob.data
            randomise = text_data.randomiser
            layout = self.layout

            row = layout.row()
            row.prop(randomise, "use_randomise")
            
            
            if randomise.use_randomise:
                row.prop(randomise, "seed")
                layout = layout.box()
                row = layout.row()
                # draw layout for randomise method: freq/man:
                col = row.column()
                row = col.row()
                row.prop(randomise, "update_method")
                row = col.row()
                row.prop(randomise, "offset")
                
                if randomise.update_method == "man":
                    row = col.row()
                    row.prop(randomise, "time")
                if randomise.update_method == "freq":
                    row = col.row()
                    row.prop(randomise, "frequency")
            
                

                row = layout.row()
                col = row.column()
                col.separator()
                row = col.row()
                row.prop(randomise, "generate_method")
                if randomise.generate_method == 'random':
                    row = col.row()
                    row.prop(randomise, "no_repeats")
                if randomise.generate_method == 'ticker':
                    row = col.row()
                    row.prop(randomise, "ticklength")

                if randomise.generate_method == 'numeric':
                    row = col.row()
                    row.alignment = 'RIGHT'
                    row.prop(randomise, "group_digits")
                
                else:
                    row = col.row()
                    row.label(text = "Source:")

                    if randomise.generate_method == "grow":
                        layout.prop(randomise, "textdata")
                        #Leader:
                        row = layout.row()
                        row.prop(randomise, "leader")
                        if randomise.leader == 'flash':
                            row = layout.row()
                            row.prop(randomise, "leader_period")
                        #elif randomise.leader == "random":
                        #    layout.prop(randomise, "noise_source")

                    elif randomise.generate_method == "ticker":
                        row = layout.row()
                        row.prop(randomise, "textdata")
                    
                    else:             
                        if randomise.textsource in ["alphanumeric","characters"]:
                            layout.prop(randomise, "textsource")
                            layout.prop(randomise, "caps")
                        if randomise.textsource  in ["binary", "digits"]:
                            layout.prop(randomise, "textsource")
                        if randomise.textsource in ["tbchars","tblines"]:
                            layout.prop(randomise, "textsource")
                            layout.prop(randomise, "textdata")

                layout = self.layout
                layout.separator()


           # Noise properties
                row = layout.row()
                row.prop(randomise, "use_noise")

                if randomise.use_noise or randomise.leader == 'random':
                    layout = layout.box()

                if randomise.use_noise:
                    row = layout.row()
                    row.prop(randomise, "noise_update_independent")
                    if randomise.noise_update_independent:
                        row.prop(randomise, "noise_update_period")

                    row = layout.row()
                    row.prop(randomise, "noise_method")
                    if randomise.noise_method == "mask":
                        row = layout.row()
                        row.prop(randomise, "noise_mask")
                        row = layout.row()
                    else:
                        row = layout.row()
                        row.prop(randomise, "noise_threshold")

                        row = layout.row()
                        row.prop(randomise, "noise_pick_independent")
                        if randomise.noise_pick_independent:
                            row.prop(randomise, "noise_pick_period")
                    row = layout.row()
                    row.prop(randomise, "noise_ignore_whitespace")
                        
                        
                    #Noise source for both noise and leader:
                if randomise.use_noise or randomise.leader == 'random':
                    row = layout.row()
                    row.prop(randomise, "noise_source")
                    if randomise.noise_source in ['characters','alphanumeric']:
                        row = layout.row()
                        row.prop(randomise, "caps")
                    elif randomise.noise_source == 'tbchars':
                        row = layout.row()
                        row.prop(randomise, 'noise_textdata')

#Registration:
def register():
    #Properties:
    bpy.utils.register_class(RandomiserObjectProps)
    bpy.utils.register_class(RandomiserTextProps)
    bpy.types.Object.randomiser = bpy.props.PointerProperty(type = RandomiserObjectProps)
    bpy.types.TextCurve.randomiser = bpy.props.PointerProperty(type = RandomiserTextProps)
    
    #Operators:
    bpy.utils.register_class(RandomiseTextData)
    bpy.utils.register_class(RandomiseObjectData)
    bpy.utils.register_class(RandomiseSpreadSeeds)
    bpy.utils.register_class(RandomiseCopySeed)

    #UI:
    bpy.utils.register_class(RandomiserPanelObject)
    bpy.utils.register_class(RandomiserPanelText)

    #Handlers
    bpy.app.handlers.frame_change_post.append(randomise_handler)
    

def unregister():
    #Properties:
    bpy.utils.unregister_class(RandomiserObjectProps)
    bpy.utils.unregister_class(RandomiserTextProps)

    #Operators:
    bpy.utils.unregister_class(RandomiseTextData)
    bpy.utils.unregister_class(RandomiseObjectData)
    bpy.utils.unregister_class(RandomiseSpreadSeeds)
    bpy.utils.unregister_class(RandomiseCopySeed)

    #UI:
    bpy.utils.unregister_class(RandomiserPanelObject)
    bpy.utils.unregister_class(RandomiserPanelText)

    #Handlers:
    bpy.app.handlers.frame_change_post.remove(randomise_handler)


