import os
import tempfile

# core.database membaca SFD_DB_PATH saat di-import, jadi harus diset sebelum modul tes meng-import core
os.environ["SFD_DB_PATH"] = os.path.join(tempfile.mkdtemp(prefix="sfd-test-"), "smart_food_delivery.db")
