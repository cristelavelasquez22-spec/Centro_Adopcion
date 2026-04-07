import config

def get_available_dogs():
    conn = config.get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, age, breed FROM Dog WHERE adopted = FALSE")
    dogs_data = cur.fetchall()
    conn.close()
    return dogs_data

def get_dog_by_id(dog_id):
    conn = config.get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, age, breed FROM Dog WHERE id = ?", (dog_id,))
    dog_data = cur.fetchone()
    conn.close()
    return dog_data

def register_adoption_transactional(dog_id, adopter_name, adopter_lastname, address, id_card):
    conn = config.get_db_connection()
    if not conn: return False
    
    cur = conn.cursor()
    try:
        conn.autocommit = False # Iniciamos transacción
        
        # 1. Registrar a la Persona (Person)
        cur.execute("INSERT INTO Person (name, lastName, id_card) VALUES (?, ?, ?)", 
                   (adopter_name, adopter_lastname, id_card))
        person_id = cur.lastrowid
        
        # 2. Registrar al Adoptante (Adopter)
        cur.execute("INSERT INTO Adopter (person_id, address) VALUES (?, ?)", 
                   (person_id, address))
        
        # 3. CREAR LA RELACIÓN (Adoption) <--- ¡Aquí está la conexión!
        cur.execute("INSERT INTO Adoption (adopter_id, dog_id) VALUES (?, ?)", 
                   (person_id, dog_id))
        
        # 4. Marcar al perro como no disponible
        cur.execute("UPDATE Dog SET adopted = TRUE WHERE id = ?", (dog_id,))
        
        conn.commit() # Si todo sale bien, guardamos
        return True
        
    except Exception as e:
        conn.rollback() # Si falla algo (ej. ID duplicado), deshacemos todo
        print(f"Error: {e}")
        return False
    finally:
        conn.close()

def get_adoption_history():
    conn = config.get_db_connection()
    cur = conn.cursor()
    # Usamos exactamente la misma consulta que te funcionó en la consola
    query = """
        SELECT 
            P.name, 
            P.lastName, 
            D.name, 
            D.breed, 
            A.adoption_date
        FROM Adoption A
        JOIN Adopter Ad ON A.adopter_id = Ad.person_id
        JOIN Person P ON Ad.person_id = P.id
        JOIN Dog D ON A.dog_id = D.id
    """
    cur.execute(query)
    history = cur.fetchall()
    conn.close()
    return history