"""
Extended matplotlib plots with keybindings to automate image processing.

Makes use of: 
https://matplotlib.org/3.1.0/users/event_handling.html    

Some key shortcuts are set in matplotlibrc:
https://matplotlib.org/3.1.0/users/navigation_toolbar.html

------------------------- CLASSES --------------------------------
There are 3 classes in play:
    - `DataUnit` is one piece of data. After processing the information from
      processing is written into the `annotation` attribute.
    - `Batch` is a list of data to process. Opens new figures and saves data to
      file.
    - `FigureWithBindings` is the extended figure thing. 
------------------------------------------------------------------


----------------------- HOW TO USE -------------------------------
1. Create a list of `DataUnit` classes.
2. Construct `Batch`.
3. Run `Batch.gimme_more()`.
4. Use the `FigureWithBindings` plot.

FigureWithBindings is constructed from `Batch`.
You might want to set these:j
    - preprocessing function which controls what data is shown on the plot
    - postprocessing function which maps categorized data to data you actually
      want to save By default both functions are identity functions.  The
      categorized data passed to the postprocessing functions is a list of
      3-tuples containing ('mode', x-coord, y-coord) where 'mode' is the
      category label.
------------------------------------------------------------------

-------------------- HOW TO USE THE FIGURE -----------------------
Press a 'mode' key (look at `FigureWithBindings._modes` to see what labels are
available) and left-click somewhere.
If you want to remove the last point, press right-click.
If you are finished with the picture, press 'q' to go to the next picture.
------------------------------------------------------------------
"""

import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import os.path

mpl.rcParams['keymap.quit'] = ''
print("The 'q' shortcut in normal matplotlib figures will be disabled")

class Batch:
    def __init__(self, data_list, file_to_save_to, preprocess_fun=lambda x: x, postprocess_fun=lambda x: x, append=False):
        self.preprocess_fun = preprocess_fun
        self.postprocess_fun = postprocess_fun
        if not append and os.path.isfile(file_to_save_to):
            raise ValueError("File {} already exists! Choose another file name, delete the file or append to the existing file by passing the argument `append=True`")
        self.file_to_save_to = file_to_save_to
        self.data_list = data_list
        self.current = -1
        self._f = None
    
    def gimme_more(self):
        if self.current == len(self.data_list) - 1:
            print("No more data man!")
        else:
            self.current += 1
            self._f = FigureWithBindings(self, self.data_list[self.current], preprocess_fun=self.preprocess_fun, postprocess_fun=self.postprocess_fun)

    def take_my_data(self, data):
        self.data_list[self.current].annotation = data
        self.save_progress()
        
    def save_progress(self):
        with open(self.file_to_save_to, 'a') as f:
            f.write(self.data_list[self.current].name + ": ")
            f.write(str(self.data_list[self.current].annotation) + '\n')
        

class FigureWithBindings:
    """
    `FigureWithBindings(self, god, data, preprocess_fun postprocess_fun)`

    Parameters:
    - `god`: the creator of the figure, needed to save dat
    - `data`: data given by god
    - `preprocess_fun` - function applied on data before opening the plot
    - `postprocess_fun` - function applied on categorized data.
    Categorized data is a list of 3-tuples ('mode', x-coord, y-coord).
    
    How to:
    - add a point: press one of `FigureWithBindings._modes` keys and left-click
    - remove last point: right-click
    - quit and go to next: press 'q'
    """
    def __init__(self, god, data, preprocess_fun=lambda x: x, postprocess_fun=lambda x: x):
        self.creator = god
        self.post_fun = postprocess_fun
        self.fig, self.ax = plt.subplots()
        data_to_show = preprocess_fun(data.data)
        self.ax.imshow(data_to_show)
        self.categorized_points = [] # list of 3-tuples ('mode', x-coord, y-coord)
        self._colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k', 'w']
        self._modes = self._colors 
        self.mode_color_dict = dict(zip(self._modes, self._colors))

        self.mode = None
        self.set_mode(self._modes[0])

        self.cids = [self.fig.canvas.mpl_connect('button_press_event', self.onclick)]
        self.cids.append(self.fig.canvas.mpl_connect('key_press_event', self.onkeypress))

        for i in self._modes:
            self.add_key_press_method(i)
            self.add_mode_apply_method(i)

    def add_key_press_method(self, key):
        "Creates a series of methods to enter a `mode` for when key is pressed"
        name = 'key_pressed_'+key
        def key_press_method(self, event):
            self.set_mode(key)
        setattr(FigureWithBindings, name, key_press_method)

    def add_mode_apply_method(self, mode):
        "Creates a series of methods to apply a `mode` for a left-click event"
        name = 'mode_apply_' + mode
        def apply_mode_method(self, event):
            x, y, xv, yv = event.x, event.y, event.xdata, event.ydata
            cat_data = (mode,xv,yv)
            print("Adding: ", cat_data )
            self.categorized_points.append(cat_data)
            self.ax.scatter([xv], [yv], color=self.mode_color_dict[mode])
            self.redraw()
        setattr(FigureWithBindings, name, apply_mode_method)

    def set_mode(self, mode: str):
        print("Mode: ", mode)
        self.mode = mode

    def onkeypress(self, event):
        """Calls the appropriate method on key pressed.
        Key-press methods have to be named; `key_pressed_<key>`
        """ 
        print("key: ", event.key)
        getattr(self, 'key_pressed_' + event.key)(event)

    def onclick(self, event):
        if event.button == 1: # left click
            getattr(self, 'mode_apply_' + self.mode)(event)
        elif event.button == 3: # right click
            self.remove_last_point(event)

    def remove_last_point(self, event):
        self.ax.collections.pop(-1)
        r = self.categorized_points.pop(-1)
        print("Removed: ", r)
        self.redraw()

    def key_pressed_q(self, event):
        self.quit(event)

    def quit(self, event):
        my_data = self.post_fun(self.categorized_points)
        plt.close()
        self.creator.take_my_data(my_data)
        self.creator.gimme_more()

    def redraw(self):
        self.fig.canvas.draw()

class DataUnit:
    def __init__(self, arr, name):
        self.name = name
        self.data = arr
        self.annotation = None
 


