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
            card_type TEXT NOT NULL,
                set_code TEXT,
                illustrator TEXT
            );
    """)
    print("Table 'cards' created successfully.")

def create_monsters_table(cursor) -> None:
    """Create the 'monsters' table with a foreign key to the 'cards' table."""
    print("Creating 'monsters' table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS monsters (
            card_id INTEGER NOT NULL,
            stage TEXT,
            evolves_from TEXT,
            health INTEGER,
            mana_type TEXT,
            weakness_type TEXT,
            weakness_mod TEXT,
            resistance_type TEXT,
            resistance_mod TEXT,
            retreat_cost INTEGER,
            FOREIGN KEY (card_id) REFERENCES cards(id)
        );
    """)
    print("Table 'monsters' created successfully.")

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
            source_attack_id INTEGER,
            effect_name TEXT NOT NULL,
            target TEXT NOT NULL,
            value TEXT,
            condition TEXT,
            FOREIGN KEY (source_card_id) REFERENCES cards(id),
            FOREIGN KEY (source_attack_id) REFERENCES attacks(id)
        );
    """)
    print("Table 'effects' created successfully.")

def main():
    """Main script function."""
    # Create the data directory
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    create_cards_table(cursor)
    create_monsters_table(cursor)
    create_attacks_table(cursor)
    create_attack_costs_table(cursor)
    create_effects_table(cursor)

    conn.commit()
    conn.close()


if __name__ == "__main__":
    main()
