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

import bpy, mathutils, random, operator, string #locale no longer needed!
from random import Random
from bpy.app.handlers import persistent

# Functions:

def get_iter(data, mode, shift): #"data might be an object or text datablock."
    #Mode is a string in ["update", "noise1", "noise2" "mask"]
    current_frame = bpy.context.scene.frame_current
    if mode in ['noise1', 'mask']: #i.e. for getting noise back rather than iter:
        randomise = data.randomiser
        offset = randomise.offset
        if mode == 'noise1':
            frequency = randomise.noise_update_period
        elif mode == 'mask':
            frequency = randomise.noise_pick_period
        integer = int(round(current_frame-offset+shift)/frequency)
        return integer
    if mode == 'noise2':
        integer = random.randint(1,100)
        return integer
    else:
        randomise = data.randomiser
        offset = randomise.offset
        frequency = randomise.frequency
        integer = randomise.time
        update_method = randomise.update_method
    if update_method == "man":
        return integer + shift
    elif update_method == "freq":
        integer = int(round(current_frame-offset + shift)/frequency)
        if integer >= 0:
            return integer
        else:
            return 0

def custom_rand(data, method, noisemode, shift, *args): 
    # Custom randomise method that uses current frame as seed and initialises each frame to stay predictable.
    # Args:
    #   object: Input data to operate on: either object or text data.
    #   method: Method in random to call (see docs for random)
    #   *args: required args for the method chosen, given as a list []
    x = Random(get_iter(data, noisemode, shift))
    methodtocall = getattr(x,method)
    #print(args)
    result = methodtocall(*args)
    return result



# Operators:
class RandomiseObjectData (bpy.types.Operator):
    bl_idname = 'object.randomise_data'
    bl_label = "Randomises an objects object data."
    object_string = bpy.props.StringProperty()

    def randomise_data(self, object):
        randomise = object.randomiser
        frequency = randomise.frequency
        generate_method = randomise.generate_method
        group_name = randomise.source_group
        group = bpy.data.groups[group_name]
        current_frame = bpy.context.scene.frame_current

        #Get data source and do sanity check:
        #print("Source Group name give is: " + group_name)
        data_source = [bpy.data.objects[name] for name in sorted(group.objects.keys()) if bpy.data.objects[name].type == object.type] #Sorted and cleaned list of objects in source group
        if len(data_source) == 0:
            print("Data source list is empty. Skipping.")
            return
        else:
            if generate_method == 'ordered':
                object.data = data_source[get_iter(object, 'update', 0) % len(data_source)].data
            elif generate_method == 'random':
                #DON'T call choice if list length is zero. It causes ugly exceptions...
                if len(data_source) ==0:
                    print("Data source to choose from was length zero. Can't choose from empty set.")
                    print("Data source:" + str(data_source))
                else:
                    # If current data in list, ignore: - This buggers up frequency because it removes the current from the avaliable options even if it wasn't supposed to change anyway...
                    #Check get_iter has changed from the previous frame?
                    if randomise.update_method == 'freq':
                        if get_iter(object, 'update', -1) != get_iter(object, 'update', 0): #Only do choice list and update if required!
                            choice_list = [ob for ob in data_source if ob.data != object.data] #Remove current choice from data_source.
                            object.data = custom_rand(object, "choice", 'update', 0, choice_list).data
                    else:
                        choice_list = [ob for ob in data_source if ob.data != object.data] #Remove current choice from data_source
                        object.data =  custom_rand(object, "choice", 'update', 0, choice_list).data
            return

    def execute(self, context):
        try:
            object = bpy.data.objects[self.object_string]
        except TypeError:
            print("Couldnt find object :" + self.object_string)
        self.randomise_data(object)
        return {'FINISHED'}

class RandomiseTextData (bpy.types.Operator):
    bl_idname = 'object.randomise_text'
    bl_label = 'Randomises an objects text data.'
    data_string = bpy.props.StringProperty()

    def get_textsource(self, source, generate_method, caps, text_block):
        text_data = ""
        #Returns a string for randomiser to sample from.

        if generate_method == 'grow':
            #Check that text block is not None. If it is it can't be picked from.
            if text_block is None:
                #print("ERROR: Method: Grow - No text block given as source. Check your settings.")
                text_data = "ERROR -  Text block not found. See console."     
            else:
                for line in text_block.lines:
                    text_data += line.body
                    text_data += "\n"
            return text_data

        elif generate_method == 'ticker':
            #Check that text block is not None. If it is it can't be picked from.
            if text_block is None:
                #print("ERROR: Method: Ticker - No text block given as source. Check your settings.")
                text_data = "ERROR -  Text block not found. See console."     
            else:
                for line in text_block.lines:
                    text_data += line.body
            return text_data

        elif generate_method == 'numeric':
            #print("Nothing to generate, skipping.")
            text_data = ""
            return text_data

        else:
            if source == "binary":
                text_data = ["0","1"]
                return text_data

            elif source == "digits":
                text_data = [x for x in string.digits]
                return text_data
                
            elif source == "characters":
                if caps == "ac":
                    text_data = [x for x in string.ascii_letters]
                elif caps == "uc":
                    text_data = [x for x in string.ascii_uppercase]
                elif caps == "lc":
                    text_data = [x for x in string.ascii_lowercase]
                return text_data
                    
            elif source == "alphanumeric":
                if caps == "ac":
                    text_data = [x for x in (string.ascii_letters + string.digits)]
                elif caps == "uc":
                    text_data = [x for x in (string.ascii_uppercase + string.digits)]
                elif caps == "lc":
                    text_data = [x for x in (string.ascii_lowercase + string.digits)]
                return text_data
            
            elif source in ['tblines', 'tbchars']:
                #Check that text block is not None. If it is it can't be picked from.
                if text_block is None:
                    #print("ERROR: Method: Text Block Characters/Lines - No text block given as source. Check your settings.")
                    text_data = "ERROR -  Text block not found. See console."
                else:         
                    if source == "tblines":
                        text_data = [line.body + " " for line in text_block.lines]
                        
                    elif source == "tbchars":
                        for line in text_block.lines:
                            for char in line.body:
                                if char != " ":
                                    text_data += char
                return text_data

            else:
                print("Hmm, something should have returned by now, return None so as to give you a useful error...")
                return None             


    def addnoise(self, string, data):
        #noise info:
        randomise = data.randomiser
        source = randomise.noise_source
        mask_string = randomise.noise_mask
        noise_method = randomise.noise_method
        threshold = randomise.noise_threshold
        ignore_whitespace = randomise.noise_ignore_whitespace

        try:
            noise_text_datablock = bpy.data.texts[randomise.noise_textdata]
        except KeyError:
            #print("No text block found for noise.")
            noise_text_datablock = None
        noise_data = self.get_textsource(source, "random", randomise.caps, noise_text_datablock)

        if noise_method == 'mask':
            #Create noise at certain positions based on mask list:
            if len(mask_string) > 0:
                noise_mask = [int(a) for a in mask_string.split(",")]
            else:
                noise_mask = []
            #truncate noise mask to length of string:
            noise_mask = noise_mask[:len(string)]
            for x in noise_mask:
                #only add noise if that character is visible:
                if len(string) > 0:
                    if x < 0:
                        if abs(x) > len(string):
                            x = len(string) - (x % len(string)) 
                        else:
                            x = len(string) + x
                    text_working = string
                    try:
                        ignore_list = ["\n", ""]
                        if ignore_whitespace:
                            ignore_list.append(" ")
                        if string[x] in ignore_list:
                            pass
                        else:
                            if randomise.noise_update_independent:
                                iter_noise = 'noise1'
                            else:
                                iter_noise = 'update'
                            text_working = string[0:x] + custom_rand(data, "choice", iter_noise, x*13, noise_data) + string[x+1:]
                    except (KeyError, IndexError):
                        pass
                    string = text_working
                    #This seems to get messed up sometimes, and end up with string getting much longer...
                    

        elif noise_method == 'random':
            #Create random noise at a certain percentage of indices.
            mask_length = int((threshold) * len(string))
            string_length = len(string)
            if randomise.noise_pick_independent:
                iter_noise = 'mask'
            else:
                iter_noise = 'update'
            noise_mask = custom_rand(data,"sample", iter_noise, 0, range(0,string_length),mask_length)

            for x in noise_mask:
                text_working = string
                ignore_list = ["\n", ""]
                if ignore_whitespace:
                    ignore_list.append(" ")
                if string[x] in ignore_list:
                    pass
                else:
                    if randomise.noise_update_independent:
                        iter_noise = 'noise1'
                    else:
                        iter_noise = 'update'
                    text_working = string[0:x] + custom_rand(data,"choice", iter_noise, x*13, noise_data) + string[x+1:]    
                string = text_working

        return string


    def randomise_text(self, data):
        randomise = data.randomiser
        generate_method = randomise.generate_method
        
        frequency = randomise.frequency
        caps = randomise.caps
        text_new = ""

        #text_block is only applicable if the source requires it. Otherwise it might not even be given and will cause errors.
        source  = randomise.textsource
        try:
            if generate_method in ['random', 'ordered']:
                if source in ['tblines', 'tbchars']:
                    text_block = bpy.data.texts[randomise.textdata]
                else:
                    #print("Source doesn't require text block.")
                    text_block = None
            elif generate_method in ['grow','ticker']:
                source = 'tbchars'
                text_block = bpy.data.texts[randomise.textdata]
            else:
                #print("Generate method doesn't require text block.")
                text_block = None
        except KeyError:
            if randomise.textdata == "":
                print("ERROR: No name given for text block.")
            else:
                print("ERROR: Cannot find text block with name: " + randomise.textdata)
            print("Tip: The Text Block should contain the name of a text block in the Text Editor, NOT a text object.")    
            text_block = None

        # First get the source text from which to generate new string from:
        #print("Text Data Inputs: \n Source: " + source + " \n Generate Method: " + generate_method + "\n Caps: " + caps + "\n Text_block: " + str(text_block))
        text_data = self.get_textsource(source, generate_method, caps, text_block)
        #print("Text Data for sampling:" + text_data)
        noise_data = self.get_textsource(randomise.noise_source, "random", "ac", text_block)
        i = get_iter(data, 'update', 0)

        # Get a new string for the text:
        current_frame = bpy.context.scene.frame_current

        if generate_method == 'grow':
            if get_iter(data, 'update', 0) != 0:
                text_new = text_data[:i]

        elif generate_method == 'ticker':
            #Sanity check that input text isn't empty:
            if text_data == "":
                text_data = " "
            #create repeated string in case original isn't long enough:
            ticker_length = randomise.ticklength
            text_length = len(text_data)
            if ticker_length < text_length:
                ticker_source  = text_data * 2
            else:
                repeats = int(ticker_length/text_length) + 1
                ticker_source = text_data * repeats
            ticker_startpos = i % len(text_data)
            ticker_endpos = ticker_startpos + ticker_length
            text_new = ticker_source[ticker_startpos:ticker_endpos]

        elif generate_method == 'numeric':
            if data.randomiser.group_digits:
                text_new = format(i, ',d') #locale.format("%d", i, grouping = data.randomiser.group_digits)
            else:
                text_new = str(i)
            #print("Text New:" + text_new)

        elif generate_method == "ordered":
            text_new = text_data[i % len(text_data)]

        elif generate_method == 'random':
            previous = randomise.previous_choice
            no_repeats = randomise.no_repeats
            text_data = list(text_data)
            if no_repeats:
                #Cleaned list of choices 
                list_clean = []
                for x in text_data:
                    if x not in list_clean:
                        list_clean.append(x)
                #Check there hasn't been an increment in i in the last frame:
                i_last = get_iter(data, 'update', -1)
                if i !=  i_last:
                    #Update previous to current:
                    previous = data.body
                randomise.previous_choice = previous
                #Now remove previous from list_clean:
                if previous in list_clean:
                    list_clean.remove(previous)
                #Choose a new value:
                print("Current iter: " + str(i) + " Previous iter: " + str(i_last) + " Previous:" + previous +  " List:" + str(list_clean))
                text_new = custom_rand(data,'choice','update',0,list_clean)
            else:
                text_new = custom_rand(data,'choice','update',0,text_data)


        # Add noise to text_new:
        if randomise.use_noise:
            text_new = self.addnoise(text_new, data)

        # Add leader to text_new if on grow:
        if generate_method == "grow":
            leader = data.randomiser.leader
            leader_period = data.randomiser.leader_period
            if leader == "random":
                text_new = text_new + custom_rand(data, "choice", 'update', 0, noise_data)
            elif leader == "underscore":
                text_new  = text_new + "_"
            elif leader == 'flash':
                flash = [" ", "_"]
                flash_int = int(current_frame / leader_period) % 2
                flash_choice = flash[flash_int] #Could be made more configurable... Done!
                text_new = text_new + flash_choice

        # Apply new string:
        data.body = text_new

        return

    def execute(self, context):
        #try:
        data = bpy.data.curves[self.data_string]
        self.randomise_text(data)
        return {'FINISHED'}
        #except KeyError:
        #    print("Couldnt find data :" + self.data_string)
        #    return{'FINISHED'}

### Properties Classes:

# Object Properties:
class RandomiserObjectProps (bpy.types.PropertyGroup):
    use_randomise = bpy.props.BoolProperty(name = "Randomise")
    source_group = bpy.props.StringProperty(name = "Group", description = "Name of the Group to use for Randomise.")
    generate_method = bpy.props.EnumProperty(name = "Generate Method", items = [("ordered","Ordered","ordered"),("random","Random","random")])
    frequency = bpy.props.FloatProperty(name = "Frames per update", default = 1.0, min=0.01)
    update_method = bpy.props.EnumProperty(name = "Update Method", items = [("freq","Frequency","Automatic Based on frame numbers"),("man","Manual","Manual, based on a value that can be animated, driven, etc.")])
    time = bpy.props.IntProperty(name = "Time")
    offset = bpy.props.IntProperty(name = "Offset")

class RandomiserTextProps (bpy.types.PropertyGroup):
    use_randomise = bpy.props.BoolProperty(name = "Randomise")
    
    # Randomise Properties:

    textsource = bpy.props.EnumProperty(name = "Text Source", items = [
        ("binary","Binary","binary digits"),
        ("digits","Digits","random digits"),
        ("characters","Characters","random characters"),
        ("alphanumeric","Alphanumeric","random letters"),
        ("tblines","Text File, Lines","Random lines from a text block."),
        ("tbchars","Text File, Characters","Random characters from a text block.")
        ])
    generate_method = bpy.props.EnumProperty(name = "Generate Method", items = [
        ("ordered","Pick Ordered","ordered"),
        ("random","Pick Random","random"),
        ("grow","Typewriter","Grow sentence letter by letter."),
        ("ticker","Scrolling Text","Scrolling Text"),
        ("numeric", "Counting", "Count up or countdown."),
        ])
    caps = bpy.props.EnumProperty(name = "Case", items = [
        ("lc","Lowercase","lowercase"),
        ("uc","Uppercase","uppercase"),
        ("ac","Both","both")
        ])
    textdata = bpy.props.StringProperty(name = "Text Datablock", description = "Name of Text datablock to use.")
    frequency = bpy.props.FloatProperty(name = "Frames per Update", default = 1.0, min = 0.01 )
    time = bpy.props.IntProperty(name = "Time")
    update_method = bpy.props.EnumProperty(name = "Update Method", items = [
        ("freq","Frequency","Automatic Based on frame number."),
        ("man","Manual","Manual, based on a value that can be animated, driven, etc.")
        ])
    offset = bpy.props.IntProperty(name = "Offset")
    ticklength = bpy.props.IntProperty(name = "Scroll length", default = 10)
    group_digits = bpy.props.BoolProperty(name = "Group Digits", default = False)

    #Previous choice for random choice selections to avoid repeats:
    previous_choice = bpy.props.StringProperty(name = "Previous Choice", description = "Stored value of previous randomiser character generated.")
    no_repeats = bpy.props.BoolProperty(name = "Avoid Repeats", default = False)
    
    #Leader properties:
    leader = bpy.props.EnumProperty(name = "Leader",items = [
        ("none","None","none"),
        ("random","Noise","Taken from noise source."),
        ("underscore","Underscore","underscore"),
        ("flash","Underscore Flash","flash")
        ])
    leader_period = bpy.props.IntProperty(name = "Leader Period", default = 25)

    # Noise Properties:
    use_noise = bpy.props.BoolProperty(name = "Noise")
    noise_mask = bpy.props.StringProperty(name = "Mask (comma delimited)")
    noise_source = bpy.props.EnumProperty(name = "Noise Source", items = [
        ("digits","Digits","random digits"),
        ("characters","Characters","random letters"),
        ("alphanumeric","Alphanumeric","random letters and numbers"),
        ("binary", "Binary", "Zeroes and Ones"),
        ("tbchars", "Text Block, Characters", "Random characters from a text block.")
        ])
    noise_textdata = bpy.props.StringProperty(name = "Text Datablock", description = "Name of Text datablock to use for Noise.")
    noise_method = bpy.props.EnumProperty(name = "Noise Method", items = [
        ("mask","Mask","mask"),
        ("random","Random","random")
        ])
    noise_threshold = bpy.props.FloatProperty(name = "Noise Threshold", min = 0.0, max = 1.0)
    #Options for updating noise indepenendently from the base string.
    noise_pick_independent = bpy.props.BoolProperty(name = "Pick Noise Sites Independently", default = False)
    noise_update_independent = bpy.props.BoolProperty(name = "Update Noise Independently", default = False)
    noise_pick_period  = bpy.props.FloatProperty(name = "Frames per Update", default = 1.0, min = 0.01 )
    noise_update_period  = bpy.props.FloatProperty(name = "Frames per Update", default = 1.0, min = 0.01 )

    noise_ignore_whitespace = bpy.props.BoolProperty(name = "Ignore WhiteSpace", default = True)
    



# Handlers:
@persistent
def randomise_handler(dummy):
    # Randomise Objects
    to_randomise = []
    for object in bpy.data.objects:
        try:
            if object.randomiser.use_randomise == True:
                try:
                    if object.randomiser.source_group in bpy.data.groups.keys():
                        to_randomise.append(object)
                except (KeyError, AttributeError): #Key error for key not found. Attr Error for key not given.
                    print("ERROR:Group not found for object to pick random data from.")
                    pass
        except AttributeError:
            pass
    for object in to_randomise:
        bpy.ops.object.randomise_data(object_string = object.name)

    # Randomise Text
    to_randomise = []
    for text in bpy.data.curves:
        try:
            if text.randomiser.use_randomise == True:
                to_randomise.append(text)
        except AttributeError:
            pass
    for text in to_randomise:
        bpy.ops.object.randomise_text(data_string = text.name)
    return
