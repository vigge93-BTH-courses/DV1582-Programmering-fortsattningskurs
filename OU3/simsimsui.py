import io
import sys
from copy import copy, deepcopy
from math import cos, pi, sin, sqrt
from tkinter import font

import mtTkinter

""" A text and graphical user iterface for a SImSims network """


class Coords():
    ''' 
    Represent coordinate pairs.

    Args:
        x1,y1,x2,y2,...: a sequence of coordinate pairs
    '''

    def __init__(self, *args, **kwargs):
        self._coords = []
        self.append(*args)

    def __copy__(self):
        newone = type(self)()
        newone._coords = deepcopy(self._coords)
        return newone

    def __iter__(self):
        return self._coords.__iter__()

    def __getitem__(self, i):
        return self._coords[i]

    def __len__(self):
        return len(self._coords)

    def __str__(self):
        return "["+", ".join([str(f) for f in self._coords])+"]"

    def append(self, *args):
        ''' Append one or several coordinate pairs.
            Args:
               x1, y1, x2, y2, ...:    list of coordinate pairs
        '''
        nargs = len(args)
        assert nargs % 2 == 0
        for i in range(0, nargs, 2):
            self._coords.extend((float(args[i]), float(args[i+1])))

    def translate(self, *args):
        ''' Returns a copy of stored coordinates, translated with dx, dy.
            Args:
                dx, dy: value by witch to translate coordinates.
        '''
        if len(args) == 1:
            assert isinstance(args[0], Coords) and len(args[0]) == 2
            dx, dy = args[0][:]
        elif len(args) == 2:
            dx, dy = args[:]
        else:
            raise ValueError("To many or wrong arguments")

        nw = type(self)()
        for i in range(0, len(self._coords), 2):
            nw.append(self._coords[i]+dx, self._coords[i+1]+dy)
        return nw


class SimSimsUI():
    ''' Abstract class for a SimSims User Interface. 
        A UI object create other ui objects for tokens, 
        places and transitions.
    '''

    def __init__(self):
        self._uis = []
        self._on_shoot = None

    def _create_place_ui(self, properties):
        raise NotImplementedError()

    def _create_token_ui(self, properties):
        raise NotImplementedError()

    def _create_transition_ui(self, properties):
        raise NotImplementedError()

    def _create_arc_ui(self, src_d, dst_d, properties):
        return None

    def _shoot(self):
        """ Call the on_shoot callback if present. """
        if self._on_shoot:
            self._on_shoot()

    def create_place_ui(self, properties={}):
        ''' Creates an UI for a place.
            Args:
                owner:  The place that uses the ui
                properties: Properties to the ui (see subclass documentation)
        '''
        ui = self._create_place_ui(properties)
        if ui:
            self._uis.append(ui)

        return ui

    def create_token_ui(self, properties={}):
        ''' Creates an UI for a token.
            Args:
                owner:  The token that uses the ui
                properties: Properties to the ui (see subclass documentation)
        '''
        ui = self._create_token_ui(properties)
        return ui

    def create_transition_ui(self, properties={}):
        ''' Creates an UI for a transition.
            Args:
                owner:  The transition that uses the ui
                properties: Properties to the ui (see subclass documentation)
        '''
        ui = self._create_transition_ui(properties)
        if ui:
            self._uis.append(ui)

        return ui

    def connect(self, src_ui, dst_ui, properties={}):
        ''' Connects the src_ui node_ui ui to dst_ui's UI. 
            No other other purpose than visual.
            Args:
                src_ui: src of an arc.
                dst_ui: dst of an arc.
        '''
        if [x for x in src_ui._arcs if x._out == dst_ui]:
            return

        barcs = [x for x in dst_ui._arcs if x._out == src_ui]
        if barcs:
            barcs[0].bidirectional = True
        else:
            a_ui = self._create_arc_ui(src_ui, dst_ui, properties)
            if a_ui:
                a_ui._out = dst_ui
                a_ui._in = src_ui
                src_ui._arcs.append(a_ui)
                dst_ui._arcs.append(a_ui)
                a_ui.update_position()

    def remove(self, ui):
        ''' Removes a node from the ui.
            Args:
                node_ui: node to remove.
        '''
        if ui in self._uis:
            self._uis.remove(ui)
        ui.shoot()

    def update_ui(self):
        ''' Function that initiate an update of the interface. 
            Typically called at the same interval as the simulation clock or 
            in a separate loop if multi-threaded .

            This function is implemented by subclasses.
        '''
        raise NotImplementedError()

    def on_shoot(self, fkn):
        """ Set function to call when UI signals a shoot """
        self._on_shoot = fkn

    def shoot(self):
        ''' Function to call after the simulation is halted to close 
            any open windows or output channels.

            This function is implemented by subclasses.
        '''
        raise NotImplementedError()


class UIDrawer:
    """ Abstract class for a drawer. """

    def __init__(self, properties={}):
        self._properties = {}
        self.properties = properties

    @property
    def properties(self):
        return self._properties

    @properties.setter
    def properties(self, properties):
        self._verify_properties(copy(properties))

    def _verify_properties(self, properties):
        self.properties.update(properties)

    def draw(self, content_drawers=[]):
        ''' Draws the UI for the component.
        '''
        raise NotImplementedError()

    def shoot(self):
        pass


class UIComponent:
    """ A ui component, that has a drawer to visualize it """

    def __init__(self, drawer):
        self._drawer = drawer

    @property
    def drawer(self):
        return self._drawer

    def update_properties(self, properties):
        """ Update the properties """
        self.drawer.properties = properties

    def draw(self):
        self._draw()

    def _draw(self):
        self.drawer.draw()

    def shoot(self):
        self.drawer.shoot()


class UINodeComponent(UIComponent):
    ''' A node component in the ui.
        Args:
            drawer
        Properties:
            tokens: number of tokens
    '''

    def __init__(self, drawer):
        UIComponent.__init__(self, drawer)
        self._arcs = []
        self._tokens = []

    @property
    def tokens(self):
        """ Number of tokens """
        return len(self._tokens)

    def _draw(self):
        """ Redefine from UIComponent """
        self._drawer.draw(self._tokens)

    def add_token(self, token_ui):
        ''' Add a token UI to this node_ui.
            Args:
                token_ui: UI of the token to add.
        '''
        self._tokens.append(token_ui)

    def remove_token(self, token_ui):
        ''' Remove a token UI to this node_ui.
            Args:
                token_ui: UI of the token to remove.
        '''
        self._tokens.remove(token_ui)

    def autoplace(self, index, places):
        ''' Place a graphical ui component.
            Args:
                index: the index of the component to place.
                places: the number of spots. Should be the same for all components.
        '''
        pass

    def rmove(self, dx, dy):
        ''' Moves a graphical component relative its current possition.
            Args:
                dx: relative move in x-direction
                dy: relative move in y-direction
        '''
        pass

    def shoot(self):
        for arc in copy(self._arcs):
            arc._in._arcs.remove(arc)
            arc._out._arcs.remove(arc)

            arc.shoot()
        UIComponent.shoot(self)
        self._tokens.clear()


class UIArcComponent(UIComponent):
    """An arc component in the ui."""

    def __init__(self, outc, inc, drawer):
        self._in = inc
        self._out = outc
        UIComponent.__init__(self, drawer)

    @property
    def bidirectional(self):
        return self.drawer.bidirectional

    @bidirectional.setter
    def bidirectional(self, b):
        self.drawer.bidirectional = b

    def update_position(self):
        """ Update the position of the arc's drawer """
        self.drawer.update_position(self._in.drawer, self._out.drawer)


class SimSimsTextUI(SimSimsUI):
    ''' A text UI. 
    '''

    def __init__(self, channel=io.StringIO()):
        self._fout = channel
        SimSimsUI.__init__(self)

    def _create_place_ui(self, properties={}):
        return UINodeComponent(TextUINodeDrawer(self._fout, "Place", properties))

    def _create_transition_ui(self, properties={}):
        return UINodeComponent(TextUINodeDrawer(self._fout, "Transition", properties))

    def _create_token_ui(self, properties):
        return UIComponent(TextUITokenDrawer(self._fout, properties))

    def update_ui(self):
        """ Overrides from SimSimsUI. """
        self._fout.write("-----------------------------------\n")
        for ui in self._uis:
            ui.draw()
            self._fout.write("\n")
        self._fout.write("-----------------------------------\n")
        print(self._fout.getvalue(), file=sys.stdout)


class TextUINodeDrawer(UIDrawer):
    ''' A text drawer for a place.
    '''

    def __init__(self, fout, lable, properties={}):
        UIDrawer.__init__(self, properties)
        self._lable = lable
        self._fout = fout

    def draw(self, content_drawers=[]):
        """ Overrides from UIDrawer. """
        self._fout.write(self._lable)
        if "lable" in self.properties.keys():
            self._fout.write(" ("+self.properties["lable"]+")")
        self._fout.write(": ")
        for drawer in content_drawers:
            drawer.draw()


class TextUITokenDrawer(UIDrawer):
    ''' A text drawer for a token. 
    '''

    def __init__(self, fout, properties={}):
        UIDrawer.__init__(self, properties)
        self._fout = fout

    def draw(self, content_drawer=[]):
        """ Overrides from UIDrawer """
        self._fout.write("*")


class SimSimsGUI(mtTkinter.Tk, SimSimsUI):
    """ A Graphical UI. """

    def __init__(self, w=400, h=400):
        mtTkinter.Tk.__init__(self)

        self.protocol("WM_DELETE_WINDOW", self._shoot)
        # make Esc exit the program
        self.bind('<Escape>', lambda e: self._shoot())

        SimSimsUI.__init__(self)
        self._canvas = mtTkinter.Canvas(self, width=w, height=h)
        self._canvas.pack()
        self.update()

    @property
    def canvas(self):
        """ The canvas used for drawing objects. """
        return self._canvas

    def _create_place_ui(self, properties):
        return GUINodeComponent(GUIPlaceDrawer(self.canvas, properties))

    def _create_transition_ui(self, properties):
        return GUINodeComponent(GUITransitionDrawer(self.canvas, properties))

    def _create_token_ui(self, properties):
        return UIComponent(GUITokenDrawer(self.canvas, properties))

    def _create_arc_ui(self, src_d, dst_d, properties):
        return UIArcComponent(src_d, dst_d, GUIArcDrawer(self.canvas, properties))

    def _shoot(self):
        """ Overrides from SimSimsUI """
        SimSimsUI._shoot(self)
        mtTkinter.Tk.iconify(self)

    def update_ui(self):
        """ Overrides from TokenUI """
        if self.winfo_exists():
            self.canvas.update()
            self.update_idletasks()
            self.update()

    def shoot(self):
        """ Overrides from SimSimsUI. """
        mtTkinter.Tk.destroy(self)


class GUINodeComponent(UINodeComponent):
    """A graphical node component. """

    def __init__(self, drawer):
        UINodeComponent.__init__(self, drawer)

    def autoplace(self, index, n_places):
        """ Overrides from UINodeComponent. """
        w, h = (self.drawer.canvas.winfo_width(),
                self.drawer.canvas.winfo_height())
        allpos = GUIDrawer.sunflower(
            n_places, 1.0, min(w, h)/2-1.5*self.drawer._radius)
        x = w // 2
        y = h // 2

        self.drawer.position = Coords(x, y).translate(allpos[index-1])
        for a in self._arcs:
            a.update_position()
        self.draw()

    def rmove(self, dx, dy):
        """ Overrides from UINodeComponent. """
        self.drawer.position = self.drawer.position.translate(dx, dy)
        for a in self._arcs:
            a.update_position()
        self.draw()

    def add_token(self, token):
        """ Overrides from UINodeComponent. """
        token.drawer.position = copy(self.drawer.position)
        UINodeComponent.add_token(self, token)
        self.draw()

    def remove_token(self, token):
        """ Overrides from UINodeComponent. """
        token.drawer.position = Coords(0.0, 0.0)
        UINodeComponent.remove_token(self, token)
        self.draw()


class GUIDrawer(UIDrawer):
    ''' An abstract GUI drawer.

        Args:
            canvas: The canvas from the GUI-window
            properties: Common properties for GUI components.
    '''

    def __init__(self, canvas, properties):
        UIDrawer.__init__(self, properties)

        self._shapes = []
        self._xy = Coords(0.0, 0.0)
        self._canvas = canvas
        self._define()

    def _verify_properties(self, properties):
        """ Override from UIDrawer """
        UIDrawer._verify_properties(self, properties)
        if not "color" in self.properties.keys():
            self.properties["color"] = "#000"

    @property
    def canvas(self):
        """ The canvas used for drawing objects. """
        return self._canvas

    @property
    def shapes(self):
        """ The canvas used for drawing objects. """
        return self._shapes

    @property
    def position(self):
        """ The position of the object """
        return self._get_position()

    @position.setter
    def position(self, *args):
        """ Sets the position of the object as coordinate pair."""
        self._set_position(*args)

    def _get_position(self):
        return self._xy

    def _set_position(self, *args):
        if len(args) == 1:
            assert isinstance(args[0], Coords) and len(args[0]) == 2
            self._xy = args[0]
        elif len(args) == 2:
            self._xy = Coords(args[0], args[1])

    def _define(self):
        raise NotImplementedError()

    def draw(self, content_drawers=[]):
        """ Draws the component """
        for s in self._shapes:
            if s[1]:
                coords = s[1].translate(self.position)
                self.canvas.coords(s[0], coords[:])
        for drawer in content_drawers:
            drawer.draw()

    def shoot(self):
        UIDrawer.shoot(self)
        for shape in self._shapes:
            self.canvas.delete(shape[0])
        self._shapes.clear()

    @classmethod
    def _sf_radius(cls, k, n, b):
        if k > n-b:
            r = 1
        else:
            r = sqrt(k-1/2)/sqrt(n-(b+1)/2)
        return r

    @classmethod
    def sunflower(cls, n, alpha, radius):
        if n == 1:
            return [Coords(0.0, 0.0)]
        pairs = []
        b = round(alpha*sqrt(n))
        phi = (sqrt(5)+1)/2
        for k in range(1, n+1):
            r = radius*GUIDrawer._sf_radius(k, n, b)
            theta = 2*pi*k/phi**2
            x = r*cos(theta)
            y = r*sin(theta)
            pairs.append(Coords(x, y))

        return pairs


class GUITokenDrawer(GUIDrawer):
    """ A graphical token drawer """
    BASE_LENGTH = 2.0

    def __init__(self, canvas, properties={}):
        GUIDrawer.__init__(self, canvas, properties)

    def _define(self):
        shape = self.canvas.create_oval(
            0.0, 0.0, 0.0, 0.0, fill=self.properties["color"], width=0, outline=self.properties["color"])
        self.canvas.tag_raise(shape)
        coords = Coords(-GUITokenDrawer.BASE_LENGTH, -GUITokenDrawer.BASE_LENGTH,
                        GUITokenDrawer.BASE_LENGTH, GUITokenDrawer.BASE_LENGTH)
        self.shapes.append((shape, coords))


class GUINodeDrawer(GUIDrawer):
    """ An abstract graphical node drawer """

    def __init__(self, canvas, size, properties={}):
        self._font = font.Font(family='Arial', size=7)
        self._radius = size
        GUIDrawer.__init__(self, canvas, properties)

    def _verify_properties(self, properties):
        """ Override from UIDrawer """
        GUIDrawer._verify_properties(self, properties)
        if not "fill" in self.properties.keys():
            self.properties["fill"] = "#fff"

    def draw(self, content_drawers):
        """ Overrides from UIDrawer """
        GUIDrawer.draw(self)
        cps = GUIDrawer.sunflower(len(content_drawers), 1.0, 0.8*self._radius)
        for i in range(len(content_drawers)):
            content_drawers[i].drawer.position = cps[i].translate(
                self.position)
            content_drawers[i].draw()

    def anchor_point(self, coord):
        """ Virtual method to calculate an anchor point for an arc. """
        raise NotImplementedError()


class GUIPlaceDrawer(GUINodeDrawer):
    """ A graphical place drawer """

    def __init__(self, canvas, properties={}):
        GUINodeDrawer.__init__(self, canvas, 15.0, properties)

    def _define(self):
        """ Overrides from GUIDrawer """
        shape = self.canvas.create_oval(
            0.0, 0.0, 0.0, 0.0, fill=self.properties["fill"], width=2, outline=self.properties["color"])
        self.canvas.tag_lower(shape)
        coords = Coords(-self._radius, -self._radius,
                        self._radius, self._radius)
        self.shapes.append((shape, coords))
        if "lable" in self.properties.keys():
            shape = self.canvas.create_text(
                0.0, 0.0, text=self.properties["lable"], font=self._font, justify=mtTkinter.CENTER, fill=self.properties["color"])
            coords = Coords(0.0, self._radius+7)
            self.shapes.append((shape, coords))

    def anchor_point(self, coord):
        """ Overrides from GUINodeDrawer """
        x1, y1 = self.position
        x2, y2 = coord[0]-x1, coord[1]-y1
        r = self._radius
        sr = sqrt(x2*x2 + y2*y2)
        if sr > 0:
            x = r*x2/sr
            y = r*y2/sr
        else:
            x = x1
            y = y1-r
        return Coords(x+x1, y+y1)


class GUITransitionDrawer(GUINodeDrawer):
    """ A graphical transition drawer """

    def __init__(self, canvas, properties={}):
        GUINodeDrawer.__init__(self, canvas, 12.0, properties)

    def _define(self):
        """ Overrides from GUIrawer """
        shape = self.canvas.create_rectangle(
            0.0, 0.0, 0.0, 0.0, fill=self.properties["fill"], width=2, outline=self.properties["color"])
        self.canvas.tag_lower(shape)
        coords = Coords(-self._radius, -self._radius,
                        self._radius, self._radius)
        self._shapes.append((shape, coords, self.properties))
        if "lable" in self.properties.keys():
            shape = self.canvas.create_text(
                0.0, 0.0, text=self.properties["lable"], font=self._font, justify=mtTkinter.CENTER, fill=self.properties["color"])
            coords = Coords(0.0, self._radius+7)
            self.shapes.append((shape, coords))

    def anchor_point(self, coord):
        """ Overrides from GUINodeDrawer """
        x1, y1 = self.position[0], self.position[1]
        dx, dy = coord[0]-x1, coord[1]-y1
        dxa, dya = abs(dx), abs(dy)

        if dxa < 0.0001 and dya < 0.0001:
            (x, y) = (0.0, 0.0)
        elif dxa > dya:
            x = self._radius
            y = self._radius*dya/dxa
        else:
            x = self._radius*dxa/dya
            y = self._radius

        if dx < 0.0:
            x = -x
        if dy < 0.0:
            y = -y

        return Coords(x+x1, y+y1)


class GUIArcDrawer(GUIDrawer):
    """ A graphical arc drawer """

    def __init__(self, canvas, properties={}):
        self._bidirectional = False
        GUIDrawer.__init__(self, canvas, properties)

    @property
    def bidirectional(self):
        return self._bidirectional

    @bidirectional.setter
    def bidirectional(self, b):
        if not self.properties["arrows"]:
            return
        if b:
            self.canvas.itemconfig(self._shapes[0][0], arrow=mtTkinter.BOTH)
        else:
            self.canvas.itemconfig(self._shapes[0][0], arrow=mtTkinter.LAST)
        self._bidirectional = b

    def _define(self):
        """ Overrides from GUIDrawer """
        coord1 = Coords(0.0, 0.0)
        coord2 = Coords(0.0, 0.0)
        arrow = None
        if self.properties["arrows"]:
            arrow = mtTkinter.LAST
        s = self.canvas.create_line(
            coord1[0], coord1[1], coord2[0], coord2[1], fill=self.properties["color"], width=3, arrow=arrow)
        self.shapes.append((s, None))

    def _verify_properties(self, properties):
        """ Override from UIDrawer """
        GUIDrawer._verify_properties(self, properties)
        if not "arrows" in self.properties.keys():
            self.properties["arrows"] = False

    def update_position(self, src_d, dst_d):
        """ Update the position of the arc if any node change its position. """
        coord1 = src_d.anchor_point(dst_d.position)
        coord2 = dst_d.anchor_point(src_d.position)
        coords = Coords(coord1[0], coord1[1], coord2[0], coord2[1])

        s = self.shapes[0][0]
        self.canvas.coords(s, coords[:])


__author__ = 'Pedher Johansson'
__copyright__ = 'Copyright 2020, FortsÃ¤ttningskurs i Python'
__version__ = '1.2'
__email__ = 'pedher.johansson@bth.se'
