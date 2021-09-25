# python standard libraries
import os
import pathlib
import pickle
import threading
import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askopenfilename
from tkinter.filedialog import askdirectory
from tkinter import messagebox


# custom/local libraries
import randomizer
from randosettings import Settings, GameFlags, Difficulty, ShopPrices, \
    TechOrder, TabRandoScheme


#
# tkinter does not have a native tooltip implementation.
# This tooltip implementation is stolen from Stack Overflow:
# https://stackoverflow.com/a/36221216
# Re-stolen from Anguirel's original implementation
#
class CreateToolTip(object):
    """
    create a tooltip for a given widget
    """
    def __init__(self, widget, text='widget info'):
        self.waittime = 800     # miliseconds
        self.wraplength = 300   # pixels
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.widget.bind("<ButtonPress>", self.leave)
        self.id = None
        self.tw = None

    def enter(self, event=None):
        self.schedule()

    def leave(self, event=None):
        self.unschedule()
        self.hidetip()

    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(self.waittime, self.showtip)

    def unschedule(self):
        id = self.id
        self.id = None
        if id:
            self.widget.after_cancel(id)

    def showtip(self, event=None):
        x = y = 0
        x, y, cx, cy = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20
        # creates a toplevel window
        self.tw = tk.Toplevel(self.widget)
        # Leaves only the label and removes the app window
        self.tw.wm_overrideredirect(True)
        self.tw.wm_geometry("+%d+%d" % (x, y))
        label = tk.Label(self.tw, text=self.text, justify='left',
                         background="#ffffff", relief='solid', borderwidth=1,
                         wraplength=self.wraplength)
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tw
        self.tw = None
        if tw:
            tw.destroy()
# end class CreateToolTip


# Going to make a class for the gui to avoid reliance on globals
class RandoGUI:

    difficulty_dict = dict((x, str(x)) for x in list(Difficulty))
    difficulty_inverse_dict = dict(
        (y, x) for (x, y) in difficulty_dict.items()
    )

    shop_price_dict = dict((x, str(x)) for x in list(ShopPrices))
    shop_price_inverse_dict = dict(
        (y, x) for (x, y) in shop_price_dict.items()
    )

    tech_order_dict = dict((x, str(x)) for x in list(TechOrder))
    tech_order_inverse_dict = dict(
        (y, x) for (x, y) in tech_order_dict.items()
    )

    def __init__(self):
        self.main_window = tk.Tk()
        self.main_window.wm_title('Jets of Time')

        # Now that we have a tk window, we can make the variables
        # Game config variables
        self.flag_dict = dict()
        for x in list(GameFlags):
            self.flag_dict[x] = tk.IntVar()

        self.item_difficulty = tk.StringVar()
        self.enemy_difficulty = tk.StringVar()
        self.shop_prices = tk.StringVar()
        self.tech_order = tk.StringVar()

        self.power_tab_max = tk.IntVar()
        self.power_tab_min = tk.IntVar()

        self.magic_tab_max = tk.IntVar()
        self.magic_tab_min = tk.IntVar()

        self.speed_tab_max = tk.IntVar()
        self.speed_tab_min = tk.IntVar()

        self.tab_rando_scheme = tk.StringVar()
        self.tab_success_chance = tk.DoubleVar()

        # By default, dc puts no restrictions on assignment
        self.char_choices = [[tk.IntVar(value=1) for i in range(7)]
                             for j in range(7)]

        self.duplicate_duals = tk.IntVar(value=0)

        # generation variables
        self.seed = tk.StringVar()
        self.input_file = tk.StringVar()
        self.output_file = tk.StringVar()

        self.gen_thread = None

        # Set up the notebook tabs
        self.notebook = ttk.Notebook(self.main_window)
        self.notebook.pack(expand=True)

        self.get_general_page()
        self.get_tabs_page()
        self.dc_page = self.get_dc_page()

        self.notebook.add(self.general_page,
                          text='General')

        self.notebook.add(self.tabs_page,
                          text='Tabs')

        self.notebook.add(self.dc_page, text='DC')

        # This can only be called after all of the widgets are initialized
        self.load_settings_file()

    def get_settings(self):
        return self.__settings

    def set_settings(self, new_settings: Settings):
        self.__settings = new_settings
        print(self.__settings.gameflags)
        self.update_gui_vars()

    settings = property(get_settings, set_settings)

    # Methods for loading/unloading settings file.  Should be out of class?
    # Mostly copied from Anguirel's original
    def get_settings_file(self):
        filePath = ""
        if os.name == "nt":
            # If on Windows, put the settings file in roaming appdata
            dir = os.getenv('APPDATA')
            filePath = pathlib.Path(dir).joinpath('JetsOfTime')
        else:
            # If on Mac/Linux, make it a hidden file in the home directory
            filePath = pathlib.Path(os.path.expanduser('~')).joinpath(
                '.JetsOfTime')

        # changing from settings.dat to flags.dat to avoid errors reading
        # the old style settings object
        return filePath.joinpath("flags.dat")

    def save_settings(self):
        filePath = self.get_settings_file()
        if not filePath.parent.exists():
            filePath.parkent.mkdir()

        with open(str(filePath), 'wb') as outfile:
            pickle.dump(
                [self.settings,
                 self.input_file.get(),
                 self.output_file.get()],
                outfile
            )

    def load_settings_file(self):
        filePath = self.get_settings_file()
        if filePath.exists():
            with open(str(filePath), 'rb') as infile:
                [self.settings, input_file, output_file] = pickle.load(infile)
        else:
            self.settings = Settings.get_new_player_presets()
            self.input_file.set('test1')
            self.output_file.set('test2')

    def update_gui_vars(self):

        # Update the flags
        for x in self.flag_dict.keys():
            if x in self.settings.gameflags:
                self.flag_dict[x].set(1)
            else:
                self.flag_dict[x].set(0)

        # Update difficulties
        self.enemy_difficulty.set(
            Difficulty.str_dict()[self.settings.enemy_difficulty]
        )

        self.item_difficulty.set(
            Difficulty.str_dict()[self.settings.item_difficulty]
        )

        self.shop_prices.set(
            ShopPrices.str_dict()[self.settings.shopprices]
        )

        self.tech_order.set(
            TechOrder.str_dict()[self.settings.techorder]
        )

        # Tab Page Stuff
        self.power_tab_min.set(self.settings.tab_settings.power_min)
        self.power_tab_max.set(self.settings.tab_settings.power_max)

        self.magic_tab_min.set(self.settings.tab_settings.magic_min)
        self.magic_tab_max.set(self.settings.tab_settings.magic_max)

        self.speed_tab_min.set(self.settings.tab_settings.speed_min)
        self.speed_tab_max.set(self.settings.tab_settings.speed_max)

        self.tab_rando_scheme.set(
            TabRandoScheme.str_dict()[self.settings.tab_settings.scheme]
        )
        
        self.verify_settings()

    # Encodes rules for enabling/disabling options depending on what options
    # have been chosen
    def verify_settings(self):
        if self.flag_dict[GameFlags.LOST_WORLDS].get() == 1:
            self.flag_dict[GameFlags.FAST_PENDANT].set(0)
            self.fast_pendant_checkbox.config(state=tk.DISABLED)
        else:
            self.fast_pendant_checkbox.config(state=tk.NORMAL)

        if self.flag_dict[GameFlags.CHRONOSANITY].get() == 1:
            self.flag_dict[GameFlags.BOSS_SCALE].set(0)
            self.boss_scaling_checkbox.config(state=tk.DISABLED)
        else:
            self.boss_scaling_checkbox.config(state=tk.NORMAL)

        if self.flag_dict[GameFlags.DUPLICATE_CHARS].get() == 1:
            self.notebook.tab(self.dc_page, state=tk.NORMAL)
        else:
            self.notebook.tab(self.dc_page, state=tk.DISABLED)

        if self.tab_rando_scheme.get() == \
           TabRandoScheme.str_dict()[TabRandoScheme.UNIFORM]:
            self.tab_prob_scale.config(
                state=tk.DISABLED,
                fg='grey'
            )
        else:
            self.tab_prob_scale.config(
                state=tk.NORMAL,
                fg='black'
            )
        

    # Methods for constructing parts of the layout
    def get_presets_frame(self):
        # Presets
        frame = tk.Frame(
            self.general_page, borderwidth=1,
            highlightbackground="black",
            highlightthickness=1
        )

        row = 0
        # Presets Header
        tk.Label(
            frame,
            text="Preset Selection:"
        ).grid(row=row, column=0, sticky=tk.E)

        def silly(settings: Settings):
            self.settings = settings

        # Preset Buttons
        tk.Button(
            frame, text="Race",
            command=lambda: self.set_settings(
                Settings.get_race_presets()
            )
        ).grid(row=row, column=1)

        tk.Button(
            frame, text="New Player",
            command=lambda: self.set_settings(
                Settings.get_new_player_presets()
            )
        ).grid(row=row, column=2)

        tk.Button(
            frame, text="Lost Worlds",
            command=lambda: self.set_settings(
                Settings.get_lost_worlds_presets()
            )
        ).grid(row=row, column=3)

        tk.Button(
            frame, text="Hard",
            command=lambda: self.set_settings(
                Settings.get_hard_presets()
            )
        ).grid(row=row, column=4)

        return frame

    # should only be called when the dc settings window is up
    def dc_settings_valid(self) -> bool:
        for i in range(7):
            is_set = False
            for j in self.char_choices[i]:
                if j.get() == 1:
                    is_set = True

            if not is_set:
                return False
        return True

    def get_dc_set_char_choices(self, parent):
        dcframe = tk.Frame(
            parent, borderwidth=1, highlightbackground='black',
            highlightthickness=1
        )

        row = 0
        col = 0

        char_names = [
            'Crono', 'Marle', 'Lucca', 'Robo', 'Frog', 'Ayla', 'Magus'
        ]

        row += 1

        for i in range(7):
            tk.Label(
                dcframe,
                text=char_names[i],
                anchor='center'
            ).grid(row=row, column=(i+1))

        row += 1

        for i in range(7):
            tk.Label(
                dcframe,
                text=char_names[i]+' choices:',
                anchor="w"
            ).grid(row=row, column=0)

            col += 1

            for j in range(7):
                tk.Checkbutton(
                    dcframe,  # text=char_names[j],
                    variable=self.char_choices[i][j]
                ).grid(row=row, column=col)

                col += 1

            col = 0
            row += 1

        return dcframe

    def get_dc_set_autofill(self, parent):

        # Helper for setting the underlying variables
        def set_all(val):
            for i in range(7):
                for j in self.char_choices[i]:
                    j.set(val)

        dcframe = tk.Frame(
            parent, borderwidth=1, highlightbackground='black',
            highlightthickness=1
        )

        row = 0

        button = tk.Button(dcframe, text='Check All',
                           command=lambda: set_all(1))
        button.grid(row=row, column=0, columnspan=2)

        button = tk.Button(dcframe, text='Uncheck All',
                           command=lambda: set_all(0))
        button.grid(row=row, column=2, columnspan=2)

        dcframe.pack(fill=tk.X)

        return dcframe

    def get_dc_set_additional_options(self, parent):

        dcframe = tk.Frame(parent, borderwidth=1,
                           highlightbackground='black',
                           highlightthickness=1)

        label = tk.Label(dcframe, text='Additional Options')
        label.grid(row=0, column=0)

        checkbutton = tk.Checkbutton(
            dcframe, text='Duplicate Duals',
            variable=self.duplicate_duals
        )
        checkbutton.grid(row=1, column=0)
        CreateToolTip(checkbutton,
                      'Check this to enable dual techs betweeen copies of the '
                      + 'same character (e.g. Ayla+Ayla beast toss).')

        return dcframe

    def display_dup_char_settings_window(self):

        self.dc_set = tk.Toplevel(self.main_window)
        self.dc_set.protocol('WM_DELETE_WINDOW',
                             self.dc_set_verify_close)

        instruction_frame = tk.Frame(self.dc_set)

        tk.Label(
            instruction_frame,
            text='Indicate allowed character assignments.'
        ).pack(expand=1, fill='both')

        instruction_frame.pack(expand=1, fill='both')

        # self.get_dc_set_char_choices().pack(expand=1, fill='both')
        # self.get_dc_set_autofill().pack(expand=1, fill='both')
        # self.get_dc_set_additional_options().pack(expand=1, fill='both')

        # The Return button doesn't get its own function yet
        dcframe = tk.Frame(
            self.dc_set,
            borderwidth=1,
            highlightbackground='black',
            highlightthickness=1
        )

        button = tk.Button(dcframe, text='Return',
                           command=self.dc_set_verify_close)
        button.grid()

        dcframe.pack(expand=1, fill='both')

        # Is this the right way to lock focus?
        self.dc_set.focus_get()
        self.dc_set.grab_set()

    def get_general_options(self):
        frame = tk.Frame(
            self.general_page, borderwidth=1,
            highlightbackground="black", highlightthickness=1
        )
        row = 0

        label = tk.Label(frame, text="Game Options:")
        label.grid(row=row, column=0, sticky=tk.W)
        row = row + 1

        # Disable glitches
        checkButton = tk.Checkbutton(
            frame,
            text="Disable Glitches (g)",
            variable=self.flag_dict[GameFlags.FIX_GLITCH]
        )
        checkButton.grid(row=row, column=0, sticky=tk.W, columnspan=2)
        CreateToolTip(
            checkButton,
            "Disables common glitches such as the unequip and save " +
            "anywhere glitches."
        )

        # Quiet Mode (No Music)
        checkButton = tk.Checkbutton(
            frame,
            text="Quiet Mode - No Music (q)",
            variable=self.flag_dict[GameFlags.QUIET_MODE]
        )
        checkButton.grid(
            row=row, column=2, sticky=tk.W, columnspan=2
        )
        CreateToolTip(
            checkButton,
            "Music is disabled.  Sound effects will still play."
        )
        row = row + 1

        return frame

    def get_difficulty_options(self):
        frame = tk.Frame(
            self.general_page,
            borderwidth=1, highlightbackground="black", highlightthickness=1
        )

        row = 0

        # Dropdown for enemy difficulty

        # There is no Easy mode for enemy stats
        enemy_difficulty_values = [
            RandoGUI.difficulty_dict[x]
            for x in RandoGUI.difficulty_dict.keys()
            if x != Difficulty.EASY
        ]
        
        label = tk.Label(frame, text="Enemy Difficulty:")
        label.grid(row=row, column=0, sticky=tk.W)

        self.enemy_diff_dropdown = tk.OptionMenu(
            frame, self.enemy_difficulty, *enemy_difficulty_values
        )
        self.enemy_diff_dropdown.grid(
            row=row, column=1, sticky=tk.W, columnspan=2
        )

        CreateToolTip(
            self.enemy_diff_dropdown,
            'On hard mode, some enemies (particularly bosses) have increased '
            'stats and decreased XP/TP rewards.  See \'Hard Tweaks.txt\' '
            'for a complete list of changes.'
        )

        # row += 1

        # Dropdown for item_difficulty difficulty
        item_difficulty_values = RandoGUI.difficulty_dict.values()

        label = tk.Label(frame, text="Item Difficulty:")
        label.grid(row=row, column=3, sticky=tk.W)

        self.item_diff_dropdown = tk.OptionMenu(
            frame, self.item_difficulty, *item_difficulty_values
        )
        self.item_diff_dropdown.grid(
            row=row, column=4, sticky=tk.W, columnspan=2
        )

        CreateToolTip(
            self.item_diff_dropdown,
            'Easier difficulties improve the quality of treasure and enemy '
            'drops.'
        )

        return frame

    def get_general_flags_frame(self):
        frame = tk.Frame(
            self.general_page,
            borderwidth=1,
            highlightbackground="black",
            highlightthickness=1
        )

        row = 0

        label = tk.Label(frame, text="Randomizer Options:")
        label.grid(row=row, column=0, sticky=tk.W)
        row = row + 1

        # Lost Worlds
        self.lost_worlds_checkbox = tk.Checkbutton(
            frame, text="Lost Worlds (l)",
            variable=self.flag_dict[GameFlags.LOST_WORLDS],
            command=self.verify_settings
        )
        self. lost_worlds_checkbox.grid(
            row=row, column=0, sticky=tk.W, columnspan=2
        )

        CreateToolTip(
            self.lost_worlds_checkbox,
            'An alternate game mode where you start with access to '
            'Prehistory, the Dark Ages, and the Future. Find the clone and '
            'c.trigger to climb Death Peak and beat the Black Omen, or find '
            'the Dreamstone and Ruby Knife to make your way to Lavos '
            'through the Ocean Palace. 600AD and 1000AD are unavailable '
            'until the very end of the game.'
        )

        # Boss Rando
        self.boss_rando_checkbox = tk.Checkbutton(
            frame,
            text="Randomize bosses (ro)",
            variable=self.flag_dict[GameFlags.BOSS_RANDO],
            command=self.verify_settings
        )
        self.boss_rando_checkbox.grid(
            row=row, column=2, sticky=tk.W, columnspan=2
        )
        CreateToolTip(
            self.boss_rando_checkbox,
            'Various dungeon bosses are shuffled and scaled.  Does not '
            'affect end game bosses.')
        row = row + 1

        # Boss Scaling
        self.boss_scaling_checkbox = tk.Checkbutton(
            frame,
            text="Boss scaling (b)",
            variable=self.flag_dict[GameFlags.BOSS_SCALE],
            command=self.verify_settings
        )
        self.boss_scaling_checkbox.grid(
            row=row, column=0, sticky=tk.W, columnspan=2
        )
        CreateToolTip(
            self.boss_scaling_checkbox,
            'Bosses are scaled in difficulty based on how many key items '
            'they block.  Early bosses are unaffected.'
        )

        # Zeal 2 End
        self.zeal_end_checkbox = tk.Checkbutton(
            frame,
            text="Zeal 2 as last boss (z)",
            variable=self.flag_dict[GameFlags.ZEAL_END],
            command=self.verify_settings
        )
        self.zeal_end_checkbox.grid(
            row=row, column=2, sticky=tk.W, columnspan=2
        )
        CreateToolTip(
            self.zeal_end_checkbox,
            'The game ends after defeating Zeal 2 when going through the '
            'Black Omen.  Lavos is still required for the Ocean Palace route.'
        )
        row = row + 1

        # Fast Pendant
        self.fast_pendant_checkbox = tk.Checkbutton(
            frame,
            text="Early Pendant Charge (p)",
            variable=self.flag_dict[GameFlags.FAST_PENDANT],
            command=self.verify_settings
        )
        self.fast_pendant_checkbox.grid(
            row=row, column=0, sticky=tk.W, columnspan=2
        )
        CreateToolTip(
            self.fast_pendant_checkbox,
            'The pendant becomes charged immediately upon access to the '
            'Future, granting access to sealed doors and chests.'
        )

        # Locked Chars
        self.locked_chars_checkbox = tk.Checkbutton(
            frame, text="Locked characters (c)",
            variable=self.flag_dict[GameFlags.LOCKED_CHARS],
            command=self.verify_settings
        )
        self.locked_chars_checkbox.grid(
            row=row, column=2, sticky=tk.W, columnspan=2
        )
        CreateToolTip(
            self.locked_chars_checkbox,
            'The Dreamstone is required to access the character in the '
            'Dactyl Nest and power must be turned on at the Factory before '
            'the Proto Dome character can be obtained.'
        )
        row = row + 1

        self.unlocked_magic_checkbox = tk.Checkbutton(
            frame,
            text="Unlocked Magic (m)",
            variable=self.flag_dict[GameFlags.UNLOCKED_MAGIC],
            command=self.verify_settings
        )
        self.unlocked_magic_checkbox.grid(
            row=row, column=0, sticky=tk.W, columnspan=2
        )
        CreateToolTip(
            self.unlocked_magic_checkbox,
            'Magic is unlocked at the start of the game, no trip to Spekkio '
            'required.'
        )

        # Tab Treasures
        self.tab_treasure_checkbox = tk.Checkbutton(
            frame,
            text="Make all treasures tabs (tb)",
            variable=self.flag_dict[GameFlags.TAB_TREASURES],
            command=self.verify_settings
        )
        self.tab_treasure_checkbox.grid(
            row=row, column=2, sticky=tk.W, columnspan=3
        )
        CreateToolTip(
            self.tab_treasure_checkbox,
            'All treasures chest contents are replaced with power, magic, '
            'or speed tabs.'
        )
        row = row + 1

        # Chronosanity
        self.chronosanity_checkbox = tk.Checkbutton(
            frame, text="Chronosanity (cr)",
            variable=self.flag_dict[GameFlags.CHRONOSANITY],
            command=self.verify_settings,
        )
        self.chronosanity_checkbox.grid(
            row=row, sticky=tk.W, columnspan=2
        )
        CreateToolTip(
            self.chronosanity_checkbox,
            'Key items can now show up in most treasure chests in addition '
            'to their normal locations.'
        )

        # Duplicate Characters
        self.dup_char_checkbox = tk.Checkbutton(
            frame,
            text="Duplicate Characters (dc)",
            variable=self.flag_dict[GameFlags.DUPLICATE_CHARS],
            command=self.verify_settings
        )
        self.dup_char_checkbox.grid(
            row=row, column=2, sticky=tk.W, columnspan=2
        )
        CreateToolTip(
            self.dup_char_checkbox,
            'Characters can now show up more than once. Quests are '
            'activated and turned in based on the default NAME of the '
            'character.')
        row = row + 1

        # Shop Prices dropdown
        shop_price_values = RandoGUI.shop_price_dict.values()
        label = tk.Label(frame, text="Shop Prices:")
        label.grid(row=row, column=0, sticky=tk.W)

        self.shop_price_dropdown = tk.OptionMenu(
            frame,
            self.shop_prices,
            *shop_price_values
        )
        self.shop_price_dropdown.grid(
            row=row, column=1, sticky=tk.W, columnspan=2
        )

        CreateToolTip(
            self.shop_price_dropdown,
            "Determines shop prices:\n"
            "Normal - Standard randomizer shop prices\n"
            "Free - Everything costs 1G (minimum allowed by the game)\n"
            "Mostly Random - Random prices except for some key consumables\n"
            "Fully Random - Random price for every item"
        )

        row += 1

        tech_order_values = RandoGUI.tech_order_dict.values()
        label = tk.Label(frame, text="Tech Randomization:")
        label.grid(row=row, column=0, sticky=tk.W)

        self.tech_order_dropdown = tk.OptionMenu(
            frame, self.tech_order, *tech_order_values)
        self.tech_order_dropdown.grid(
            row=row, column=1, sticky=tk.W, columnspan=2
        )

        CreateToolTip(
            self.tech_order_dropdown,
            "Determines the order in which techs are learned:\n"
            "Normal - Vanilla tech order.\n"
            "Balanced Random - Random tech order, but stronger techs are "
            "more likely to show up later.\n"
            "Fully Random - Tech order is fully randomized."
        )
        row = row + 1

        return frame

    def get_generate_options(self):
        frame = tk.Frame(
            self.general_page,
            borderwidth=1, highlightbackground="black",
            highlightthickness=1
        )
        frame.columnconfigure(4, weight=1)
        row = 0

        # Let the user choose a seed (optional parameter)
        label = tk.Label(frame, text="Seed(optional):")
        label.grid(row=row, column=0, sticky=tk.W+tk.E)

        tk.Entry(
            frame, textvariable=self.seed
        ).grid(row=row, column=1, columnspan=3)
        CreateToolTip(
            label,
            'Enter a seed for the randomizer.  Games generated with the '
            'same seed and flags will be identical every time.  This field '
            'is optional and a seed will be randomly selected if none is '
            'provided.'
        )
        row = row + 1

        # Let the user select the base ROM to copy and patch
        label = tk.Label(frame, text="Input ROM:")
        label.grid(row=row, column=0, sticky=tk.W+tk.E)
        tk.Entry(
            frame, textvariable=self.input_file
        ).grid(row=row, column=1, columnspan=3)
        tk.Button(
            frame,
            text="Browse",
            command=lambda: self.input_file.set(askopenfilename())
        ).grid(row=row, column=4, sticky=tk.W)
        CreateToolTip(
            label,
            'The vanilla Chrono Trigger ROM used to generate a randomized '
            'game.'
        )
        row = row + 1

        # Let the user select the output directory
        label = tk.Label(frame, text="Output Folder:")
        label.grid(row=row, column=0, sticky=tk.W+tk.E)

        tk.Entry(
            frame, textvariable=self.output_file
        ).grid(row=row, column=1, columnspan=3)

        tk.Button(
            frame, text="Browse",
            command=lambda: self.output_file.set(askdirectory())
        ).grid(row=row, column=4, sticky=tk.W)
        CreateToolTip(
            label,
            'The output location of the randomized ROM.  Defaults to the '
            'input ROM location if left blank.'
        )
        row = row + 1

        # Add a progress bar to the GUI for ROM generation
        self.progressBar = ttk.Progressbar(
            frame, orient='horizontal', mode='indeterminate'
        )
        self.progressBar.grid(
            row=row, column=0, columnspan=5, sticky=tk.E+tk.W
        )
        row = row + 1

        tk.Button(
            frame, text="Generate", command=self.generate_handler
        ).grid(row=row, column=2, sticky=tk.W, columnspan=2)

        return frame

    def randomize(self):
        # Check for bad input.  For now it's only from dc settings page
        if self.flag_dict[GameFlags.DUPLICATE_CHARS].get() == 1 \
           and not self.dc_settings_valid():
            messagebox.showerror(
                'DC Settings Error',
                'Each character must have at least one choice selected.'
            )
            self.notebook.select(self.dc_page)

    def generate_handler(self):
        if self.gen_thread is None or not self.gen_thread.is_alive():
            self.gen_thread = threading.Thread(target=self.randomize)
            self.progressBar.start(50)
            self.gen_thread.start()

    def get_general_page(self):
        self.general_page = ttk.Frame(self.notebook)
        self.get_presets_frame().pack(fill='both', expand=True)
        self.get_difficulty_options().pack(fill='both', expand=True)
        self.get_general_options().pack(fill='both', expand=True)
        self.get_general_flags_frame().pack(fill='both', expand=True)
        self.get_generate_options().pack(fill='both', expand=True)

    def get_tabs_page(self):
        self.tabs_page = ttk.Frame(self.notebook)

        frame = tk.Frame(
            self.tabs_page, borderwidth=1,
            highlightbackground="black",
            highlightthickness=1
        )

        tk.Label(
            frame, text='Tab Magnitudes:'
        ).pack(side='left', fill='both', expand=True)

        self.get_tab_magnigtude_frame(
            frame,
            'Power',
            self.power_tab_min,
            self.power_tab_max
        ).pack(fill=tk.X)

        self.get_tab_magnigtude_frame(
            frame,
            'Magic',
            self.magic_tab_min,
            self.magic_tab_max
        ).pack(fill=tk.X)

        self.get_tab_magnigtude_frame(
            frame,
            'Magic',
            self.speed_tab_min,
            self.speed_tab_max
        ).pack(fill=tk.X)

        frame.pack(fill=tk.X)

        frame = tk.Frame(
            self.tabs_page
        )

        tk.Label(
            frame, text='Tab Randomization Scheme: '
        ).grid(row=0, column=0, columnspan=3)

        tab_rando_options = TabRandoScheme.str_dict().values()
        tab_scheme_dropdown = ttk.OptionMenu(
            frame,
            self.tab_rando_scheme,
            None,
            *tab_rando_options,
            command=lambda x: self.verify_settings()
        )
        tab_scheme_dropdown.grid(row=0, column=3)

        tk.Label(frame, text='p = ').grid(row=1, column=0)

        self.tab_prob_scale = tk.Scale(
            frame,
            from_=0,
            to=1,
            length=300,
            resolution=0.01,
            orient=tk.HORIZONTAL,
            variable=self.tab_success_chance
        )

        self.tab_prob_scale.grid(row=1, column=1, columnspan=3)

        frame.pack()

        return self.tabs_page

    def get_tab_magnigtude_frame(self, parent,
                                 tab_type: str,
                                 min_val: tk.IntVar,
                                 max_val: tk.IntVar):

        def set_high_given_low(low: int, high: tk.IntVar):
            a = low
            b = high.get()

            if a > b:
                high.set(a)

        def set_low_given_high(low: tk.IntVar, high: int):
            a = low.get()
            b = high

            if a > b:
                low.set(b)

        frame = tk.Frame(parent)

        row = 0

        tab_choices = [x for x in range(1, 10)]

        label = tk.Label(
            frame,
            text=tab_type+' Min:'
        )
        label.grid(row=row, column=0, sticky=tk.E)

        min_dropdown = ttk.OptionMenu(
            frame,
            min_val,
            1,  # Have to set a default for integer options
            *tab_choices,
            command=lambda x: set_high_given_low(x, max_val)
        )
        min_dropdown.grid(row=row, column=1)

        label = tk.Label(
            frame,
            text=tab_type+' Max:'
        )
        label.grid(row=row, column=3, sticky=tk.E)

        max_dropdown = ttk.OptionMenu(
            frame,
            max_val,
            1,  # Have to set a default for integer options
            *tab_choices,
            command=lambda x: set_low_given_high(min_val, x)
        )
        max_dropdown.grid(row=row, column=4)

        return frame

    def get_dc_page(self):
        frame = ttk.Frame(self.notebook)

        instruction_frame = tk.Frame(frame)

        tk.Label(
            instruction_frame,
            text='Indicate allowed character assignments below:'
        ).pack(fill=tk.X, side=tk.LEFT)

        instruction_frame.pack(fill=tk.X)

        self.get_dc_set_char_choices(frame).pack(fill=tk.X)
        self.get_dc_set_autofill(frame).pack(fill=tk.X)
        self.get_dc_set_additional_options(frame).pack(fill=tk.X)

        return frame


if __name__ == '__main__':

    gui = RandoGUI()
    gui.main_window.mainloop()
