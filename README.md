# blackstar

A monster-battling card game engine written in Python. It is both a personal project and a learning experience, but I'd like for the engine to be portable and to one day support any UI possible. But it's hard. So this is my dump for the engine as I work on it.

At the moment, Blackstar only supports the terminal. No cards are preloaded for the time being. A bonafide release with support for databases would be nice. Then you could actually use it effectively.

Come back soon though :)

## Requirements
- Just Python 3.x.

## Installation

1.  **Clone the repository:**
    ```bash
    git clone <your-repository-url>
    cd blackstar
    ```

2.  **Create and activate the virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install required dependencies:**
    ```bash
    pip install colorlog colorful
    ```

## Running
Just run the `main.py script from the root of the project folder.

```bash
python src/main.py
```