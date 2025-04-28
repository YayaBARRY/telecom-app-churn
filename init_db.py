from app import Base, engine

if __name__ == "__main__":
    print("⏳ Création des tables dans la base de données...")
    Base.metadata.create_all(engine)
    print("✅ Tables créées avec succès !")