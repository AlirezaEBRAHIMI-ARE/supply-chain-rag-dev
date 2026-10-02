import sqlite3

# Name of the database file. SQLite stores the whole database as one file on disk.
# You can call this variable anything; "DB_NAME" is just a clear, conventional name.
DB_NAME = "tracking.db"


def init_db():
    """Create the shipments table if it doesn't already exist."""
    conn = sqlite3.connect(DB_NAME)   # opens the file (creates it if missing)
    cursor = conn.cursor()            # the object you use to run SQL commands

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS shipments (
            id TEXT PRIMARY KEY,
            status TEXT NOT NULL,
            origin TEXT NOT NULL,
            destination TEXT NOT NULL,
            last_updated TEXT NOT NULL
        )
    """)

    conn.commit()  # writes the change to disk — without this, nothing is saved
    conn.close()   # releases the file so other code/processes can use it


def insert_shipment(shipment_id, origin, destination):
    """Create a new shipment, starting at status 'pending'."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO shipments (id, status, origin, destination, last_updated)
        VALUES (?, ?, ?, ?, datetime('now'))
        """,
        (shipment_id, "pending", origin, destination),
        # The ?-placeholders are filled in from this tuple, in order.
        # Never paste values directly into the SQL string (f-string etc.) —
        # that's how SQL injection bugs happen. Placeholders are the safe way.
    )

    conn.commit()
    conn.close()


def update_status(shipment_id, new_status):
    """Move a shipment to a new status (pending -> in_transit -> customs -> delivered)."""
    allowed = ["pending", "in_transit", "customs", "delivered"]
    if new_status not in allowed:
        raise ValueError(f"Invalid status '{new_status}'. Must be one of {allowed}.")

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE shipments
        SET status = ?, last_updated = datetime('now')
        WHERE id = ?
        """,
        (new_status, shipment_id),
    )

    conn.commit()
    rows_changed = cursor.rowcount  # how many rows the UPDATE actually touched
    conn.close()

    if rows_changed == 0:
        raise ValueError(f"No shipment found with id '{shipment_id}'.")


def get_shipment(shipment_id):
    """Look up one shipment by id. Returns a dict, or None if not found."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, status, origin, destination, last_updated FROM shipments WHERE id = ?",
        (shipment_id,),
    )
    row = cursor.fetchone()  # one row (a tuple) or None
    conn.close()

    if row is None:
        return None

    return {
        "id": row[0],
        "status": row[1],
        "origin": row[2],
        "destination": row[3],
        "last_updated": row[4],
    }


if __name__ == "__main__":
    # This block only runs when you execute `python tracking.py` directly —
    # it does NOT run when another file does `import tracking`.
    # It's a quick self-test so you can confirm the module works on its own.
    init_db()
    insert_shipment("SHIP123", "Paris", "Berlin")
    print("After insert:", get_shipment("SHIP123"))

    update_status("SHIP123", "in_transit")
    print("After update:", get_shipment("SHIP123"))
