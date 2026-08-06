"""Build (or rebuild) the vector store from documents in ./data.

Run this once before starting the API, and again any time you add or
change files in the data/ folder.
"""

from eilaaj.pipeline import build_vector_store_for_data


def main():
    print("Building the E-Ilaaj knowledge base...")
    vector_store = build_vector_store_for_data()
    if vector_store is not None:
        print("Done. The API can now answer questions grounded in your documents.")


if __name__ == "__main__":
    main()
