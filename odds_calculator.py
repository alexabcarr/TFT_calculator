import tkinter as tk
from PIL import Image, ImageTk
import json
import os

# Find the root path to the files
dirname = os.path.dirname(os.path.abspath(__file__))

# Tracks the length of the longest champion name for each tier for formatting purposes
max_len_per_cost = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}

# The next two values are not available in the Riot API but are publicly known so they were manually entered

# The base amount of each tier of champion in the store
base_amounts = {1: 30, 2: 25, 3: 18, 4: 10, 5: 9}

# The rate of rolling each tier of champion (for each shop slot) at the given level
# There is no shop for level 1, so there are no rates
# tier_rates_per_level[3] = {1: .75, 2: .25, 3: .0, 4: .0, 5: .0} means that at level 3,
#    there is a 75% chance to roll tier 1 champions and a 25% chance for tier 2 champions in each shop slot
# 'All ones', 'All twos', 'All threes', 'All fours', 'All fives', and 'The count' are all charms that guarantee the shop to have certain odds regardless of level
tier_rates_per_level = {2: {1: 1, 2: .0, 3: .0, 4: .0, 5: .0}, 3: {1: .75, 2: .25, 3: .0, 4: .0, 5: .0}, 4: {1: .55, 2: .30, 3: .15, 4: .0, 5: .0},
                        5: {1: .45, 2: .33, 3: .20, 4: .02, 5: .0}, 6: {1: .30, 2: .40, 3: .25, 4: .05, 5: .0}, 7: {1: .19, 2: .30, 3: .40, 4: .10, 5: .01},
                        8: {1: .18, 2: .27, 3: .32, 4: .20, 5: .03}, 9: {1: .15, 2: .20, 3: .25, 4: .30, 5: .10}, 10: {1: .05, 2: .10, 3: .20, 4: .40, 5: .25},
                        11: {1: .01, 2: .10, 3: .12, 4: .50, 5: .35}, "All ones": {1: 1, 2: 0, 3: 0, 4: 0, 5: 0}, "All twos": {1: 0, 2: 1, 3: 0, 4: 0, 5: 0}, 
                        "All threes": {1: 0, 2: 0, 3: 1, 4: 0, 5: 0}, "All fours": {1: 0, 2: 0, 3: 0, 4: 1, 5: 0}, "All fives": {1: 0, 2: 0, 3: 0, 4: 0, 5: 1},
                        "The count": {1: .2, 2: .2, 3: .2, 4: .2, 5: .2}}

class InventoryApp:
    def __init__(self, root):
        """
        Initializes the application
        """
        self.root = root
        self.root.title("Shop Tracker")
    
        # The path to the file containing champion data
        dataloc = os.path.join(dirname, "/TFT_odds_calculator/RiotAssets/14.15.1/data/en_US/tft-champion.json")

        with open(dataloc) as f:
            data = json.load(f)

        self.temp_items = {}

        # Look through the 'data' section of the file
        for datum in data["data"]:
            # Find the champions from this set
            if datum[25:33] == "TFTSet12":

                # Pull out each champion's data
                champ_info = data["data"][datum]

                # The image folder header for splash arts

                img_path = os.path.join(dirname, "/TFT_odds_calculator/RiotAssets/14.15.1/img/tft-champion/")

                # Locate the sprite for this champion and crop it to the intended size
                img_data = champ_info['image']
                full_img = Image.open(img_path + img_data['full'])

                champ_tier = champ_info['tier']
                champ_name = champ_info['name']

                # Check the champion's name length and compare it to the longest name seen yet for this tier
                max_len_per_cost[champ_tier] = max(max_len_per_cost[champ_tier], len(champ_name))

                # Add the champion data to the dictionary of all champions
                self.temp_items[champ_name] = {"image": full_img, "quantity": base_amounts[champ_info['tier']], "tier": champ_info['tier']}
        
        # Sort the dictionary alphabetically
        champ_names = list(self.temp_items.keys())
        champ_names.sort()
        self.items = {i: self.temp_items[i] for i in champ_names}

        self.create_widgets()

    def create_widgets(self):
        """
        Creates all the interactable widgets in the GUI, such as champions and their buttons, target drop-downs, and the information boxes
        """

        # Track the number of champions encountered for each tier
        tier_rows = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        
        tier_colors = {1: "gray", 2: "green", 3: "blue", 4: "purple", 5: "gold"}

        # Initialize the frame for each champion
        for champ_name, champ_info in self.items.items():
            # Get the champion's location and update the number of champions for that tier
            champ_col = champ_info['tier']
            champ_row = tier_rows[champ_col]
            tier_rows[champ_col] = tier_rows[champ_col] + 1

            # Initialize the frame for each champion using their rarity color
            frame = tk.Frame(self.root, highlightbackground=tier_colors[champ_col], highlightthickness=2)

            # Set the location based on the champion's tier and the number of champions for that tier
            frame.grid(row=champ_row, column=champ_col, padx=5, pady=5)

            # Load and display the image
            img = champ_info["image"].resize((150, 75))
            img = ImageTk.PhotoImage(img)

            img_label = tk.Label(frame, image=img)
            img_label.image = img
            img_label.grid(row=champ_row, column=champ_col, rowspan=3, sticky="w")

            # Champion name
            champion_buffer = (max_len_per_cost[champ_col] - len(champ_name))
            formatted_name = champ_name.center(len(champ_name) + champion_buffer)
            name_label = tk.Label(frame, text=formatted_name, font= "TkFixedFont")
            name_label.grid(row=champ_row, column=champ_col+1)

            # Quantity display          
            quantity_label = tk.Label(frame, text="")
            quantity_label.grid(row=champ_row, column=champ_col+2, pady=5)
            quantity_label.configure(text=str(champ_info["quantity"]) + "/" + str(base_amounts[champ_info['tier']]))

            # +1 button
            add_button = tk.Button(frame, text="+1", command=lambda name=champ_name: self.change_quantity(name, 1))
            add_button.grid(row=champ_row+2, column=champ_col+3, padx=5, sticky='e')

            # +3 button
            add_3_button = tk.Button(frame, text="+3", command=lambda name=champ_name: self.change_quantity(name, 3))
            add_3_button.grid(row=champ_row+2, column=champ_col+4, padx=5, sticky='e')
            
            # -1 button
            remove_button = tk.Button(frame, text="-1", command=lambda name=champ_name: self.change_quantity(name, -1))
            remove_button.grid(row=champ_row+2, column=champ_col+2, padx=5, sticky='w')

            # -3 button
            remove_3_button = tk.Button(frame, text="-3", command=lambda name=champ_name: self.change_quantity(name, -3))
            remove_3_button.grid(row=champ_row+2, column=champ_col+1, padx=5, sticky='e')

            # Text box for the user to manually enter the number left
            cur_quantity = tk.StringVar()
            entry = tk.Entry(frame, width=3, justify="center", textvariable=cur_quantity)
            entry.insert(0, str(champ_info["quantity"]))
            entry.grid(row=champ_row, column=champ_col+3, padx=5, sticky='w')

            # Button to update the number left based on the text box
            update_button = tk.Button(frame, text="✓", command= lambda name=champ_name: self.update_quantity(name, "update"))
            update_button.grid(row=champ_row, column=champ_col+4, padx=5)

            # Button to reset the number left to the default
            reset_button = tk.Button(frame, text="⟳", command= lambda name=champ_name: self.update_quantity(name, base_amounts[champ_col]))
            reset_button.grid(row=champ_row+2, column=champ_col+1, padx=5, sticky='w')

            # Button to zero out the number of this champion left
            # Mostly useful for testing so it has been commented out
            #zero_button = tk.Button(frame, text="✖", command= lambda name=champ_name: self.update_quantity(name, 0))
            #zero_button.grid(row=champ_row+2, column=champ_col+1, padx=5)

            # Store configurable widgets in champ info
            champ_info["entry"] = entry
            champ_info["quantity_label"] = quantity_label
            champ_info["cur_quantity"] = cur_quantity
            
        # Non-champion elements

        # Create a drop-down menu for all champions
        selected_champ = tk.StringVar()
        selected_champ.set("N/A")
        champ_selector = tk.OptionMenu(self.root, selected_champ, *self.items)
        champ_selector.grid(row=8, column=5, padx=40, sticky='w')

        # Create a drop-down menu to select your level
        levels = [i for i in tier_rates_per_level.keys()]
        current_level = tk.StringVar()
        current_level.set("N/A")
        level_selector = tk.OptionMenu(self.root, current_level, *levels)
        level_selector.grid(row=8, column=5, padx=40, sticky='e')

        # Enclose the flavor text in a box
        frame = tk.Frame(self.root, highlightbackground="black", highlightthickness=2)
        frame.grid(row=9, column=5, padx= 5, pady= 5)

        stats_label = tk.Label(frame, text="")
        stats_label.grid(row=10, column=5, pady=5)

        # A button to calculate and update the odds
        calculate_button = tk.Button(frame, text="Calculate odds", command= lambda: self.update_odds())
        calculate_button.grid(row=9, column=5, padx=5)
        
        # Initialize a new instance variable to access the odds variables as necessary
        self.rolling_params = {}
        self.rolling_params["level"] = current_level
        self.rolling_params["champ"] = selected_champ
        self.rolling_params["odds"] = stats_label
        stats_label.configure(text="Select a champion and your current level, then click 'Calculate odds!'")

        # Highlight red so the user is hopefully cautious
        frame = tk.Frame(self.root, highlightbackground="red", highlightthickness=4)
        frame.grid(row=12, column=5)
        # Button to reset the board to the default state
        wipe_button = tk.Button(frame, text="Wipe the whole board", command= lambda: self.wipe_board())
        wipe_button.grid(row=12, column=5, padx=5)


    def change_quantity(self, champ_name, amount):
        """
        Changes the quantity of the target champion BY the target amount

        Params:
            champ_name (str): The name of the target champion
            amount (int): The number to increment or decrement the target champion's quantity by
        """
        champ_info = self.items[champ_name]

        current_quantity = champ_info["quantity"]

        # Ensuring that the new value is between the required 0<quantity<num_in_tier
        new_quantity = max(0, int(current_quantity) + amount)
        new_quantity = min(base_amounts[champ_info["tier"]], new_quantity)

        # Update the variable with the numeric quantity
        champ_info["quantity"] = new_quantity

        # Update the board elements
        self.update_board(champ_name) 

    def update_quantity(self, champ_name, new_quantity):
        """
        Changes the quantity of the target champion TO the target amount

        Params:
            champ_name (str): The name of the target champion
            amount (int): The number to increment or decrement the target champion's quantity to
        """
        # The highest number of this champion that can be in the pool
        num_in_tier = base_amounts[self.items[champ_name]["tier"]]

        champ_info = self.items[champ_name]

        try:
            # Try to convert the new value to an int
            new_quantity = int(new_quantity)

        # When we pass the update flag 
        except ValueError:
            try:
                # Try to parse the user's input field
                new_quantity = int(champ_info["cur_quantity"].get())
            except:
                # If the user provides invalid input, return the value to the default
                new_quantity = num_in_tier

        # Ensuring that the new value is between the required 0<quantity<num_in_tier
        new_quantity = max(0, new_quantity)
        new_quantity = min(base_amounts[champ_info["tier"]], new_quantity)

        # Update the quantity variable with the numeric quantity
        champ_info["quantity"] = new_quantity

        # Update the board elements
        self.update_board(champ_name)

    
    def wipe_board(self):
        """
        Resets the board to the default state for all champions.
        """

        champions = self.items

        for champ in champions:
            # Find the base number of this champion in the store
            default_number = base_amounts[champions[champ]["tier"]]

            # Update the quantity with the default
            self.update_quantity(champ, default_number)
    
    def update_board(self, champ_name):
        """
        Updates the given board element corresponding with champ_name
        """

        champ_info = self.items[champ_name]
        quantity = champ_info["quantity"]

        # The highest number of this champion that can be in the pool
        num_in_tier = base_amounts[self.items[champ_name]["tier"]]

        # Update the label to say current/max
        champ_info["quantity_label"].configure(text= str(quantity)+ "/" + str(num_in_tier))

        # Update the user-interactable field with the current value
        champ_info["entry"].delete(0, tk.END)
        champ_info["entry"].insert(0, str(champ_info["quantity"]))    

    def recursive_odds(self, target_champs_left, same_tier_champs_left, level_odds, recursion):
        """
        Determines the expected number of the target champion in each shop of 5 champions.
        Helper function for calculate_odds()

        Params:
            target_champs_left (int): The number of the target champion remaining in the pool
            same_tier_champs_left (int): The total number of each champion of the same tier as the target champion
            level_odds (float): The percentage (in decimal form) odds of rolling any champion of the target champion's tier for the current level
            recursion (int): The recursion level of the function, up to 5

        Returns:
            (float): The expected number of the target champion per shop
        """
        # Terminate once we've checked all 5 shop slots
        if recursion >= 5:
            return 0
        # Calculate the expected value for the current shop slot using the given probabilities
        try:
            ev = (target_champs_left / same_tier_champs_left) * level_odds
        # Catching division by zero errors
        except:
            ev = 0

        # Calculate the odds for the next slot, if we hit 
        pos_ev = min(1, ev) * self.recursive_odds(target_champs_left-1, same_tier_champs_left-1, level_odds, recursion+1)
        # Calculate the odds for the next slot, if we don't hit
        neg_ev = (1 - min(1, ev)) * self.recursive_odds(target_champs_left, same_tier_champs_left-1, level_odds, recursion+1)

        # Return the sum of the ev of the current slot and the next slot
        return ev + pos_ev + neg_ev

    def calculate_odds(self, champ, level):
        """
        Determines the expected number of the target champion in each shop of 5 champions.

        Params:
            champ (str): The target champion
            level (int): The user's current level

        Returns:
            (float): The expected number of the target champion per shop
        """
        # Determine the champion's tier
        champ_tier = self.items[champ]['tier']

        try:
            level = int(level)
        except:
            pass

        # Determine the chances of rolling any unit of the target's tier
        level_odds = tier_rates_per_level[level][champ_tier]

        # Find the number of the target champions left
        target_champs_left = self.items[champ]["quantity"]

        same_tier_champs_left = 0
        for champion in self.items:
            # For each champion, determine if it is of the target tier
            if self.items[champion]['tier'] == champ_tier:
                # If it is, add these champions to the pool
                same_tier_champs_left += int(self.items[champion]['quantity'])
        
        expected_value = self.recursive_odds(target_champs_left, same_tier_champs_left, level_odds, 0)
        return expected_value
    
    def update_odds(self):
        """
        Updates the odds of rolling a champion in the GUI. 
        Depends on the current_level and selected_champ variables and their associated buttons.
        """

        # Take the values from the level and champ buttons
        level = self.rolling_params["level"].get()
        champ = self.rolling_params["champ"].get()

        # Calculate the EV per shop and format it into a readable string
        ev = self.calculate_odds(champ, level)
        ev_string = "Your expected number of {0}s per shop at level {1} is roughly {2:.3f}.\n".format(champ, level, ev)

        # Gold expected is 2* the inverse of ev, since we spend 2 gold to reroll the shop
        try:
            gold = 2/ev
        except:
            gold = 99
        # Adding another formatted string for the expected gold spent per target champion
        gold_string = "This means you can expect to spend about {0:.2f} gold rolling to see each {1}.".format(max(2, gold), champ)

        # An optional flavor_string if the gold or ev are outside of the expecetd values
        flavor_string = ""
        if gold > 30:
            flavor_string = "\nThis is higher than average. You might want to consider searching for a different unit/double-checking boards."
        if ev > 2: 
            flavor_string = "\nYou're expecting more than 2 {0}s per roll, which is rather high. Are your boards scouted properly?".format(champ)
        
        # Update the flavor sentence by concatenating the relevant strings
        self.rolling_params["odds"].configure(text=ev_string + gold_string + flavor_string)
    
if __name__ == "__main__":
    root = tk.Tk()
    app = InventoryApp(root)
    root.mainloop()
