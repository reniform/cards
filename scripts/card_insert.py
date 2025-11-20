import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "cards.db")


def get_int_input(prompt):
    """Safely gets an integer from user input, allowing for empty values."""
    while True:
        try:
            value = input(prompt)
            if value == '':
                return None  # Allow empty input for optional fields
            return int(value)
        except ValueError:
            print("Invalid input. Please enter a whole number.")

def get_float_input(prompt):
    """Safely gets a float from user input, allowing for empty values."""
    while True:
        try:
            value = input(prompt)
            if value == '':
                return None
            return float(value)
        except ValueError:
            print("Invalid input. Please enter a number.")


def add_monster_evolutions(cursor, card_id):
    """Interactively adds one or more evolution sources for a monster."""
    print("--- Adding Evolution Sources ---")
    while True:
        if input("Add an evolution source? (y/n): ").lower() != 'y':
            break
        evolves_from = input("Enter name of monster it evolves from: ")
        cursor.execute("INSERT INTO monster_evolutions (card_id, evolves_from_name) VALUES (?, ?)", (card_id, evolves_from))
        print(f"Added evolution source: {evolves_from}")

def add_monster_types(cursor, card_id):
    """Interactively adds one or more mana types for a monster."""
    print("--- Adding Monster Types ---")
    types_added = False
    while True:
        prompt = "Add a mana type? (y/n): " if types_added else "Add a mana type? (y/n, defaults to COLORLESS if none): "
        if input(prompt).lower() != 'y':
            break
        mana_type = input("Enter mana type (e.g., FIRE, WATER): ").upper()
        cursor.execute("INSERT INTO monster_types (card_id, mana_type) VALUES (?, ?)", (card_id, mana_type))
        print(f"Added type: {mana_type}")
        types_added = True

    if not types_added:
        cursor.execute("INSERT INTO monster_types (card_id, mana_type) VALUES (?, ?)", (card_id, "COLORLESS"))
        print("No type added. Defaulting to COLORLESS.")

def add_monster_weaknesses(cursor, card_id):
    """Interactively adds one or more weaknesses for a monster."""
    print("--- Adding Weaknesses ---")
    while True:
        if input("Add a weakness? (y/n): ").lower() != 'y':
            break
        mana_type = input("Enter weakness mana type: ").upper()
        modifier = input("Enter weakness modifier (e.g., x2): ")
        cursor.execute("INSERT INTO monster_weaknesses (card_id, mana_type, modifier) VALUES (?, ?, ?)", (card_id, mana_type, modifier))
        print(f"Added weakness: {mana_type} ({modifier})")

def add_monster_resistances(cursor, card_id):
    """Interactively adds one or more resistances for a monster."""
    print("--- Adding Resistances ---")
    while True:
        if input("Add a resistance? (y/n): ").lower() != 'y':
            break
        mana_type = input("Enter resistance mana type: ").upper()
        modifier = input("Enter resistance modifier (e.g., -30): ")
        cursor.execute("INSERT INTO monster_resistances (card_id, mana_type, modifier) VALUES (?, ?, ?)", (card_id, mana_type, modifier))
        print(f"Added resistance: {mana_type} ({modifier})")


def add_monster_data(cursor, card_id):
    """Prompts for and inserts monster-specific data into the 'monsters' table."""
    print("--- Adding Monster Details ---")
    stage = input("Enter stage (e.g., BASIC, STAGEONE): ").upper()
    if stage != 'BASIC':
        add_monster_evolutions(cursor, card_id)

    health = get_int_input("Enter health points: ")
    retreat_cost = get_int_input("Enter retreat cost (number): ")

    cursor.execute("INSERT INTO monsters (card_id, stage, health, retreat_cost) VALUES (?, ?, ?, ?)",
                   (card_id, stage, health, retreat_cost))
    print("Successfully inserted monster details.")

    # Add named abilities (e.g., Pokémon Powers) before types/attacks
    add_monster_abilities(cursor, card_id)

    add_monster_types(cursor, card_id)
    add_monster_weaknesses(cursor, card_id)
    add_monster_resistances(cursor, card_id)

    # After adding monster data, ask to add attacks.
    add_attacks(cursor, card_id)


def add_monster_abilities(cursor, card_id):
    """Interactively adds one or more named abilities to a monster card."""
    print("--- Adding Monster Abilities ---")
    while True:
        if input("Add a named ability (e.g., Pokémon Power)? (y/n): ").lower() != 'y':
            break

        name = input("Enter ability name: ")
        ability_type = input("Enter ability type (e.g., Pokémon Power, Poké-Body): ")

        cursor.execute("""
            INSERT INTO monster_abilities (card_id, name, type)
            VALUES (?, ?, ?)
        """, (card_id, name, ability_type))
        ability_id = cursor.lastrowid
        print(f"Successfully added ability '{name}' with ID: {ability_id}")

        # Now add the specific effects for this ability
        add_effects(cursor, card_id, ability_id=ability_id)

def add_attacks(cursor, card_id):
    """Interactively adds one or more attacks to a monster card."""
    print("--- Adding Attacks ---")
    while True:
        if input("Add an attack to this monster? (y/n): ").lower() != 'y':
            break

        title = input("Enter attack title: ")
        damage = input("Enter attack damage (e.g., 30, 10+, 20x): ")
        description = input("Enter attack description: ")

        cursor.execute("""
            INSERT INTO attacks (card_id, title, damage, description)
            VALUES (?, ?, ?, ?)
        """, (card_id, title, damage, description))
        attack_id = cursor.lastrowid
        print(f"Successfully added attack '{title}' with ID: {attack_id}")

        # Now add costs and effects for this specific attack
        add_attack_costs(cursor, attack_id)
        add_effects(cursor, card_id, attack_id=attack_id, ability_id=None)


def add_attack_costs(cursor, attack_id):
    """Interactively adds one or more mana costs to an attack."""
    print("--- Adding Attack Costs ---")
    while True:
        if input("Add a mana cost to this attack? (y/n): ").lower() != 'y':
            break
        mana_type = input("Enter mana type for cost (e.g., FIRE, COLORLESS): ").upper()
        quantity = get_int_input("Enter quantity for this mana type: ")
        cursor.execute("""
            INSERT INTO attack_costs (attack_id, mana_type, quantity)
            VALUES (?, ?, ?)
        """, (attack_id, mana_type, quantity))
        print(f"Added cost: {quantity} {mana_type}")


def add_effects(cursor, card_id, attack_id=None, ability_id=None):
    """Interactively adds one or more effects to a card or an attack."""
    print("--- Adding Effects ---")
    if attack_id:
        prompt = "Add an effect to this attack? (y/n): "
    elif ability_id:
        prompt = "Add an effect for this ability? (y/n): "
    else: # Card-level effect for Utility/Mana cards
        prompt = "Add a card-level effect? (y/n): "

    while True:
        if input(prompt).lower() != 'y':
            break
        effect_name = input("Enter effect name (e.g., HEAL, DRAW): ").upper()
        target = input("Enter target (e.g., SELF, YOUR_POKEMON_CHOICE): ").upper()
        value = input("Enter effect value (e.g., 30, 7, or leave blank): ")
        condition = input("Enter condition (e.g., ALWAYS, ON_COIN_FLIP_HEADS, or leave blank): ").upper() or "ALWAYS"
        execution_order = get_int_input("Enter execution order (e.g., 1, 2, or leave blank): ")
        cursor.execute("""
            INSERT INTO effects (source_card_id, source_attack_id, source_ability_id, effect_name, target, value, condition, execution_order)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (card_id, attack_id, ability_id, effect_name, target, value, condition, execution_order))
        print(f"Successfully added effect '{effect_name}'.")


def add_mana_data(cursor, card_id):
    """Prompts for and inserts mana-specific data into the 'mana_cards' table."""
    print("--- Adding Mana Details ---")
    mana_type = input("Enter mana type (e.g., FIRE, WATER, RAINBOW): ").upper()

    cursor.execute("""
        INSERT INTO mana_cards (card_id, mana_type)
        VALUES (?, ?)
    """, (card_id, mana_type))
    print("Successfully inserted mana details.")

def add_pokedex_data(cursor, card_id):
    """Prompts for and inserts Pokedex data for a monster card."""
    print("--- Adding Pokedex Details ---")
    level = get_int_input("Enter level: ")
    dex_number = get_int_input("Enter Pokedex number: ")
    species = input("Enter species (e.g., Mouse Pokémon): ")
    height_ft_in = input("Enter height (ft'in\"): ")
    height_m = get_float_input("Enter height (m): ")
    weight_lbs = get_float_input("Enter weight (lbs): ")
    weight_kg = get_float_input("Enter weight (kg): ")
    dex_entry = input("Enter Pokedex entry text: ")

    cursor.execute("""
        INSERT INTO pokedex_entries (card_id, level, dex_number, species, height_ft_in, height_m, weight_lbs, weight_kg, dex_entry)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (card_id, level, dex_number, species, height_ft_in, height_m, weight_lbs, weight_kg, dex_entry))
    print("Successfully inserted Pokedex details.")

def add_card_prints(cursor, card_id):
    """Interactively adds one or more prints for a conceptual card."""
    print("--- Adding Card Prints ---")
    last_illustrator = None
    last_rarity = None

    while True:
        if input("Add a print for this card? (y/n): ").lower() != 'y':
            break

        print_set_code = input("Enter this print's set code (e.g., BS, LC): ").upper()
        set_number = input("Enter this print's set number (e.g., 58/102): ")

        # Handle illustrator input with repeat option
        illustrator_prompt = "Enter this print's illustrator: "
        if last_illustrator:
            illustrator_prompt = f"Enter illustrator (or 'r' to repeat '{last_illustrator}'): "
        illustrator_input = input(illustrator_prompt)
        illustrator = last_illustrator if illustrator_input.lower() == 'r' and last_illustrator else illustrator_input

        # Handle rarity input with repeat option
        rarity_prompt = "Enter this print's rarity (e.g., Common, Rare Holo): "
        if last_rarity:
            rarity_prompt = f"Enter rarity (or 'r' to repeat '{last_rarity}'): "
        rarity_input = input(rarity_prompt)
        rarity = last_rarity if rarity_input.lower() == 'r' and last_rarity else rarity_input.upper()

        cursor.execute("""
            INSERT INTO card_prints (card_id, set_code, set_number, illustrator, rarity)
            VALUES (?, ?, ?, ?, ?)
        """, (card_id, print_set_code, set_number, illustrator, rarity))
        print(f"Successfully added print from set '{print_set_code}'.")

        # Store the entered values for the next iteration
        last_illustrator = illustrator
        last_rarity = rarity


def add_new_card(cursor):
    """Interactively prompts the user to add a new card to the database."""
    print("\n--- Adding a New Conceptual Card ---")

    # --- 1. Get Conceptual Card Data ---
    title = input("Enter card title: ")
    card_type = input("Enter card type (e.g., MONSTER, UTILITY, MANA): ").upper()
    set_code = input("Enter the card's original set code (e.g., BS for Base Set): ").upper()

    # --- 2. Insert into 'cards' table to create the conceptual card ---
    cursor.execute("""
        INSERT INTO cards (title, card_type, set_code)
        VALUES (?, ?, ?)
    """, (title, card_type, set_code))

    card_id = cursor.lastrowid
    print(f"Successfully inserted conceptual card '{title}' with ID: {card_id}")

    # --- 3. Add at least one print for this card ---
    add_card_prints(cursor, card_id)

    # --- 4. Branch to get type-specific data ---
    if card_type == "MONSTER":
        if input("Add Pokedex data for this monster? (y/n): ").lower() == 'y':
            add_pokedex_data(cursor, card_id)
        add_monster_data(cursor, card_id)
    elif card_type == "UTILITY":
        add_effects(cursor, card_id)
    elif card_type == "MANA":
        add_mana_data(cursor, card_id)
        add_effects(cursor, card_id)

    return True


def main():
    """Main function to connect to the DB and run the interactive card adder."""
    if not os.path.exists(DB_PATH):
        print(f"Error: Database file not found at '{DB_PATH}'.")
        print("Please run 'create_db.py' first to create the database.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("--- Interactive Card Adder ---")
    while True:
        add_new_card(cursor)
        conn.commit()
        print("Card saved to database.")

        if input("\nAdd another card? (y/n): ").lower() != 'y':
            break

    conn.close()
    print("\nExiting Card Adder. Database connection closed.")


if __name__ == "__main__":
    main()