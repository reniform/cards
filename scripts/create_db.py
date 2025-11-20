import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "cards.db")


def create_cards_table(cursor) -> None:
    """Create the 'cards' table with a primary key."""
    print("Creating 'cards' table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            card_type TEXT NOT NULL, -- MONSTER, UTILITY, MANA
            set_code TEXT -- The original set code to identify the card archetype
        );
    """)
    print("Table 'cards' created successfully.")

def create_card_prints_table(cursor) -> None:
    """Create the 'card_prints' table to store print-specific data."""
    print("Creating 'card_prints' table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS card_prints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            card_id INTEGER NOT NULL,
            set_code TEXT NOT NULL,
            set_number TEXT, -- e.g., "58/102" or "SV001"
            illustrator TEXT,
            rarity TEXT, -- e.g., Common, Rare, Holo Rare
            FOREIGN KEY (card_id) REFERENCES cards(id)
        );
    """)
    print("Table 'card_prints' created successfully.")

def create_pokedex_entries_table(cursor) -> None:
    """Create the 'pokedex_entries' table for monster-specific lore."""
    print("Creating 'pokedex_entries' table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pokedex_entries (
            card_id INTEGER PRIMARY KEY, -- Links to conceptual card, one entry per card
            level INTEGER,
            dex_number INTEGER,
            species TEXT NOT NULL,
            height_ft_in TEXT,
            height_m REAL,
            weight_lbs REAL,
            weight_kg REAL,
            dex_entry TEXT,
            FOREIGN KEY (card_id) REFERENCES cards(id)
        );
    """)
    print("Table 'pokedex_entries' created successfully.")

def create_monsters_table(cursor) -> None:
    """Create the 'monsters' table with a foreign key to the 'cards' table."""
    print("Creating 'monsters' table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS monsters (
            card_id INTEGER NOT NULL,
            stage TEXT,
            health INTEGER,
            retreat_cost INTEGER,
            FOREIGN KEY (card_id) REFERENCES cards(id)
        );
    """)
    print("Table 'monsters' created successfully.")

def create_monster_evolutions_table(cursor) -> None:
    """Create the 'monster_evolutions' table for multiple evolution sources."""
    print("Creating 'monster_evolutions' table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS monster_evolutions (
            card_id INTEGER NOT NULL,
            evolves_from_name TEXT NOT NULL,
            FOREIGN KEY (card_id) REFERENCES cards(id)
        );
    """)
    print("Table 'monster_evolutions' created successfully.")

def create_monster_types_table(cursor) -> None:
    """Create the 'monster_types' table to handle single or dual types."""
    print("Creating 'monster_types' table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS monster_types (
            card_id INTEGER NOT NULL,
            mana_type TEXT NOT NULL,
            FOREIGN KEY (card_id) REFERENCES cards(id)
        );
    """)
    print("Table 'monster_types' created successfully.")

def create_monster_weaknesses_table(cursor) -> None:
    """Create the 'monster_weaknesses' table."""
    print("Creating 'monster_weaknesses' table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS monster_weaknesses (
            card_id INTEGER NOT NULL,
            mana_type TEXT NOT NULL,
            modifier TEXT NOT NULL,
            FOREIGN KEY (card_id) REFERENCES cards(id)
        );
    """)
    print("Table 'monster_weaknesses' created successfully.")

def create_monster_resistances_table(cursor) -> None:
    """Create the 'monster_resistances' table."""
    print("Creating 'monster_resistances' table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS monster_resistances (
            card_id INTEGER NOT NULL,
            mana_type TEXT NOT NULL,
            modifier TEXT NOT NULL,
            FOREIGN KEY (card_id) REFERENCES cards(id)
        );
    """)
    print("Table 'monster_resistances' created successfully.")

def create_monster_abilities_table(cursor) -> None:
    """Create the 'monster_abilities' table for named abilities like Pokémon Powers."""
    print("Creating 'monster_abilities' table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS monster_abilities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            card_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            type TEXT NOT NULL, -- e.g., Pokémon Power, Poké-Body
            FOREIGN KEY (card_id) REFERENCES cards(id)
        );
    """)
    print("Table 'monster_abilities' created successfully.")

def create_attacks_table(cursor) -> None:
    """Create the 'attacks' table with a primary key."""
    print("Creating 'attacks' table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attacks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            card_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            damage TEXT,
            description TEXT,
            FOREIGN KEY (card_id) REFERENCES cards(id)
        );
    """)
    print("Table 'attacks' created successfully.")

def create_attack_costs_table(cursor) -> None:
    """Create the 'attack_costs' table to store mana costs for attacks."""
    print("Creating 'attack_costs' table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attack_costs (
            attack_id INTEGER NOT NULL,
            mana_type TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            FOREIGN KEY (attack_id) REFERENCES attacks(id)
        );
    """)
    print("Table 'attack_costs' created successfully.")

def create_effects_table(cursor) -> None:
    """Create the 'effects' table for abilities and special actions."""
    print("Creating 'effects' table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS effects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_card_id INTEGER NOT NULL,
            source_attack_id INTEGER, -- Can be NULL
            source_ability_id INTEGER, -- Can be NULL
            effect_name TEXT NOT NULL,
            target TEXT NOT NULL,
            value TEXT,
            condition TEXT,
            execution_order INTEGER,
            FOREIGN KEY (source_card_id) REFERENCES cards(id),
            FOREIGN KEY (source_attack_id) REFERENCES attacks(id),
            FOREIGN KEY (source_ability_id) REFERENCES monster_abilities(id)
        );
    """)
    print("Table 'effects' created successfully.")

def main():
    """Main script function."""
    # Safeguard against accidentally overwriting an existing database.
    if os.path.exists(DB_PATH):
        print(f"Error: Database file already exists at '{DB_PATH}'.")
        print("Please delete the file manually if you wish to re-create the database from scratch.")
        return  # Exit the script

    # Create the data directory
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    create_cards_table(cursor)
    create_card_prints_table(cursor)
    create_pokedex_entries_table(cursor)
    create_monsters_table(cursor)
    create_monster_evolutions_table(cursor)
    create_monster_types_table(cursor)
    create_monster_weaknesses_table(cursor)
    create_monster_resistances_table(cursor)
    create_monster_abilities_table(cursor)
    create_attacks_table(cursor)
    create_attack_costs_table(cursor)
    create_effects_table(cursor)

    conn.commit()
    conn.close()
    print(f"\nDatabase created successfully at '{DB_PATH}'.")


if __name__ == "__main__":
    main()
