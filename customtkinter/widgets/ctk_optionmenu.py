import tkinter
import sys
from typing import Union, Tuple, Callable

from .ctk_canvas import CTkCanvas
from ..theme_manager import ThemeManager
from ..settings import Settings
from ..draw_engine import DrawEngine
from .widget_base_class import CTkBaseClass
from .dropdown_menu import DropdownMenu


class CTkOptionMenu(CTkBaseClass):
    """
    Optionmenu with rounded corners, dropdown menu, variable support, command.
    For detailed information check out the documentation.
    """

    def __init__(self, *args,
                 width: int = 140,
                 height: int = 28,
                 corner_radius: Union[int, str] = "default_theme",

                 bg_color: Union[str, Tuple[str, str], None] = None,
                 fg_color: Union[str, Tuple[str, str]] = "default_theme",
                 button_color: Union[str, Tuple[str, str]] = "default_theme",
                 button_hover_color: Union[str, Tuple[str, str]] = "default_theme",
                 text_color: Union[str, Tuple[str, str]] = "default_theme",
                 text_color_disabled: Union[str, Tuple[str, str]] = "default_theme",
                 dropdown_fg_color: Union[str, Tuple[str, str]] = "default_theme",
                 dropdown_hover_color: Union[str, Tuple[str, str]] = "default_theme",
                 dropdown_text_color: Union[str, Tuple[str, str]] = "default_theme",

                 font: any = "default_theme",
                 dropdown_text_font: any = "default_theme",
                 values: list = None,
                 variable: tkinter.Variable = None,
                 state: str = tkinter.NORMAL,
                 hover: bool = True,
                 command: Callable = None,
                 dynamic_resizing: bool = True,
                 **kwargs):

        # transfer basic functionality (_bg_color, size, _appearance_mode, scaling) to CTkBaseClass
        super().__init__(*args, bg_color=bg_color, width=width, height=height, **kwargs)

        # color variables
        self._fg_color = ThemeManager.theme["color"]["button"] if fg_color == "default_theme" else fg_color
        self._button_color = ThemeManager.theme["color"]["optionmenu_button"] if button_color == "default_theme" else button_color
        self._button_hover_color = ThemeManager.theme["color"]["optionmenu_button_hover"] if button_hover_color == "default_theme" else button_hover_color

        # shape
        self._corner_radius = ThemeManager.theme["shape"]["button_corner_radius"] if corner_radius == "default_theme" else corner_radius

        # text and font
        self._text_color = ThemeManager.theme["color"]["text"] if text_color == "default_theme" else text_color
        self._text_color_disabled = ThemeManager.theme["color"]["text_button_disabled"] if text_color_disabled == "default_theme" else text_color_disabled
        self._font = (ThemeManager.theme["text"]["font"], ThemeManager.theme["text"]["size"]) if font == "default_theme" else font
        self._dropdown_text_font = dropdown_text_font

        # callback and hover functionality
        self._command = command
        self._variable = variable
        self._variable_callback_blocked: bool = False
        self._variable_callback_name: Union[str, None] = None
        self._state = state
        self._hover = hover
        self._dynamic_resizing = dynamic_resizing

        if values is None:
            self._values = ["CTkOptionMenu"]
        else:
            self._values = values

        if len(self._values) > 0:
            self._current_value = self._values[0]
        else:
            self._current_value = "CTkOptionMenu"

        self._dropdown_menu = DropdownMenu(master=self,
                                           values=self._values,
                                           command=self._dropdown_callback,
                                           fg_color=dropdown_fg_color,
                                           hover_color=dropdown_hover_color,
                                           text_color=dropdown_text_color,
                                           font=dropdown_text_font)

        # configure grid system (1x1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._canvas = CTkCanvas(master=self,
                                 highlightthickness=0,
                                 width=self._apply_widget_scaling(self._desired_width),
                                 height=self._apply_widget_scaling(self._desired_height))
        self._canvas.grid(row=0, column=0, rowspan=1, columnspan=1, sticky="nsew")
        self._draw_engine = DrawEngine(self._canvas)

        left_section_width = self._current_width - self._current_height
        self._text_label = tkinter.Label(master=self,
                                         font=self._apply_font_scaling(self._font),
                                         anchor="w",
                                         text=self._current_value)
        self._text_label.grid(row=0, column=0, sticky="w",
                              padx=(max(self._apply_widget_scaling(self._corner_radius), self._apply_widget_scaling(3)),
                                    max(self._apply_widget_scaling(self._current_width - left_section_width + 3), self._apply_widget_scaling(3))))

        if not self._dynamic_resizing:
            self.grid_propagate(0)

        if Settings.cursor_manipulation_enabled:
            if sys.platform == "darwin":
                self.configure(cursor="pointinghand")
            elif sys.platform.startswith("win"):
                self.configure(cursor="hand2")

        # event bindings
        self._canvas.bind("<Enter>", self._on_enter)
        self._canvas.bind("<Leave>", self._on_leave)
        self._canvas.bind("<Button-1>", self._clicked)
        self._canvas.bind("<Button-1>", self._clicked)

        self._text_label.bind("<Enter>", self._on_enter)
        self._text_label.bind("<Leave>", self._on_leave)
        self._text_label.bind("<Button-1>", self._clicked)
        self._text_label.bind("<Button-1>", self._clicked)

        self.bind('<Configure>', self._update_dimensions_event)

        self._draw()  # initial draw

        if self._variable is not None:
            self._variable_callback_name = self._variable.trace_add("write", self._variable_callback)
            self._current_value = self._variable.get()
            self._text_label.configure(text=self._current_value)

    def _set_scaling(self, *args, **kwargs):
        super()._set_scaling(*args, **kwargs)

        # change label text size and grid padding
        left_section_width = self._current_width - self._current_height
        self._text_label.configure(font=self._apply_font_scaling(self._font))
        self._text_label.grid(row=0, column=0, sticky="w",
                              padx=(max(self._apply_widget_scaling(self._corner_radius), self._apply_widget_scaling(3)),
                                    max(self._apply_widget_scaling(self._current_width - left_section_width + 3), self._apply_widget_scaling(3))))

        self._canvas.configure(width=self._apply_widget_scaling(self._desired_width),
                               height=self._apply_widget_scaling(self._desired_height))
        self._draw()

    def _set_dimensions(self, width: int = None, height: int = None):
        super()._set_dimensions(width, height)

        self._canvas.configure(width=self._apply_widget_scaling(self._desired_width),
                               height=self._apply_widget_scaling(self._desired_height))
        self._draw()

    def _draw(self, no_color_updates=False):
        left_section_width = self._current_width - self._current_height
        requires_recoloring = self._draw_engine.draw_rounded_rect_with_border_vertical_split(self._apply_widget_scaling(self._current_width),
                                                                                             self._apply_widget_scaling(self._current_height),
                                                                                             self._apply_widget_scaling(self._corner_radius),
                                                                                             0,
                                                                                             self._apply_widget_scaling(left_section_width))

        requires_recoloring_2 = self._draw_engine.draw_dropdown_arrow(self._apply_widget_scaling(self._current_width - (self._current_height / 2)),
                                                                      self._apply_widget_scaling(self._current_height / 2),
                                                                      self._apply_widget_scaling(self._current_height / 3))

        if no_color_updates is False or requires_recoloring or requires_recoloring_2:

            self._canvas.configure(bg=ThemeManager.single_color(self._bg_color, self._appearance_mode))

            self._canvas.itemconfig("inner_parts_left",
                                    outline=ThemeManager.single_color(self._fg_color, self._appearance_mode),
                                    fill=ThemeManager.single_color(self._fg_color, self._appearance_mode))
            self._canvas.itemconfig("inner_parts_right",
                                    outline=ThemeManager.single_color(self._button_color, self._appearance_mode),
                                    fill=ThemeManager.single_color(self._button_color, self._appearance_mode))

            self._text_label.configure(fg=ThemeManager.single_color(self._text_color, self._appearance_mode))

            if self._state == tkinter.DISABLED:
                self._text_label.configure(fg=(ThemeManager.single_color(self._text_color_disabled, self._appearance_mode)))
                self._canvas.itemconfig("dropdown_arrow",
                                        fill=ThemeManager.single_color(self._text_color_disabled, self._appearance_mode))
            else:
                self._text_label.configure(fg=ThemeManager.single_color(self._text_color, self._appearance_mode))
                self._canvas.itemconfig("dropdown_arrow",
                                        fill=ThemeManager.single_color(self._text_color, self._appearance_mode))

            self._text_label.configure(bg=ThemeManager.single_color(self._fg_color, self._appearance_mode))

        self._canvas.update_idletasks()

    def config(self, *args, **kwargs):
        return self.configure(*args, **kwargs)

    def configure(self, require_redraw=False, **kwargs):
        if "state" in kwargs:
            self._state = kwargs.pop("state")
            require_redraw = True

        if "fg_color" in kwargs:
            self._fg_color = kwargs.pop("fg_color")
            require_redraw = True

        if "button_color" in kwargs:
            self._button_color = kwargs.pop("button_color")
            require_redraw = True

        if "button_hover_color" in kwargs:
            self._button_hover_color = kwargs.pop("button_hover_color")
            require_redraw = True

        if "text_color" in kwargs:
            self._text_color = kwargs.pop("text_color")
            require_redraw = True

        if "font" in kwargs:
            self._font = kwargs.pop("font")
            self._text_label.configure(font=self._apply_font_scaling(self._font))

        if "command" in kwargs:
            self._command = kwargs.pop("command")

        if "variable" in kwargs:
            if self._variable is not None:  # remove old callback
                self._variable.trace_remove("write", self._variable_callback_name)

            self._variable = kwargs.pop("variable")

            if self._variable is not None and self._variable != "":
                self._variable_callback_name = self._variable.trace_add("write", self._variable_callback)
                self._current_value = self._variable.get()
                self._text_label.configure(text=self._current_value)
            else:
                self._variable = None

        if "width" in kwargs:
            self._set_dimensions(width=kwargs.pop("width"))

        if "height" in kwargs:
            self._set_dimensions(height=kwargs.pop("height"))

        if "values" in kwargs:
            self._values = kwargs.pop("values")
            self._dropdown_menu.configure(values=self._values)

        if "dropdown_color" in kwargs:
            self._dropdown_menu.configure(fg_color=kwargs.pop("dropdown_color"))

        if "dropdown_hover_color" in kwargs:
            self._dropdown_menu.configure(hover_color=kwargs.pop("dropdown_hover_color"))

        if "dropdown_text_color" in kwargs:
            self._dropdown_menu.configure(text_color=kwargs.pop("dropdown_text_color"))

        if "dropdown_text_font" in kwargs:
            self._dropdown_text_font = kwargs.pop("dropdown_text_font")
            self._dropdown_menu.configure(text_font=self._dropdown_text_font)

        if "dynamic_resizing" in kwargs:
            self._dynamic_resizing = kwargs.pop("dynamic_resizing")
            if not self._dynamic_resizing:
                self.grid_propagate(0)
            else:
                self.grid_propagate(1)

        super().configure(require_redraw=require_redraw, **kwargs)

    def cget(self, attribute_name: str) -> any:
        if attribute_name == "corner_radius":
            return self._corner_radius

        elif attribute_name == "fg_color":
            return self._fg_color
        elif attribute_name == "button_color":
            return self._button_color
        elif attribute_name == "button_hover_color":
            return self._button_hover_color
        elif attribute_name == "text_color":
            return self._text_color
        elif attribute_name == "text_color_disabled":
            return self._text_color_disabled
        elif attribute_name == "dropdown_fg_color":
            return self._dropdown_menu.cget("fg_color")
        elif attribute_name == "dropdown_hover_color":
            return self._dropdown_menu.cget("hover_color")
        elif attribute_name == "dropdown_text_color":
            return self._dropdown_menu.cget("text_color")

        elif attribute_name == "font":
            return self._font
        elif attribute_name == "dropdown_text_font":
            return self._dropdown_menu.cget("text_font")
        elif attribute_name == "values":
            return self._values
        elif attribute_name == "variable":
            return self._variable
        elif attribute_name == "state":
            return self._state
        elif attribute_name == "hover":
            return self._hover
        elif attribute_name == "command":
            return self._command
        elif attribute_name == "dynamic_resizing":
            return self._dynamic_resizing
        else:
            return super().cget(attribute_name)

    def _open_dropdown_menu(self):
        self._dropdown_menu.open(self.winfo_rootx(),
                                 self.winfo_rooty() + self._apply_widget_scaling(self._current_height + 0))

    def _on_enter(self, event=0):
        if self._hover is True and self._state == tkinter.NORMAL and len(self._values) > 0:
            # set color of inner button parts to hover color
            self._canvas.itemconfig("inner_parts_right",
                                    outline=ThemeManager.single_color(self._button_hover_color, self._appearance_mode),
                                    fill=ThemeManager.single_color(self._button_hover_color, self._appearance_mode))

    def _on_leave(self, event=0):
        if self._hover is True:
            # set color of inner button parts
            self._canvas.itemconfig("inner_parts_right",
                                    outline=ThemeManager.single_color(self._button_color, self._appearance_mode),
                                    fill=ThemeManager.single_color(self._button_color, self._appearance_mode))

    def _variable_callback(self, var_name, index, mode):
        if not self._variable_callback_blocked:
            self._current_value = self._variable.get()
            self._text_label.configure(text=self._current_value)

    def _dropdown_callback(self, value: str):
        self._current_value = value
        self._text_label.configure(text=self._current_value)

        if self._variable is not None:
            self._variable_callback_blocked = True
            self._variable.set(self._current_value)
            self._variable_callback_blocked = False

        if self._command is not None:
            self._command(self._current_value)

    def set(self, value: str):
        self._current_value = value
        self._text_label.configure(text=self._current_value)

        if self._variable is not None:
            self._variable_callback_blocked = True
            self._variable.set(self._current_value)
            self._variable_callback_blocked = False

    def get(self) -> str:
        return self._current_value

    def _clicked(self, event=0):
        if self._state is not tkinter.DISABLED and len(self._values) > 0:
            self._open_dropdown_menu()
